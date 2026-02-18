# App Flow Document
## RA HousingBot — User & System Flows

---

## 1. High-Level Architecture Flow

```
User Query
    │
    ▼
[Streamlit Frontend]
    │
    ▼
[Query Embedding]  ←── all-MiniLM-L6-v2 (HuggingFace)
    │
    ▼
[Pinecone Vector Search]  ←── Top-k relevant chunks retrieved
    │
    ▼
[Prompt Construction]  ←── System prompt + context chunks + chat history + user query
    │
    ▼
[Gemini API]  ←── Generates grounded answer
    │
    ▼
[Response + Citations]  ──► Displayed to user
```

---

## 2. Document Ingestion Flow (Admin)

```
Admin uploads PDF/DOCX
    │
    ▼
File validation (type, size check)
    │
    ▼
Text extraction  ←── PyMuPDF (PDF) / python-docx (DOCX)
    │
    ▼
Text cleaning  ←── Remove headers/footers, fix encoding
    │
    ▼
Chunking  ←── 500 tokens, 50-token overlap, split by section if possible
    │
    ▼
Embedding each chunk  ←── all-MiniLM-L6-v2
    │
    ▼
Upsert to Pinecone  ←── With metadata: {doc_name, chunk_id, page, section}
    │
    ▼
Confirmation message shown to admin
```

---

## 3. RA Chat Flow (End User)

### 3a. Session Start
1. RA opens the app URL
2. Landing page shows: welcome message, suggested starter questions, chat input box
3. Session initialized (empty chat history, unique session ID)

### 3b. Asking a Question
1. RA types question into chat input
2. App displays a loading spinner ("Searching documentation...")
3. Backend:
   - Embeds the user query
   - Queries Pinecone for top-5 most relevant chunks
   - Checks similarity scores — if all scores below threshold (0.4), trigger fallback
   - Builds prompt with system instructions, retrieved chunks, conversation history, and user query
   - Calls Gemini API
   - Parses response
4. App displays:
   - AI-generated answer
   - Source citations (document name, section/page)
   - Expandable "View source chunks" section (optional)

### 3c. Follow-up Questions
1. Chat history (last 6 turns) passed to Gemini on each subsequent query
2. User can reference previous answers naturally ("What about the exception you mentioned?")

### 3d. Feedback
1. Below each answer: 👍 / 👎 buttons
2. On click: feedback logged with query, answer, and rating
3. Toast notification: "Thanks for your feedback!"

### 3e. Session End
- No explicit logout needed (stateless session)
- Chat history cleared on page refresh

---

## 4. Admin Flow

### 4a. Document Management Page
1. Admin navigates to `/admin` (password-protected)
2. Views list of all ingested documents with: name, upload date, chunk count
3. Can upload new documents (drag & drop or file picker)
4. Can delete documents (triggers deletion of all associated Pinecone vectors)

### 4b. Feedback Review Page
1. Admin views all submitted feedback entries
2. Filterable by thumbs up / thumbs down
3. Can export as CSV for analysis

---

## 5. Error Flow

| Scenario | System Behavior |
|----------|----------------|
| Gemini API timeout | Show: "The AI is taking too long. Please try again." |
| Pinecone connection failure | Show: "Unable to search documentation. Please try again later." |
| No relevant chunks found | Show fallback message with hall director contact suggestion |
| Uploaded file is corrupted | Show: "File could not be parsed. Please check the document and re-upload." |
| File type not supported | Show: "Only PDF and DOCX files are supported." |

---

## 6. Page Map

```
/                   ←── RA Chat Interface (main)
/admin              ←── Admin login + document management
/admin/feedback     ←── Feedback review dashboard
```

---

## 7. State Management

- **Chat history:** Stored in Streamlit `st.session_state` (cleared on refresh)
- **Document index:** Persisted in Pinecone (cloud)
- **Feedback logs:** Written to a lightweight JSON file or Google Sheet (free)
- **Admin auth:** Simple password check via `st.secrets`
