from google import genai
from config.settings import *
import streamlit as st

class Generator:
    def __init__(self, gemini_api_key):
        self.client = genai.Client(api_key=gemini_api_key)

    def build_prompt(self, query, chunks, chat_history):
        system_prompt = """You are a knowledgeable housing assistant for Resident Advisors (RAs).
Answer questions ONLY based on the provided documentation excerpts.
If the answer is not in the documentation, say so clearly and suggest the RA contact their Community Director.
Always cite the source document and section for your answer.
Be concise, direct, and professional."""

        context = "\n\nDocumentation Context:\n"
        for i, chunk in enumerate(chunks, 1):
            context += f"\n[CHUNK {i} — Source: {chunk['doc_name']}, Page {chunk['page_number']}]\n{chunk['text']}\n"

        history = "\n\nConversation History:\n"
        for msg in chat_history[-MAX_CHAT_HISTORY:]:
            history += f"{msg['role']}: {msg['content']}\n"

        return f"{system_prompt}{context}{history}\n\nUser Question:\n{query}"

    def generate(self, query, chunks, chat_history):
        if not chunks:
            return {
                'answer': "I couldn't find relevant information in the available documentation. Please contact your Hall Director for assistance.",
                'sources': [],
                'is_fallback': True
            }

        prompt = self.build_prompt(query, chunks, chat_history)

        try:
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt
            )
            answer = response.text
            sources = list({f"{c['doc_name']} - Page {c['page_number']}" for c in chunks})

            return {
                'answer': answer,
                'sources': sources,
                'is_fallback': False
            }
        except Exception as e:
            return {
                'answer': f"The AI is taking too long. Please try again. Error: {str(e)}",
                'sources': [],
                'is_fallback': True
            }