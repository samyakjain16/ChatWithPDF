# backend/app/services/pdf_processing/embedder.py
from typing import List, Dict, Any, Union
from sentence_transformers import SentenceTransformer
import numpy as np
from app.core.config import settings
import torch
import logging
from dataclasses import dataclass
from .chunker import Chunk

logger = logging.getLogger(__name__)


@dataclass
class EmbeddedChunk:
    """Represents a chunk with its embedding"""
    chunk_id: str
    text: str
    embedding: np.ndarray
    metadata: Dict[str, Any]


class EmbeddingGenerator:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the embedding generator"""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        try:
            self.model = SentenceTransformer(model_name, device=self.device)
            self.dimension = self.model.get_sentence_embedding_dimension()
            logger.info(f"Loaded embedding model {
                        model_name} on {self.device}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {str(e)}")
            raise

    async def generate_embeddings(self, chunks: List[Chunk], batch_size: int = 32) -> List[EmbeddedChunk]:
        """Generate embeddings for chunks in batches"""
        try:
            embedded_chunks = []

            # Process chunks in batches
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                texts = [chunk.text for chunk in batch]

                # Generate embeddings for batch
                embeddings = self.model.encode(
                    texts,
                    show_progress_bar=False,
                    convert_to_numpy=True,
                    normalize_embeddings=True  # L2 normalization
                )

                # Create EmbeddedChunk objects
                for chunk, embedding in zip(batch, embeddings):
                    embedded_chunks.append(
                        EmbeddedChunk(
                            chunk_id=chunk.chunk_id,
                            text=chunk.text,
                            embedding=embedding,
                            metadata={
                                **chunk.metadata,
                                "embedding_model": self.model.get_model_name(),
                                "embedding_dimension": self.dimension
                            }
                        )
                    )

            return embedded_chunks

        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise

    async def generate_query_embedding(self, query: str) -> np.ndarray:
        """Generate embedding for a search query"""
        try:
            return self.model.encode(
                query,
                convert_to_numpy=True,
                normalize_embeddings=True
            )
        except Exception as e:
            logger.error(f"Error generating query embedding: {str(e)}")
            raise


class OpenAIEmbeddingGenerator:
    """OpenAI embedding generator for production use"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.dimension = 1536  # OpenAI ada-002 dimension

    async def generate_embeddings(self, chunks: List[Chunk], batch_size: int = 32) -> List[EmbeddedChunk]:
        """Generate embeddings using OpenAI API"""
        try:
            import openai
            openai.api_key = self.api_key

            embedded_chunks = []

            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                texts = [chunk.text for chunk in batch]

                response = await openai.Embedding.acreate(
                    input=texts,
                    model="text-embedding-ada-002"
                )

                embeddings = [item['embedding'] for item in response['data']]

                for chunk, embedding in zip(batch, embeddings):
                    embedded_chunks.append(
                        EmbeddedChunk(
                            chunk_id=chunk.chunk_id,
                            text=chunk.text,
                            embedding=np.array(embedding),
                            metadata={
                                **chunk.metadata,
                                "embedding_model": "text-embedding-ada-002",
                                "embedding_dimension": self.dimension
                            }
                        )
                    )

            return embedded_chunks

        except Exception as e:
            logger.error(f"Error generating OpenAI embeddings: {str(e)}")
            raise

# Factory for creating embedding generator based on settings


def create_embedding_generator() -> Union[EmbeddingGenerator, OpenAIEmbeddingGenerator]:
    """Create appropriate embedding generator based on settings"""
    if settings.USE_OPENAI_EMBEDDINGS:
        return OpenAIEmbeddingGenerator(settings.OPENAI_API_KEY)
    return EmbeddingGenerator(settings.EMBEDDING_MODEL)
