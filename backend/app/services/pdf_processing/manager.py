# backend/app/services/pdf_processing/manager.py
from typing import List, Dict, Any
import logging
from .extractor import PDFExtractor
from .chunker import PDFChunker
from .embedder import create_embedding_generator
from app.services.vector_store.qdrant import QdrantStore

logger = logging.getLogger(__name__)


class ProcessingManager:
    def __init__(self):
        self.extractor = PDFExtractor()
        self.chunker = PDFChunker()
        self.embedder = create_embedding_generator()
        self.vector_store = QdrantStore()

    async def process_pdf(self, pdf_key: str) -> Dict[str, Any]:
        """Process PDF through the entire pipeline"""
        try:
            # Extract text
            logger.info(f"Starting extraction for {pdf_key}")
            extracted_elements = await self.extractor.extract_text(pdf_key)

            # Create chunks
            logger.info("Creating chunks")
            chunks = self.chunker.create_chunks(extracted_elements)

            # Generate embeddings
            logger.info("Generating embeddings")
            embedded_chunks = await self.embedder.generate_embeddings(chunks)

            # Store in vector database
            logger.info("Storing embeddings")
            await self.vector_store.store_embeddings(embedded_chunks, pdf_key)

            return {
                "status": "success",
                "pdf_key": pdf_key,
                "num_chunks": len(chunks),
                "num_embeddings": len(embedded_chunks)
            }

        except Exception as e:
            logger.error(f"Error processing PDF {pdf_key}: {str(e)}")
            raise
