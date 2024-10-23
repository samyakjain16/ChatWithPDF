# backend/app/services/pdf_processing/extractor.py
from unstructured.partition.pdf import partition_pdf
from pathlib import Path
import tempfile
import boto3
from botocore.exceptions import ClientError
from typing import List, Dict
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class PDFExtractor:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SECRET_KEY,
            region_name=settings.AWS_REGION
        )

    async def download_from_s3(self, key: str) -> Path:
        """Download PDF from S3 to temporary file"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                self.s3.download_fileobj(
                    settings.AWS_BUCKET_NAME, key, tmp_file)
                return Path(tmp_file.name)
        except ClientError as e:
            logger.error(f"Error downloading file from S3: {str(e)}")
            raise

    async def extract_text(self, pdf_key: str) -> List[Dict[str, str]]:
        """Extract text from PDF with metadata"""
        try:
            # Download PDF from S3
            pdf_path = await self.download_from_s3(pdf_key)

            # Extract text with metadata
            elements = partition_pdf(
                filename=str(pdf_path),
                strategy="fast",
                extract_images_in_pdf=False,
                infer_table_structure=True,
                include_metadata=True
            )

            # Clean up temporary file
            pdf_path.unlink()

            # Process and structure the extracted elements
            processed_elements = []
            for element in elements:
                processed_elements.append({
                    'text': str(element),
                    'metadata': {
                        'type': element.type if hasattr(element, 'type') else 'text',
                        'page_number': element.metadata.page_number if hasattr(element, 'metadata') else None,
                        'coordinates': element.metadata.coordinates if hasattr(element, 'metadata') else None
                    }
                })

            return processed_elements

        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise
