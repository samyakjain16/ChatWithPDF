# backend/app/api/routes/search.py
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from app.services.vector_store.qdrant import QdrantStore
from app.services.pdf_processing.embedder import create_embedding_generator

router = APIRouter()


class SearchQuery(BaseModel):
    query: str
    pdf_key: Optional[str] = None
    limit: int = 5


class SearchResult(BaseModel):
    chunk_id: str
    text: str
    pdf_key: str
    metadata: dict
    score: float


@router.post("/search", response_model=List[SearchResult])
async def search_pdfs(query: SearchQuery):
    try:
        # Generate embedding for query
        embedder = create_embedding_generator()
        query_embedding = await embedder.generate_query_embedding(query.query)

        # Search in vector store
        vector_store = QdrantStore()
        results = await vector_store.search(
            query_vector=query_embedding,
            pdf_key=query.pdf_key,
            limit=query.limit
        )

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
