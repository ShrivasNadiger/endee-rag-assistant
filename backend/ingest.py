"""
Document Ingestion Pipeline
Handles document loading, chunking, embedding, and storage in Endee
"""

from typing import List, Dict, Any
import os
from openai import OpenAI
from utils.pdf_loader import load_pdf
from utils.docx_loader import load_docx
from utils.chunker import chunk_documents
from endee_client import EndeeClient


class IngestionPipeline:
    """Pipeline for ingesting documents into Endee vector database"""
    
    def __init__(
        self,
        openai_api_key: str,
        endee_client: EndeeClient,
        index_name: str,
        embedding_model: str = "text-embedding-3-small",
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ):
        """
        Initialize ingestion pipeline
        
        Args:
            openai_api_key: OpenAI API key
            endee_client: Initialized Endee REST API client
            index_name: Name of Endee index to use
            embedding_model: OpenAI embedding model name
            chunk_size: Maximum characters per chunk
            chunk_overlap: Overlapping characters between chunks
        """
        self.openai_client = OpenAI()
        self.endee_client = endee_client
        self.index_name = index_name
        self.embedding_model = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def load_document(self, file_content: bytes, filename: str) -> List[Dict[str, Any]]:
        """
        Load document based on file extension
        
        Args:
            file_content: File content as bytes
            filename: Original filename
        
        Returns:
            List of document sections with metadata
        """
        file_ext = filename.lower().split('.')[-1]
        
        if file_ext == 'pdf':
            return load_pdf(file_content, filename)
        elif file_ext in ['docx', 'doc']:
            return load_docx(file_content, filename)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using OpenAI
        
        Args:
            texts: List of text strings to embed
        
        Returns:
            List of embedding vectors
        """
        print(f"→ Generating embeddings for {len(texts)} chunks using {self.embedding_model}...")
        
        # OpenAI API call for embeddings
        response = self.openai_client.embeddings.create(
            model=self.embedding_model,
            input=texts
        )
        
        embeddings = [item.embedding for item in response.data]
        print(f"✓ Generated {len(embeddings)} embeddings")
        
        return embeddings
    
    def ingest_documents(
        self,
        files: List[tuple]  # List of (file_content: bytes, filename: str)
    ) -> Dict[str, Any]:
        """
        Complete ingestion pipeline: load, chunk, embed, and store
        
        Args:
            files: List of tuples (file_content, filename)
        
        Returns:
            Ingestion statistics
        """
        print(f"\n{'='*60}")
        print(f"STARTING DOCUMENT INGESTION")
        print(f"{'='*60}\n")
        
        all_documents = []
        
        # Step 1: Load all documents
        print("STEP 1: Loading documents...")
        for file_content, filename in files:
            try:
                docs = self.load_document(file_content, filename)
                all_documents.extend(docs)
            except Exception as e:
                print(f"✗ Failed to load {filename}: {str(e)}")
                continue
        
        if not all_documents:
            return {
                "success": False,
                "error": "No documents were successfully loaded",
                "chunks_created": 0,
                "vectors_stored": 0
            }
        
        print(f"\n✓ Loaded {len(all_documents)} document sections from {len(files)} files\n")
        
        # Step 2: Chunk documents
        print("STEP 2: Chunking documents...")
        chunks = chunk_documents(
            all_documents,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        
        if not chunks:
            return {
                "success": False,
                "error": "No chunks were created",
                "chunks_created": 0,
                "vectors_stored": 0
            }
        
        print(f"✓ Created {len(chunks)} chunks\n")
        
        # Step 3: Generate embeddings
        print("STEP 3: Generating embeddings...")
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.generate_embeddings(texts)
        print()
        
        # Step 4: Prepare vectors for Endee REST API
        print("STEP 4: Preparing vectors for Endee...")
        vectors = []
        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            # Create unique ID
            chunk_id = f"{chunk.get('document_name', 'unknown')}_{idx}"
            
            # Prepare metadata (combines display and filter data)
            metadata = {
                "document_name": chunk.get("document_name", ""),
                "text": chunk.get("text", ""),  # Store full text for retrieval
                "chunk_index": chunk.get("chunk_index", 0)
            }
            
            # Add page number or paragraph index to metadata
            if "page_number" in chunk:
                metadata["page_number"] = chunk["page_number"]
            if "paragraph_index" in chunk:
                metadata["paragraph_index"] = chunk["paragraph_index"]
            
            # Format for Endee REST API
            vectors.append({
                "id": chunk_id,
                "vector": embedding,
                "metadata": metadata
            })
        
        print(f"✓ Prepared {len(vectors)} vectors\n")
        
        # Step 5: Store in Endee via REST API
        print("STEP 5: Storing vectors in Endee via REST API...")
        upsert_result = self.endee_client.insert_documents(
            index_name=self.index_name,
            vectors=vectors
        )
        
        print(f"\n{'='*60}")
        print(f"INGESTION COMPLETE")
        print(f"{'='*60}")
        print(f"Files processed: {len(files)}")
        print(f"Chunks created: {len(chunks)}")
        print(f"Vectors stored: {upsert_result['count']}")
        print(f"Upsert time: {upsert_result['elapsed_ms']} ms")
        print(f"{'='*60}\n")
        
        return {
            "success": True,
            "files_processed": len(files),
            "chunks_created": len(chunks),
            "vectors_stored": upsert_result["count"],
            "upsert_time_ms": upsert_result["elapsed_ms"]
        }
