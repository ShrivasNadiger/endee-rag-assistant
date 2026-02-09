"""
Endee Vector Database REST API Client
Handles all HTTP interactions with Endee standalone service
"""

import time
import requests
from typing import List, Dict, Any, Optional


class EndeeClient:
    """Client for interacting with Endee vector database via REST API"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        """
        Initialize Endee REST API client
        
        Args:
            base_url: Endee server URL (default: http://localhost:8080)
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
        
    def create_index(
        self,
        index_name: str,
        dimension: int,
        metric: str = "cosine"
    ) -> Dict[str, Any]:
        """
        Create a new vector index in Endee
        
        Args:
            index_name: Name of the index
            dimension: Vector dimension (must match embedding size)
            metric: Distance metric (cosine, euclidean, or dot)
        
        Returns:
            Response from Endee API
        """
        url = f"{self.base_url}/indexes"
        payload = {
            "name": index_name,
            "dimension": dimension,
            "metric": metric
        }
        
        try:
            response = self.session.post(url, json=payload)
            
            # Index might already exist (409 conflict)
            if response.status_code == 409:
                print(f"✓ Index '{index_name}' already exists")
                return {"status": "exists", "index_name": index_name}
            
            response.raise_for_status()
            print(f"✓ Created index '{index_name}' (dimension={dimension}, metric={metric})")
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error creating index: {str(e)}")
            raise
    
    def insert_documents(
        self,
        index_name: str,
        vectors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Insert/upsert vectors into Endee index
        
        Args:
            index_name: Target index name
            vectors: List of vector objects with structure:
                {
                    "id": str,
                    "vector": List[float],
                    "metadata": Dict (optional)
                }
        
        Returns:
            Dict with insertion statistics and latency
        """
        url = f"{self.base_url}/indexes/{index_name}/vectors"
        
        start_time = time.time()
        
        try:
            response = self.session.post(url, json={"vectors": vectors})
            response.raise_for_status()
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            result = response.json()
            result['elapsed_ms'] = round(elapsed_ms, 2)
            
            print(f"✓ Inserted {len(vectors)} vectors into '{index_name}' ({elapsed_ms:.2f}ms)")
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error inserting vectors: {str(e)}")
            raise
    
    def search(
        self,
        index_name: str,
        query_vector: List[float],
        top_k: int = 5,
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """
        Perform vector similarity search in Endee
        
        Args:
            index_name: Index to search
            query_vector: Query embedding vector
            top_k: Number of results to return
            include_metadata: Whether to include metadata in results
        
        Returns:
            Dict with search results and retrieval latency:
            {
                "results": List[Dict],
                "retrieval_latency_ms": float
            }
        """
        url = f"{self.base_url}/indexes/{index_name}/search"
        payload = {
            "vector": query_vector,
            "top_k": top_k,
            "include_metadata": include_metadata
        }
        
        # Measure retrieval latency (critical performance metric)
        start_time = time.time()
        
        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            
            # Calculate Endee retrieval latency
            retrieval_latency_ms = (time.time() - start_time) * 1000
            
            result = response.json()
            
            return {
                "results": result.get("results", []),
                "retrieval_latency_ms": round(retrieval_latency_ms, 2)
            }
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error searching vectors: {str(e)}")
            raise
    
    def delete_index(self, index_name: str) -> Dict[str, Any]:
        """
        Delete an index from Endee
        
        Args:
            index_name: Name of index to delete
        
        Returns:
            Response from Endee API
        """
        url = f"{self.base_url}/indexes/{index_name}"
        
        try:
            response = self.session.delete(url)
            response.raise_for_status()
            print(f"✓ Deleted index '{index_name}'")
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error deleting index: {str(e)}")
            raise
    
    def get_index_info(self, index_name: str) -> Dict[str, Any]:
        """
        Get information about an index
        
        Args:
            index_name: Name of index
        
        Returns:
            Index information
        """
        url = f"{self.base_url}/indexes/{index_name}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error getting index info: {str(e)}")
            raise
    
    def health_check(self) -> bool:
        """
        Check if Endee service is healthy
        
        Returns:
            True if service is healthy, False otherwise
        """
        url = f"{self.base_url}/health"
        
        try:
            response = self.session.get(url, timeout=5)
            return response.status_code == 200
        except:
            return False
