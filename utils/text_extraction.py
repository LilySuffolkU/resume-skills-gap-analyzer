"""
Text extraction utilities for resume processing.
Supports PDF, DOCX, and TXT file formats.
"""

import re
from typing import Optional
import PyPDF2
from docx import Document
import io


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text from PDF file bytes.
    
    Args:
        file_bytes: PDF file content as bytes
        
    Returns:
        Extracted text as string
        
    Raises:
        Exception: If PDF cannot be read
    """
    try:
        pdf_file = io.BytesIO(file_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
            
        return text
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")


def extract_text_from_docx(file_bytes: bytes) -> str:
    """
    Extract text from DOCX file bytes.
    
    Args:
        file_bytes: DOCX file content as bytes
        
    Returns:
        Extracted text as string
        
    Raises:
        Exception: If DOCX cannot be read
    """
    try:
        docx_file = io.BytesIO(file_bytes)
        doc = Document(docx_file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        raise Exception(f"Failed to extract text from DOCX: {str(e)}")


def extract_text_from_txt(file_bytes: bytes) -> str:
    """
    Extract text from TXT file bytes.
    
    Args:
        file_bytes: TXT file content as bytes
        
    Returns:
        Extracted text as string
        
    Raises:
        Exception: If TXT cannot be read
    """
    try:
        # Try UTF-8 first, then fallback to latin-1
        try:
            text = file_bytes.decode('utf-8')
        except UnicodeDecodeError:
            text = file_bytes.decode('latin-1')
        return text
    except Exception as e:
        raise Exception(f"Failed to extract text from TXT: {str(e)}")


def clean_text(text: str) -> str:
    """
    Clean extracted text by removing excessive whitespace and normalizing.
    
    Args:
        text: Raw extracted text
        
    Returns:
        Cleaned text
    """
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    # Normalize line breaks
    text = re.sub(r'\n+', '\n', text)
    return text


def extract_text_from_file(file_bytes: bytes, file_type: str) -> str:
    """
    Main function to extract text from uploaded file.
    
    Args:
        file_bytes: File content as bytes
        file_type: File extension (pdf, docx, txt)
        
    Returns:
        Cleaned extracted text
        
    Raises:
        Exception: If file type is unsupported or extraction fails
    """
    file_type = file_type.lower()
    
    if file_type == 'pdf':
        text = extract_text_from_pdf(file_bytes)
    elif file_type in ['docx', 'doc']:
        text = extract_text_from_docx(file_bytes)
    elif file_type == 'txt':
        text = extract_text_from_txt(file_bytes)
    else:
        raise Exception(f"Unsupported file type: {file_type}. Supported types: PDF, DOCX, TXT")
    
    return clean_text(text)

