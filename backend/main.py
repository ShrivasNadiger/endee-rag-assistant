"""
FastAPI Main Application
RAG system with Endee vector database
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

from endee_client import EndeeClient
from ingest import IngestionPipeline
from retriever import Retriever
from rag_pipeline import RAGPipeline

# Load environment variables
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ENDEE_BASE_URL = os.getenv("ENDEE_BASE_URL", "http://localhost:8080")
ENDEE_INDEX_NAME = os.getenv("ENDEE_INDEX_NAME", "rag_documents")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1536"))
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4-turbo-preview")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))

# Validate configuration
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Initialize FastAPI app
app = FastAPI(
    title="RAG Application with Endee",
    description="Retrieval Augmented Generation using Endee vector database via REST API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Endee REST API client
endee_client = EndeeClient(base_url=ENDEE_BASE_URL)

# Initialize pipelines
ingestion_pipeline = IngestionPipeline(
    openai_api_key=OPENAI_API_KEY,
    endee_client=endee_client,
    index_name=ENDEE_INDEX_NAME,
    embedding_model=EMBEDDING_MODEL,
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP
)

retriever = Retriever(
    openai_api_key=OPENAI_API_KEY,
    endee_client=endee_client,
    index_name=ENDEE_INDEX_NAME,
    embedding_model=EMBEDDING_MODEL
)

rag_pipeline = RAGPipeline(
    openai_api_key=OPENAI_API_KEY,
    retriever=retriever,
    llm_model=LLM_MODEL
)


# Pydantic models
class QueryRequest(BaseModel):
    query: str
    top_k: int = 5


class QueryResponse(BaseModel):
    answer: str
    chunks: List[Dict[str, Any]]
    retrieval_latency_ms: float
    generation_latency_ms: float
    total_latency_ms: float


class IngestResponse(BaseModel):
    success: bool
    message: str
    files_processed: int
    chunks_created: int
    vectors_stored: int
    upsert_time_ms: float


# API Endpoints

@app.on_event("startup")
async def startup_event():
    """Initialize Endee index on startup via REST API"""
    print("\n" + "="*60)
    print("INITIALIZING RAG APPLICATION")
    print("="*60)
    print(f"Endee URL: {ENDEE_BASE_URL}")
    print(f"Index Name: {ENDEE_INDEX_NAME}")
    print(f"Embedding Model: {EMBEDDING_MODEL}")
    print(f"LLM Model: {LLM_MODEL}")
    print("="*60 + "\n")
    
    # Check Endee health
    if not endee_client.health_check():
        print("⚠ WARNING: Cannot connect to Endee at", ENDEE_BASE_URL)
        print("Please ensure Endee is running (docker-compose up -d)")
    else:
        print("✓ Endee service is healthy")
    
    # Create or connect to Endee index via REST API
    try:
        endee_client.create_index(
            index_name=ENDEE_INDEX_NAME,
            dimension=EMBEDDING_DIMENSION,
            metric="cosine"
        )
    except Exception as e:
        print(f"⚠ Warning: Could not create index: {str(e)}")
        print("Index may already exist or Endee may not be running")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "RAG Application with Endee",
        "endee_url": ENDEE_BASE_URL,
        "index_name": ENDEE_INDEX_NAME
    }


@app.post("/ingest", response_model=IngestResponse)
async def ingest_documents(files: List[UploadFile] = File(...)):
    """
    Ingest documents into Endee vector database
    
    Accepts multiple PDF and DOCX files, chunks them, generates embeddings,
    and stores vectors in Endee with metadata.
    
    Args:
        files: List of uploaded files (.pdf or .docx)
    
    Returns:
        Ingestion statistics including chunks created and latency
    """
    # Validate file types
    allowed_extensions = {".pdf", ".docx", ".doc"}
    file_data = []
    
    for file in files:
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_ext} not supported. Only PDF and DOCX files are allowed."
            )
        
        # Read file content
        content = await file.read()
        file_data.append((content, file.filename))
    
    if not file_data:
        raise HTTPException(
            status_code=400,
            detail="No valid files provided"
        )
    
    try:
        # Run ingestion pipeline
        result = ingestion_pipeline.ingest_documents(file_data)
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Ingestion failed")
            )
        
        return IngestResponse(
            success=True,
            message=f"Successfully ingested {result['files_processed']} files",
            files_processed=result["files_processed"],
            chunks_created=result["chunks_created"],
            vectors_stored=result["vectors_stored"],
            upsert_time_ms=result["upsert_time_ms"]
        )
        
    except Exception as e:
        print(f"✗ Ingestion error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ingestion failed: {str(e)}"
        )


@app.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """
    Query the RAG system
    
    Retrieves relevant chunks from Endee using vector similarity,
    generates an answer using OpenAI, and returns citations.
    
    Args:
        request: Query request with query text and optional top_k
    
    Returns:
        Answer with inline citations, retrieved chunks, and latency metrics
    """
    if not request.query or not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty"
        )
    
    try:
        # Run RAG pipeline
        result = rag_pipeline.generate_answer(
            query=request.query,
            top_k=request.top_k
        )
        
        return QueryResponse(
            answer=result["answer"],
            chunks=result["chunks"],
            retrieval_latency_ms=result["retrieval_latency_ms"],
            generation_latency_ms=result["generation_latency_ms"],
            total_latency_ms=result["total_latency_ms"]
        )
        
    except Exception as e:
        print(f"✗ Query error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Query failed: {str(e)}"
        )


@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    return {
        "endee": endee_client.get_stats(),
        "config": {
            "embedding_model": EMBEDDING_MODEL,
            "llm_model": LLM_MODEL,
            "chunk_size": CHUNK_SIZE,
            "chunk_overlap": CHUNK_OVERLAP
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
