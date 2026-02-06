"""
Document Utilities - Text Chunker
Splits text into overlapping chunks with metadata preservation
"""

from typing import List, Dict, Any


def chunk_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    metadata: Dict[str, Any] = None
) -> List[Dict[str, Any]]:
    """
    Split text into overlapping chunks
    
    Args:
        text: Text to chunk
        chunk_size: Maximum characters per chunk
        chunk_overlap: Number of overlapping characters between chunks
        metadata: Metadata to attach to each chunk
    
    Returns:
        List of chunks with metadata:
        {
            "text": str,
            "chunk_index": int,
            **metadata
        }
    """
    if not text or not text.strip():
        return []
    
    chunks = []
    start = 0
    chunk_index = 0
    
    while start < len(text):
        # Calculate end position
        end = start + chunk_size
        
        # Extract chunk
        chunk = text[start:end].strip()
        
        if chunk:
            chunk_data = {
                "text": chunk,
                "chunk_index": chunk_index,
                **(metadata or {})
            }
            chunks.append(chunk_data)
            chunk_index += 1
        
        # Move to next chunk with overlap
        start = end - chunk_overlap
        
        # Prevent infinite loop
        if start >= len(text):
            break
    
    return chunks


def chunk_documents(
    documents: List[Dict[str, Any]],
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> List[Dict[str, Any]]:
    """
    Chunk multiple documents while preserving metadata
    
    Args:
        documents: List of document dicts with 'text' field
        chunk_size: Maximum characters per chunk
        chunk_overlap: Number of overlapping characters
    
    Returns:
        List of all chunks from all documents with preserved metadata
    """
    all_chunks = []
    
    for doc in documents:
        text = doc.get("text", "")
        
        # Extract metadata (everything except 'text')
        metadata = {k: v for k, v in doc.items() if k != "text"}
        
        # Chunk this document
        doc_chunks = chunk_text(
            text=text,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            metadata=metadata
        )
        
        all_chunks.extend(doc_chunks)
    
    print(f"✓ Created {len(all_chunks)} chunks from {len(documents)} documents")
    
    return all_chunks
