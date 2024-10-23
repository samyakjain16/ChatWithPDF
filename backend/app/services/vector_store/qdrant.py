# backend/app/services/vector_store/qdrant.py
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    Match
)
from typing import List, Dict, Any, Optional
from app.services.pdf_processing.embedder import EmbeddedChunk
import numpy as np
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class QdrantStore:
    def __init__(self):
        """Initialize Qdrant client"""
        try:
            self.client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY,
            )
            self.collection_name = settings.QDRANT_COLLECTION
            self._ensure_collection()
            logger.info(f"Connected to Qdrant at {settings.QDRANT_URL}")
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant: {str(e)}")
            raise

    def _ensure_collection(self):
        """Ensure collection exists with correct settings"""
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=settings.EMBEDDING_DIMENSION,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to ensure collection: {str(e)}")
            raise

    async def store_embeddings(
        self,
        embedded_chunks: List[EmbeddedChunk],
        pdf_key: str
    ) -> bool:
        """Store embeddings in Qdrant"""
        try:
            points = []
            for chunk in embedded_chunks:
                point = PointStruct(
                    id=chunk.chunk_id,
                    vector=chunk.embedding.tolist(),
                    payload={
                        "text": chunk.text,
                        "pdf_key": pdf_key,
                        "metadata": chunk.metadata
                    }
                )
                points.append(point)

            # Store in batches
            batch_size = 100
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch
                )

            logger.info(f"Stored {len(points)} embeddings for PDF {pdf_key}")
            return True

        except Exception as e:
            logger.error(f"Failed to store embeddings: {str(e)}")
            raise

    async def search(
        self,
        query_vector: np.ndarray,
        pdf_key: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar chunks"""
        try:
            search_filter = None
            if pdf_key:
                search_filter = Filter(
                    must=[
                        FieldCondition(
                            key="pdf_key",
                            match=Match(value=pdf_key)
                        )
                    ]
                )

            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector.tolist(),
                limit=limit,
                query_filter=search_filter
            )

            results = []
            for result in search_results:
                results.append({
                    "chunk_id": result.id,
                    "text": result.payload["text"],
                    "pdf_key": result.payload["pdf_key"],
                    "metadata": result.payload["metadata"],
                    "score": result.score
                })

            return results

        except Exception as e:
            logger.error(f"Failed to search vectors: {str(e)}")
            raise

    async def delete_pdf(self, pdf_key: str) -> bool:
        """Delete all chunks for a specific PDF"""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="pdf_key",
                            match=Match(value=pdf_key)
                        )
                    ]
                )
            )
            logger.info(f"Deleted all chunks for PDF {pdf_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete PDF chunks: {str(e)}")
            raise
