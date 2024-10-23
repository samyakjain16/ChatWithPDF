# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.routes import pdf
from pathlib import Path

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads directory
uploads_path = Path("data/uploads")
uploads_path.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory="data/uploads"), name="uploads")

# Include routes
app.include_router(pdf.router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"message": "PDF Chat API is running"}
