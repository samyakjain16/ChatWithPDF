from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # API configs
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "PDF Chat API"

    # AWS Credentials
    AWS_ACCESS_KEY: str
    AWS_SECRET_KEY: str
    AWS_BUCKET_NAME: str
    AWS_REGION: str

    # Model configs
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str
    QDRANT_COLLECTION: str = "pdf_chunks"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
