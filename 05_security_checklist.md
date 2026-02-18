# Security Checklist
## RA HousingBot — Security & Privacy Requirements

---

## 1. API Key & Secrets Management

- [ ] **Never hardcode API keys** in source code or commit them to GitHub
- [ ] Store all secrets in `.streamlit/secrets.toml` locally and in Streamlit Cloud's Secrets Manager for deployment
- [ ] Add `.streamlit/secrets.toml` and `.env` to `.gitignore` immediately
- [ ] Rotate API keys if they are ever accidentally exposed in a commit
- [ ] Use environment-specific keys (separate keys for dev vs. production)
- [ ] Limit Gemini API key permissions to only the services needed (generative language API)
- [ ] Set up Pinecone API key with minimum required permissions (read/write to one index only)

---

## 2. Admin Access Control

- [ ] Admin panel (`/admin`) is password-protected via `st.secrets["ADMIN_PASSWORD"]`
- [ ] Admin password is a strong password (16+ characters, mixed case, numbers, symbols)
- [ ] Admin password is stored only in secrets — never in code or plain text files
- [ ] Consider adding a simple session timeout for admin (re-prompt password after inactivity)
- [ ] Log all admin actions (document upload, deletion) with timestamps to an audit log
- [ ] Admin panel is clearly separated from RA-facing interface (separate Streamlit page or app)

---

## 3. Input Validation & Injection Prevention

- [ ] Sanitize all user chat inputs before embedding or passing to Gemini (strip HTML tags, excessive whitespace)
- [ ] Limit input length — reject queries over 1000 characters with a user-facing error
- [ ] Validate uploaded file types server-side (check MIME type, not just extension)
- [ ] Limit upload file size (e.g., max 20MB per file) to prevent abuse
- [ ] Scan uploaded documents for unexpected executable content (basic check: reject files with embedded scripts)
- [ ] Prompt injection mitigation: system prompt explicitly instructs Gemini to ignore instructions embedded in user queries or documents
- [ ] Never pass raw user input directly into system-level operations (file paths, shell commands)

---

## 4. Data Privacy

- [ ] No Personally Identifiable Information (PII) is collected or stored
- [ ] Chat history is session-only — cleared on refresh, never persisted to a database
- [ ] Feedback logs store only the query text and rating — no user identity, IP, or session linking
- [ ] Inform RAs in the UI that queries are sent to Google Gemini (third-party API) for processing
- [ ] Review Google Gemini's data retention policies — ensure compliance with institutional data policies
- [ ] Do not upload documents containing student PII (SSNs, conduct records, medical info) to the system
- [ ] Implement a data retention policy for feedback logs — purge logs older than one academic year

---

## 5. Document Security

- [ ] Only trusted admins can ingest documents — no public document upload endpoint
- [ ] Validate that uploaded documents are legitimate housing docs before ingestion (admin responsibility)
- [ ] Store document metadata (not raw text) in the local registry — raw text is in Pinecone only
- [ ] Implement Pinecone namespace isolation if multiple housing departments share one instance
- [ ] Ensure deleted documents are fully removed from Pinecone (delete by `doc_id` prefix filter)

---

## 6. Transport & Infrastructure Security

- [ ] All traffic served over HTTPS (Streamlit Community Cloud enforces this by default)
- [ ] Pinecone and Gemini API calls made over HTTPS only
- [ ] Do not log raw API responses containing chunk text to console in production
- [ ] Set appropriate CORS headers if ever building a standalone API backend

---

## 7. Dependency Security

- [ ] Pin dependency versions in `requirements.txt` to prevent supply chain attacks
- [ ] Regularly audit dependencies with `pip audit` or `safety check`
- [ ] Update dependencies at least once per semester
- [ ] Avoid dependencies with known critical CVEs
- [ ] Use only well-maintained, widely-used packages (no abandoned libraries)

---

## 8. Abuse & Rate Limiting

- [ ] Be aware of Gemini free tier rate limits (15 RPM) — add a try/except with a user-friendly error if rate limit is hit
- [ ] Add basic client-side throttling in Streamlit (disable send button while response is loading)
- [ ] If usage grows, consider adding Streamlit authentication (Streamlit's built-in auth or Auth0) to restrict access to RAs only
- [ ] Monitor Gemini and Pinecone usage dashboards for unexpected spikes

---

## 9. Deployment Checklist (Before Going Live)

- [ ] All secrets confirmed stored in Streamlit Cloud Secrets Manager (not in repo)
- [ ] `.gitignore` reviewed — no sensitive files tracked
- [ ] GitHub repo set to **private**
- [ ] Test that admin panel cannot be accessed without password
- [ ] Test fallback response is triggered when no relevant docs found
- [ ] Test that uploading a non-PDF/DOCX file is rejected gracefully
- [ ] Verify Gemini responses never include fabricated policy information (manual QA with 10+ test queries)
- [ ] Inform RAs that this tool is an aid — not a replacement for official policy consultation

---

## 10. Ongoing Security Practices

- [ ] Review and update documents each semester (remove outdated policy docs)
- [ ] Review feedback logs monthly for signs of prompt injection attempts or policy misuse
- [ ] Check for new CVEs in dependencies each semester
- [ ] Rotate Gemini and Pinecone API keys annually
- [ ] Maintain an incident response plan: what to do if API keys are leaked or the app is abused
