"""
Document Utilities - PDF Loader
Extracts text from PDF files with page number tracking
"""

from typing import List, Dict
import PyPDF2
from io import BytesIO


def load_pdf(file_content: bytes, filename: str) -> List[Dict[str, any]]:
    """
    Extract text from PDF file with page-level metadata
    
    Args:
        file_content: PDF file content as bytes
        filename: Original filename
    
    Returns:
        List of dicts with structure:
        {
            "text": str,
            "page_number": int,
            "document_name": str
        }
    """
    pages = []
    
    try:
        # Create PDF reader from bytes
        pdf_file = BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Extract text from each page
        for page_num, page in enumerate(pdf_reader.pages, start=1):
            text = page.extract_text()
            
            # Only include pages with actual text content
            if text and text.strip():
                pages.append({
                    "text": text.strip(),
                    "page_number": page_num,
                    "document_name": filename
                })
        
        print(f"✓ Extracted {len(pages)} pages from {filename}")
        
    except Exception as e:
        print(f"✗ Error loading PDF {filename}: {str(e)}")
        raise
    
    return pages
