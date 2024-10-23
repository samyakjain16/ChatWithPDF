from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import uuid
from datetime import datetime
from pydantic import BaseModel
from app.services.s3 import S3Service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize S3 Service
s3_service = S3Service()


class PDF(BaseModel):
    id: str
    filename: str
    uploadedAt: str
    url: str


@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    try:
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        print("Filename:", file.filename)
        # Upload to S3
        url = await s3_service.upload_file(file.file, unique_filename)

        return {
            "filename": file.filename,
            "id": str(uuid.uuid4()),
            "url": url,
            "status": "uploaded"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error during upload: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload file")


@router.get("/pdfs", response_model=List[PDF])
async def get_pdfs():
    try:
        files = await s3_service.list_files()
        return [
            PDF(
                id=str(uuid.uuid4()),
                filename=file['key'].split('_', 1)[1],  # Remove UUID prefix
                uploadedAt=file['last_modified'].isoformat(),
                url=file['url']
            )
            for file in files
        ]
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error listing PDFs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list PDFs")
