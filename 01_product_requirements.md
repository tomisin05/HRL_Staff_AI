# Product Requirements Document (PRD)
## RA Housing Assistant — RAG-Powered Chatbot

---

## 1. Overview

### Product Name
**RA HousingBot** — A Retrieval-Augmented Generation (RAG) chatbot designed for Resident Advisors (RAs) to query housing policies, procedures, and documentation through a conversational interface.

### Problem Statement
RAs are required to be familiar with large volumes of housing documentation — policy manuals, emergency procedures, conduct protocols, and resident handbooks. Searching through these documents manually is time-consuming, especially during high-pressure situations. RAs need instant, accurate answers grounded in official documentation.

### Solution
A document-specific AI chatbot that ingests official RA/housing documentation, embeds it into a vector store, and uses Gemini to generate accurate, cited answers in response to natural language questions.

### Target Users
- Resident Advisors (RAs) at a university or housing complex
- Potentially: Hall Directors and housing staff (secondary)

---

## 2. Goals & Success Metrics

| Goal | Metric |
|------|--------|
| Reduce time RAs spend searching docs | Avg. query-to-answer < 10 seconds |
| Improve policy accuracy | >90% of answers traceable to source docs |
| High RA adoption | >70% of RAs use it at least once per week |
| Low hallucination rate | <5% of answers contain unverifiable claims |

---

## 3. Functional Requirements

### Core Features

**FR-01: Document Ingestion**
- Admin can upload PDF and DOCX housing documents via a dedicated upload interface
- System parses, chunks, embeds, and stores documents in Pinecone
- Duplicate detection prevents re-uploading the same document

**FR-02: Natural Language Q&A**
- RAs can type questions in plain English
- System retrieves the top-k most relevant document chunks
- Gemini generates a grounded answer using retrieved context
- Answers include source citations (document name + section)

**FR-03: Fallback Behavior**
- If no relevant chunks are found above a confidence threshold, the system responds: *"I couldn't find relevant information in the available documentation. Please contact your Hall Director."*
- System never fabricates policy information

**FR-04: Conversation History**
- Each session maintains multi-turn context (last N messages)
- Context is passed to Gemini to support follow-up questions

**FR-05: Source Citation Display**
- Each answer displays the source document name and, where available, page number or section
- Users can see which chunks were used to generate the answer

**FR-06: Admin Document Management**
- Admin can view all uploaded documents
- Admin can delete outdated documents
- Re-upload triggers re-embedding

### Secondary Features

**FR-07: Query Suggestions**
- Display 3–5 suggested starter questions on the home screen (e.g., "What is the guest policy?", "How do I file an incident report?")

**FR-08: Feedback Mechanism**
- Thumbs up / thumbs down on each answer
- Feedback stored for future review and model improvement

---

## 4. Non-Functional Requirements

- **Performance:** Response time under 10 seconds for 95% of queries
- **Availability:** 99% uptime during academic year (hosted on Streamlit Cloud)
- **Scalability:** Support up to 100 concurrent RA users
- **Accuracy:** Answers must be grounded in documents; no hallucinated policies
- **Privacy:** No personally identifiable information (PII) stored beyond session
- **Accessibility:** WCAG 2.1 AA compliant UI

---

## 5. Out of Scope (v1)

- Voice input/output
- Mobile native app (web-responsive is sufficient)
- Multi-language support
- Integration with housing management software (e.g., StarRez)
- Real-time document sync from shared drives

---

## 6. Assumptions & Constraints

- Documents are provided in English only
- Housing documents are relatively static (updated once or twice per semester)
- All users (RAs) are trusted internal users — no public access
- Free-tier infrastructure only (Pinecone free, Gemini free tier, Streamlit Community Cloud)
