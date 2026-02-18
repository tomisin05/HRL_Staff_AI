# Backend Document
## RA HousingBot — Tech Stack & Data Schema

---

## 1. Full Tech Stack

### Frontend
| Component | Tool | Reason |
|-----------|------|--------|
| UI Framework | **Streamlit** | Pure Python, no JS needed, free hosting |
| Hosting | **Streamlit Community Cloud** | Free, GitHub-connected deployment |

### Backend / Logic
| Component | Tool | Reason |
|-----------|------|--------|
| Language | **Python 3.11+** | Ecosystem for ML/NLP is unmatched |
| App orchestration | **LlamaIndex** | Purpose-built for RAG pipelines, clean abstractions |
| PDF parsing | **PyMuPDF (fitz)** | Fast, accurate, handles complex PDFs |
| DOCX parsing | **python-docx** | Standard library for Word files |
| Text cleaning | **regex + custom utils** | Strip noise from extracted text |

### Embeddings
| Component | Tool | Reason |
|-----------|------|--------|
| Embedding model | **`all-MiniLM-L6-v2`** (HuggingFace) | Free, runs locally, 384-dim vectors, fast |
| Embedding library | **sentence-transformers** | Easy local inference, no API cost |

### Vector Store
| Component | Tool | Reason |
|-----------|------|--------|
| Vector DB | **Pinecone** (free tier) | Persistent cloud storage, 2GB free, simple API |
| Index type | Cosine similarity | Standard for semantic search |
| Dimensions | 384 | Matches `all-MiniLM-L6-v2` output |

### LLM
| Component | Tool | Reason |
|-----------|------|--------|
| Generation model | **Google Gemini 1.5 Flash** | Free tier (15 RPM, 1M TPM), fast, capable |
| SDK | **`google-generativeai`** | Official Python SDK |

### Secrets / Config
| Component | Tool |
|-----------|------|
| API key management | `st.secrets` (Streamlit) or `.env` + `python-dotenv` locally |

---

## 2. Project Directory Structure

```
ra-housingbot/
│
├── app.py                    # Main Streamlit app (chat interface)
├── admin.py                  # Admin panel (document management)
│
├── core/
│   ├── ingest.py             # Document parsing, chunking, embedding, upsert
│   ├── retrieval.py          # Query embedding + Pinecone search
│   ├── generation.py         # Prompt building + Gemini API call
│   └── utils.py              # Text cleaning, file helpers
│
├── config/
│   └── settings.py           # Constants: chunk size, top-k, thresholds, model names
│
├── data/
│   └── feedback.json         # Stores user feedback logs (local file)
│
├── .streamlit/
│   └── secrets.toml          # API keys (not committed to git)
│
├── requirements.txt
└── README.md
```

---

## 3. Data Schema

### 3a. Pinecone Vector Index

**Index name:** `ra-housingbot`
**Dimensions:** `384`
**Metric:** `cosine`

Each vector in Pinecone represents one document chunk and is stored with the following structure:

```json
{
  "id": "chunk_unique_id",
  "values": [0.023, -0.187, ...],   // 384-dimensional embedding
  "metadata": {
    "doc_name": "RA Handbook 2024.pdf",
    "doc_id": "ra_handbook_2024",
    "chunk_index": 12,
    "page_number": 5,
    "section": "Section 4 - Guest Policy",
    "text": "Guests may stay for a maximum of two consecutive nights...",
    "upload_date": "2025-08-01T14:32:00Z"
  }
}
```

**Field Descriptions:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | `{doc_id}_chunk_{chunk_index}` — unique per chunk |
| `values` | float[] | 384-dim embedding vector |
| `doc_name` | string | Original filename shown to user in citations |
| `doc_id` | string | Slugified doc name used for deletion/deduplication |
| `chunk_index` | int | Position of chunk within document (0-indexed) |
| `page_number` | int | Page where chunk originates (if available) |
| `section` | string | Section heading above chunk (if parseable) |
| `text` | string | Raw chunk text passed to Gemini as context |
| `upload_date` | ISO datetime | When the document was ingested |

---

### 3b. Feedback Log Schema

Stored in `data/feedback.json` as a list of objects:

```json
[
  {
    "feedback_id": "fb_20250801_143201_a3f2",
    "timestamp": "2025-08-01T14:32:01Z",
    "session_id": "sess_abc123",
    "user_query": "What is the quiet hours policy?",
    "bot_answer": "Quiet hours are enforced from 10pm to 8am on weekdays...",
    "sources_used": ["RA Handbook 2024.pdf - Section 6.1"],
    "rating": "thumbs_up",
    "top_k_scores": [0.87, 0.81, 0.74, 0.69, 0.65]
  }
]
```

---

### 3c. Document Registry Schema

Stored in `data/documents.json` to track all ingested documents:

```json
[
  {
    "doc_id": "ra_handbook_2024",
    "doc_name": "RA Handbook 2024.pdf",
    "file_type": "pdf",
    "chunk_count": 42,
    "upload_date": "2025-08-01T14:00:00Z",
    "file_size_kb": 1240,
    "status": "active"
  }
]
```

---

## 4. Core Logic Details

### Chunking Strategy

```python
CHUNK_SIZE = 500        # tokens
CHUNK_OVERLAP = 50      # tokens
SEPARATORS = ["\n\n", "\n", ". "]   # priority order for splitting
```

Chunking uses LlamaIndex's `SentenceSplitter` with the above config. Where section headings are detected (via regex on common heading patterns), chunks are split at heading boundaries first.

### Retrieval Strategy

```python
TOP_K = 5                          # chunks retrieved per query
SIMILARITY_THRESHOLD = 0.40        # minimum score to use a chunk
FALLBACK_THRESHOLD_COUNT = 0       # if 0 chunks pass threshold → fallback response
```

Query flow:
1. Embed user query with `all-MiniLM-L6-v2`
2. Query Pinecone for top-5 cosine similarity matches
3. Filter out chunks below `SIMILARITY_THRESHOLD`
4. If no chunks pass: return fallback message
5. Sort remaining chunks by score (descending)
6. Pass chunks as context to Gemini

### Prompt Template

```
System:
You are a knowledgeable housing assistant for Resident Advisors (RAs).
Answer questions ONLY based on the provided documentation excerpts.
If the answer is not in the documentation, say so clearly and suggest the RA contact their Hall Director.
Always cite the source document and section for your answer.
Be concise, direct, and professional.

Documentation Context:
[CHUNK 1 — Source: RA Handbook 2024, Section 4.2]
{chunk_1_text}

[CHUNK 2 — Source: Emergency Procedures, Page 3]
{chunk_2_text}

... (up to 5 chunks)

Conversation History:
{last_6_turns}

User Question:
{user_query}
```

---

## 5. Dependencies (requirements.txt)

```
streamlit>=1.35.0
google-generativeai>=0.7.0
pinecone-client>=3.0.0
sentence-transformers>=3.0.0
llama-index>=0.10.0
llama-index-vector-stores-pinecone>=0.1.0
PyMuPDF>=1.24.0
python-docx>=1.1.0
python-dotenv>=1.0.0
```

---

## 6. Environment Variables

```toml
# .streamlit/secrets.toml

GEMINI_API_KEY = "your_gemini_api_key"
PINECONE_API_KEY = "your_pinecone_api_key"
PINECONE_INDEX_NAME = "ra-housingbot"
ADMIN_PASSWORD = "your_admin_password"
```
