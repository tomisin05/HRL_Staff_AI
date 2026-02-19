import fitz
from docx import Document
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from datetime import datetime
import json
from pathlib import Path
from config.settings import *
from core.utils import clean_text, generate_doc_id
import streamlit as st

class DocumentIngestor:
    def __init__(self, pinecone_api_key):
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        self.pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
        self.index = self.pc.Index(PINECONE_INDEX_NAME)
    
    def extract_text_from_pdf(self, file):
        """Extract text from PDF file"""
        doc = fitz.open(stream=file.read(), filetype="pdf")
        text_chunks = []
        for page_num, page in enumerate(doc, 1):
            text = page.get_text()
            if text.strip():
                text_chunks.append((clean_text(text), page_num))
        return text_chunks
    
    def extract_text_from_docx(self, file):
        """Extract text from DOCX file"""
        doc = Document(file)
        text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        return [(clean_text(text), 1)]
    
    def chunk_text(self, text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        return chunks
    
    def ingest_document(self, file, doc_name):
        """Process and ingest a document into Pinecone"""
        doc_id = generate_doc_id(doc_name)
        file_ext = Path(doc_name).suffix.lower()
        
        # Extract text
        if file_ext == '.pdf':
            page_texts = self.extract_text_from_pdf(file)
        else:
            page_texts = self.extract_text_from_docx(file)
        
        # Chunk and embed
        vectors = []
        chunk_count = 0
        
        for page_text, page_num in page_texts:
            chunks = self.chunk_text(page_text)
            for chunk_idx, chunk in enumerate(chunks):
                embedding = self.embedding_model.encode(chunk).tolist()
                vector_id = f"{doc_id}_chunk_{chunk_count}"
                
                vectors.append({
                    "id": vector_id,
                    "values": embedding,
                    "metadata": {
                        "doc_name": doc_name,
                        "doc_id": doc_id,
                        "chunk_index": chunk_count,
                        "page_number": page_num,
                        "text": chunk,
                        "upload_date": datetime.utcnow().isoformat()
                    }
                })
                chunk_count += 1
        
        # Upsert to Pinecone
        self.index.upsert(vectors=vectors)
        
        # Update document registry
        self._update_registry(doc_id, doc_name, file_ext, chunk_count)
        
        return chunk_count
    
    def _update_registry(self, doc_id, doc_name, file_type, chunk_count):
        """Update local document registry"""
        registry_path = Path("data/documents.json")
        registry_path.parent.mkdir(exist_ok=True)
        
        if registry_path.exists():
            with open(registry_path, 'r') as f:
                registry = json.load(f)
        else:
            registry = []
        
        registry.append({
            "doc_id": doc_id,
            "doc_name": doc_name,
            "file_type": file_type,
            "chunk_count": chunk_count,
            "upload_date": datetime.utcnow().isoformat(),
            "status": "active"
        })
        
        with open(registry_path, 'w') as f:
            json.dump(registry, f, indent=2)
    
    def delete_document(self, doc_id):
        """Delete all vectors for a document from Pinecone"""
        self.index.delete(filter={"doc_id": doc_id})
        
        # Update registry
        registry_path = Path("data/documents.json")
        if registry_path.exists():
            with open(registry_path, 'r') as f:
                registry = json.load(f)
            registry = [doc for doc in registry if doc['doc_id'] != doc_id]
            with open(registry_path, 'w') as f:
                json.dump(registry, f, indent=2)
