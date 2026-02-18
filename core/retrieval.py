from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from config.settings import *

class Retriever:
    def __init__(self, pinecone_api_key):
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        self.pc = Pinecone(api_key=pinecone_api_key)
        self.index = self.pc.Index(PINECONE_INDEX_NAME)
    
    def retrieve(self, query, top_k=TOP_K):
        """Retrieve relevant chunks for a query"""
        query_embedding = self.embedding_model.encode(query).tolist()
        
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        # Filter by similarity threshold
        filtered_chunks = []
        for match in results['matches']:
            if match['score'] >= SIMILARITY_THRESHOLD:
                filtered_chunks.append({
                    'text': match['metadata']['text'],
                    'doc_name': match['metadata']['doc_name'],
                    'page_number': match['metadata'].get('page_number', 'N/A'),
                    'score': match['score']
                })
        
        return filtered_chunks
