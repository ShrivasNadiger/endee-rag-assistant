"""
RAG Pipeline
Combines retrieval and generation with citation support
"""

import re
from typing import List, Dict, Any
from openai import OpenAI
from retriever import Retriever


class RAGPipeline:
    """RAG pipeline for generating answers with citations"""
    
    def __init__(
        self,
        openai_api_key: str,
        retriever: Retriever,
        llm_model: str = "gpt-4-turbo-preview"
    ):
        """
        Initialize RAG pipeline
        
        Args:
            openai_api_key: OpenAI API key
            retriever: Initialized retriever
            llm_model: OpenAI chat model for generation
        """
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.retriever = retriever
        self.llm_model = llm_model
    
    def format_citation(self, chunk: Dict[str, Any]) -> str:
        """
        Format citation for a chunk
        
        Args:
            chunk: Chunk metadata
        
        Returns:
            Citation string in format: [source_name – page/section]
        """
        doc_name = chunk.get("document_name", "Unknown")
        
        # Use page number if available (PDF), otherwise paragraph index (DOCX)
        if chunk.get("page_number"):
            location = f"page {chunk['page_number']}"
        elif chunk.get("paragraph_index"):
            location = f"para {chunk['paragraph_index']}"
        else:
            location = f"chunk {chunk.get('chunk_index', 0)}"
        
        return f"[{doc_name} – {location}]"
    
    def construct_prompt(self, query: str, chunks: List[Dict[str, Any]]) -> str:
        """
        Construct RAG prompt with retrieved context
        
        Args:
            query: User query
            chunks: Retrieved chunks with metadata
        
        Returns:
            Formatted prompt for LLM
        """
        # Build context from chunks
        context_parts = []
        for idx, chunk in enumerate(chunks, 1):
            citation = self.format_citation(chunk)
            context_parts.append(f"[{idx}] {citation}\n{chunk['text']}\n")
        
        context = "\n".join(context_parts)
        
        # Construct prompt with citation instructions
        prompt = f"""You are a helpful assistant that answers questions based on the provided context.

CONTEXT:
{context}

INSTRUCTIONS:
1. Answer the user's question using ONLY the information from the context above
2. After EACH sentence in your answer, add an inline citation in the format [source_name – page/section]
3. Use the exact citation format shown in the context (e.g., [document.pdf – page 5])
4. If the context doesn't contain enough information to answer, say so clearly
5. Be concise and accurate

USER QUESTION:
{query}

ANSWER:"""
        
        return prompt
    
    def generate_answer(
        self,
        query: str,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Generate answer with citations using RAG
        
        Args:
            query: User query
            top_k: Number of chunks to retrieve
        
        Returns:
            Dict with answer, citations, and metrics:
            {
                "answer": str,
                "chunks": List[Dict],
                "retrieval_latency_ms": float,
                "generation_latency_ms": float,
                "total_latency_ms": float
            }
        """
        import time
        
        total_start = time.time()
        
        # Step 1: Retrieve relevant chunks
        retrieval_result = self.retriever.retrieve(query, top_k=top_k)
        chunks = retrieval_result["chunks"]
        retrieval_latency = retrieval_result["retrieval_latency_ms"]
        
        if not chunks:
            return {
                "answer": "I couldn't find any relevant information to answer your question.",
                "chunks": [],
                "retrieval_latency_ms": retrieval_latency,
                "generation_latency_ms": 0,
                "total_latency_ms": (time.time() - total_start) * 1000
            }
        
        # Step 2: Construct prompt
        prompt = self.construct_prompt(query, chunks)
        
        # Step 3: Generate answer
        print(f"→ Generating answer using {self.llm_model}...")
        gen_start = time.time()
        
        response = self.openai_client.chat.completions.create(
            model=self.llm_model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides accurate answers with citations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        answer = response.choices[0].message.content
        generation_latency = (time.time() - gen_start) * 1000
        total_latency = (time.time() - total_start) * 1000
        
        print(f"✓ Generated answer (latency: {generation_latency:.2f} ms)")
        
        return {
            "answer": answer,
            "chunks": chunks,
            "retrieval_latency_ms": round(retrieval_latency, 2),
            "generation_latency_ms": round(generation_latency, 2),
            "total_latency_ms": round(total_latency, 2)
        }
