# RA HousingBot — RAG-Powered Chatbot

A Retrieval-Augmented Generation (RAG) chatbot for Resident Advisors to query housing policies and documentation.

## Features

- 🤖 Natural language Q&A powered by Google Gemini
- 📚 Document ingestion (PDF/DOCX) with vector search via Pinecone
- 📄 Source citations for all answers
- 👍👎 Feedback mechanism
- 🔐 Admin panel for document management
- ⚡ Fast semantic search with sentence-transformers

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Create `.streamlit/secrets.toml` from the template:

```bash
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml` and add your keys:

```toml
GEMINI_API_KEY = "your_gemini_api_key"
PINECONE_API_KEY = "your_pinecone_api_key"
PINECONE_INDEX_NAME = "ra-housingbot"
ADMIN_PASSWORD = "your_secure_password"
```

### 3. Create Pinecone Index

Go to [Pinecone Console](https://app.pinecone.io/) and create an index:
- Name: `ra-housingbot`
- Dimensions: `384`
- Metric: `cosine`

### 4. Run the App

```bash
streamlit run app.py
```

## Usage

### For RAs (End Users)

1. Open the app URL
2. Type questions about housing policies
3. View AI-generated answers with source citations
4. Provide feedback with 👍/👎 buttons

### For Admins

1. Navigate to the Admin page (sidebar link)
2. Login with admin password
3. Upload PDF/DOCX documents
4. View and manage ingested documents
5. Review user feedback

## Project Structure

```
HRL_Staff_AI/
├── app.py                    # Main chat interface
├── pages/
│   └── admin.py              # Admin panel
├── core/
│   ├── ingest.py             # Document processing
│   ├── retrieval.py          # Vector search
│   ├── generation.py         # Gemini integration
│   └── utils.py              # Helper functions
├── config/
│   └── settings.py           # Configuration constants
├── data/                     # Generated at runtime
│   ├── documents.json        # Document registry
│   └── feedback.json         # User feedback logs
└── requirements.txt
```

## Security Notes

- Never commit `.streamlit/secrets.toml` to git
- Use strong admin passwords
- Review the security checklist in `05_security_checklist.md`
- Rotate API keys if exposed

## Deployment

Deploy to Streamlit Community Cloud:

1. Push code to GitHub (private repo)
2. Connect repo to Streamlit Cloud
3. Add secrets in Streamlit Cloud dashboard
4. Deploy!

## License

Internal use only - University Housing
