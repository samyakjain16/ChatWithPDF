# backend/app/services/pdf_processing/chunker.py
from typing import List, Dict, Any
import re
from dataclasses import dataclass
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    """Represents a processed text chunk with metadata"""
    text: str
    metadata: Dict[str, Any]
    chunk_id: str
    start_page: int
    end_page: int
    chunk_type: str


class PDFChunker:
    def __init__(self,
                 chunk_size: int = 512,
                 chunk_overlap: int = 50,
                 min_chunk_size: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size

    def create_chunks(self, extracted_elements: List[Dict[str, Any]]) -> List[Chunk]:
        """Main chunking method that preserves document structure"""
        try:
            chunks = []
            current_chunk = []
            current_chunk_size = 0
            current_metadata = {
                "start_page": None,
                "document_sections": set()
            }

            for element in extracted_elements:
                text = element['text']
                element_type = element['metadata']['type']
                page_number = element['metadata']['page_number']

                # Update metadata
                if current_metadata["start_page"] is None:
                    current_metadata["start_page"] = page_number

                # Handle different element types
                if element_type == "heading":
                    # Create new chunk at headings
                    if current_chunk:
                        chunks.append(self._create_chunk_object(
                            current_chunk,
                            current_metadata,
                            page_number
                        ))
                        current_chunk = []
                        current_chunk_size = 0

                # Add text to current chunk
                tokens = self._estimate_tokens(text)

                if current_chunk_size + tokens > self.chunk_size:
                    # Create semantic split point
                    split_point = self._find_semantic_split(text)
                    if split_point:
                        current_chunk.append(text[:split_point])
                        chunks.append(self._create_chunk_object(
                            current_chunk,
                            current_metadata,
                            page_number
                        ))
                        # Start new chunk with overlap
                        current_chunk = [text[split_point-self.chunk_overlap:]]
                        current_chunk_size = self._estimate_tokens(
                            current_chunk[0])
                    else:
                        current_chunk.append(text)
                        chunks.append(self._create_chunk_object(
                            current_chunk,
                            current_metadata,
                            page_number
                        ))
                        current_chunk = []
                        current_chunk_size = 0
                else:
                    current_chunk.append(text)
                    current_chunk_size += tokens

                current_metadata["document_sections"].add(element_type)

            # Handle remaining text
            if current_chunk:
                chunks.append(self._create_chunk_object(
                    current_chunk,
                    current_metadata,
                    page_number
                ))

            return self._post_process_chunks(chunks)

        except Exception as e:
            logger.error(f"Error in chunking process: {str(e)}")
            raise

    def _estimate_tokens(self, text: str) -> int:
        """Estimate number of tokens in text"""
        # Rough estimation: 1 token ≈ 4 characters
        return len(text) // 4

    def _find_semantic_split(self, text: str) -> int:
        """Find the best point to split text while maintaining context"""
        # Priority for split points: sentence end > paragraph > phrase
        split_points = {
            r'[.!?]\s': 10,  # Sentence endings
            r'\n\s*\n': 8,   # Paragraphs
            r'[,;:]\s': 6,   # Phrases
            r'\s': 2         # Words (last resort)
        }

        for pattern, priority in split_points.items():
            matches = list(re.finditer(pattern, text))
            if matches:
                # Find the split point closest to chunk_size
                target_position = self.chunk_size * 4  # Convert to characters
                best_split = min(matches, key=lambda x: abs(
                    x.end() - target_position))
                return best_split.end()

        return None

    def _create_chunk_object(self,
                             texts: List[str],
                             metadata: Dict[str, Any],
                             end_page: int) -> Chunk:
        """Create a chunk object with metadata"""
        from uuid import uuid4

        return Chunk(
            text=" ".join(texts),
            metadata={
                "start_page": metadata["start_page"],
                "end_page": end_page,
                "document_sections": list(metadata["document_sections"]),
                "original_length": sum(len(t) for t in texts)
            },
            chunk_id=str(uuid4()),
            start_page=metadata["start_page"],
            end_page=end_page,
            chunk_type="text"
        )

    def _post_process_chunks(self, chunks: List[Chunk]) -> List[Chunk]:
        """Post-process chunks to ensure quality"""
        processed_chunks = []

        for chunk in chunks:
            # Skip chunks that are too small
            if len(chunk.text) < self.min_chunk_size:
                continue

            # Clean up text
            chunk.text = self._clean_text(chunk.text)
            processed_chunks.append(chunk)

        return processed_chunks

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        # Remove multiple newlines
        text = re.sub(r'\n+', '\n', text)
        # Trim whitespace
        return text.strip()
