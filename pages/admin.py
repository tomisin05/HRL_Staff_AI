import streamlit as st
import json
from pathlib import Path
from core.ingest import DocumentIngestor
from core.utils import validate_file

# Page config
st.set_page_config(page_title="Admin Panel - RA HousingBot", page_icon="🔐", layout="wide")

# Authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Admin Login")
    password = st.text_input("Enter admin password:", type="password")
    if st.button("Login"):
        if password == st.secrets["ADMIN_PASSWORD"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password")
    st.stop()

# Header
col1, col2 = st.columns([6, 1])
with col1:
    st.title("🏠 RA HousingBot — Admin Panel")
with col2:
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

# Initialize ingestor
@st.cache_resource
def init_ingestor():
    return DocumentIngestor(st.secrets["PINECONE_API_KEY"])

ingestor = init_ingestor()

# Document upload section
st.header("📁 Upload New Document")
uploaded_file = st.file_uploader("Choose a PDF or DOCX file", type=['pdf', 'docx'])

if uploaded_file:
    is_valid, message = validate_file(uploaded_file)
    if is_valid:
        if st.button("Upload and Process"):
            with st.spinner(f"Processing {uploaded_file.name}..."):
                try:
                    chunk_count = ingestor.ingest_document(uploaded_file, uploaded_file.name)
                    st.success(f"✅ Successfully ingested {uploaded_file.name} ({chunk_count} chunks)")
                except Exception as e:
                    st.error(f"❌ Error processing document: {str(e)}")
    else:
        st.error(message)

# Document list section
st.header("📚 Ingested Documents")

registry_path = Path("data/documents.json")
if registry_path.exists():
    with open(registry_path, 'r') as f:
        documents = json.load(f)
    
    if documents:
        for doc in documents:
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            with col1:
                st.write(f"**{doc['doc_name']}**")
            with col2:
                st.write(f"{doc['chunk_count']} chunks")
            with col3:
                st.write(doc['upload_date'][:10])
            with col4:
                if st.button("🗑️", key=f"delete_{doc['doc_id']}"):
                    try:
                        ingestor.delete_document(doc['doc_id'])
                        st.success(f"Deleted {doc['doc_name']}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting: {str(e)}")
    else:
        st.info("No documents uploaded yet.")
else:
    st.info("No documents uploaded yet.")

# Feedback section
st.header("💬 User Feedback")

feedback_path = Path("data/feedback.json")
if feedback_path.exists():
    with open(feedback_path, 'r') as f:
        feedback = json.load(f)
    
    if feedback:
        filter_option = st.selectbox("Filter by:", ["All", "Thumbs Up", "Thumbs Down"])
        
        filtered_feedback = feedback
        if filter_option == "Thumbs Up":
            filtered_feedback = [f for f in feedback if f['rating'] == 'thumbs_up']
        elif filter_option == "Thumbs Down":
            filtered_feedback = [f for f in feedback if f['rating'] == 'thumbs_down']
        
        st.write(f"Showing {len(filtered_feedback)} feedback entries")
        
        for fb in filtered_feedback[-20:]:
            with st.expander(f"{fb['rating']} - {fb['timestamp'][:10]}"):
                st.write(f"**Query:** {fb['user_query']}")
                st.write(f"**Answer:** {fb['bot_answer']}")
                st.write(f"**Sources:** {', '.join(fb['sources_used'])}")
    else:
        st.info("No feedback received yet.")
else:
    st.info("No feedback received yet.")

st.sidebar.markdown("---")
st.sidebar.markdown("[← Back to Chat](../)")
