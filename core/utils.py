import re
import hashlib
from pathlib import Path

def clean_text(text):
    """Clean extracted text from documents"""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    return text.strip()

def generate_doc_id(filename):
    """Generate a unique document ID from filename"""
    return re.sub(r'[^a-z0-9_]', '_', filename.lower().replace('.pdf', '').replace('.docx', ''))

def validate_file(file, max_size_mb=20):
    """Validate uploaded file type and size"""
    if file is None:
        return False, "No file provided"
    
    file_ext = Path(file.name).suffix.lower()
    if file_ext not in ['.pdf', '.docx']:
        return False, "Only PDF and DOCX files are supported"
    
    file.seek(0, 2)
    size_mb = file.tell() / (1024 * 1024)
    file.seek(0)
    
    if size_mb > max_size_mb:
        return False, f"File size exceeds {max_size_mb}MB limit"
    
    return True, "Valid"
