"""
Vector Retrieval Module
Handles query embedding and vector search in Endee
"""

from typing import List, Dict, Any
from openai import OpenAI
from endee_client import EndeeClient


class Retriever:
    """Retrieves relevant chunks from Endee using vector similarity"""
    
    def __init__(
        self,
        openai_api_key: str,
        endee_client: EndeeClient,
        index_name: str,
        embedding_model: str = "text-embedding-3-small"
    ):
        """
        Initialize retriever
        
        Args:
            openai_api_key: OpenAI API key
            endee_client: Initialized Endee REST API client
            index_name: Name of Endee index to query
            embedding_model: OpenAI embedding model (must match ingestion model)
        """
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.endee_client = endee_client
        self.index_name = index_name
        self.embedding_model = embedding_model
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for query text
        
        Args:
            query: User query string
        
        Returns:
            Query embedding vector
        """
        response = self.openai_client.embeddings.create(
            model=self.embedding_model,
            input=[query]
        )
        
        return response.data[0].embedding
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Retrieve relevant chunks for a query
        
        Args:
            query: User query string
            top_k: Number of chunks to retrieve
        
        Returns:
            Dict with retrieved chunks and latency:
            {
                "chunks": List[Dict],
                "retrieval_latency_ms": float,
                "query": str
            }
        """
        print(f"\n→ Retrieving top {top_k} chunks for query: '{query}'")
        
        # Generate query embedding
        query_embedding = self.generate_query_embedding(query)
        
        # Query Endee via REST API (latency is tracked inside endee_client)
        result = self.endee_client.search(
            index_name=self.index_name,
            query_vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        # Extract and format chunks from REST API response
        chunks = []
        for item in result["results"]:
            metadata = item.get("metadata", {})
            chunk = {
                "id": item.get("id", ""),
                "similarity": item.get("score", 0.0),  # REST API returns 'score'
                "text": metadata.get("text", ""),
                "document_name": metadata.get("document_name", ""),
                "page_number": metadata.get("page_number"),
                "paragraph_index": metadata.get("paragraph_index"),
                "chunk_index": metadata.get("chunk_index", 0)
            }
            chunks.append(chunk)
        
        print(f"✓ Retrieved {len(chunks)} chunks (latency: {result['retrieval_latency_ms']} ms)")
        
        return {
            "chunks": chunks,
            "retrieval_latency_ms": result["retrieval_latency_ms"],
            "query": query
        }
