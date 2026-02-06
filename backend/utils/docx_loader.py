"""
Document Utilities - DOCX Loader
Extracts text from Word documents with paragraph tracking
"""

from typing import List, Dict
from docx import Document
from io import BytesIO


def load_docx(file_content: bytes, filename: str) -> List[Dict[str, any]]:
    """
    Extract text from DOCX file with paragraph-level metadata
    
    Args:
        file_content: DOCX file content as bytes
        filename: Original filename
    
    Returns:
        List of dicts with structure:
        {
            "text": str,
            "paragraph_index": int,
            "document_name": str
        }
    """
    paragraphs = []
    
    try:
        # Create Document from bytes
        docx_file = BytesIO(file_content)
        doc = Document(docx_file)
        
        # Extract text from each paragraph
        for para_idx, paragraph in enumerate(doc.paragraphs, start=1):
            text = paragraph.text
            
            # Only include paragraphs with actual text content
            if text and text.strip():
                paragraphs.append({
                    "text": text.strip(),
                    "paragraph_index": para_idx,
                    "document_name": filename
                })
        
        print(f"✓ Extracted {len(paragraphs)} paragraphs from {filename}")
        
    except Exception as e:
        print(f"✗ Error loading DOCX {filename}: {str(e)}")
        raise
    
    return paragraphs
