import streamlit as st
from datetime import datetime
import json
from pathlib import Path
from core.retrieval import Retriever
from core.generation import Generator
from config.settings import MAX_QUERY_LENGTH

# Page config
st.set_page_config(page_title="RA HousingBot", page_icon="🏠", layout="centered")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background-color: #1A3A5C;
        padding: 1rem;
        border-radius: 8px;
        color: white;
        margin-bottom: 2rem;
    }
    .user-message {
        background-color: #DCE8F5;
        padding: 12px 16px;
        border-radius: 12px 12px 2px 12px;
        margin: 8px 0;
        text-align: right;
    }
    .bot-message {
        background-color: white;
        border: 1px solid #E2E8F0;
        padding: 16px;
        border-radius: 12px 12px 12px 2px;
        margin: 8px 0;
    }
    .citation {
        background-color: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-radius: 6px;
        padding: 8px;
        margin-top: 8px;
        font-size: 12px;
        font-style: italic;
        color: #2563EB;
    }
    .fallback-message {
        border-left: 4px solid #E67E22;
        background-color: #FFF7ED;
        padding: 12px;
        margin: 8px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Initialize components
@st.cache_resource
def init_components():
    retriever = Retriever(st.secrets["PINECONE_API_KEY"])
    generator = Generator(st.secrets["GEMINI_API_KEY"])
    return retriever, generator

try:
    retriever, generator = init_components()
except Exception as e:
    st.error("Failed to initialize. Please check your API keys.")
    st.stop()

# Header
st.markdown('<div class="main-header"><h1>🏠 RA HousingBot</h1><p>Ask me anything about housing policies...</p></div>', unsafe_allow_html=True)

# Suggested questions
if not st.session_state.messages:
    st.markdown("### 💡 Suggested Questions:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("What's the guest policy?"):
            st.session_state.messages.append({"role": "user", "content": "What's the guest policy?"})
            st.rerun()
        if st.button("What are quiet hours?"):
            st.session_state.messages.append({"role": "user", "content": "What are quiet hours?"})
            st.rerun()
    with col2:
        if st.button("How do I file an incident report?"):
            st.session_state.messages.append({"role": "user", "content": "How do I file an incident report?"})
            st.rerun()

# Display chat history
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        if message.get("is_fallback"):
            st.markdown(f'<div class="fallback-message">⚠️ {message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-message">🤖 {message["content"]}</div>', unsafe_allow_html=True)
            if message.get("sources"):
                sources_html = "<div class='citation'>📄 Sources: " + ", ".join(message["sources"]) + "</div>"
                st.markdown(sources_html, unsafe_allow_html=True)
        
        # Feedback buttons
        col1, col2, col3 = st.columns([6, 1, 1])
        with col2:
            if st.button("👍", key=f"up_{len(st.session_state.messages)}_{message.get('timestamp', '')}"):
                save_feedback(message, "thumbs_up")
                st.toast("Thanks for your feedback!")
        with col3:
            if st.button("👎", key=f"down_{len(st.session_state.messages)}_{message.get('timestamp', '')}"):
                save_feedback(message, "thumbs_down")
                st.toast("Thanks for your feedback!")

# Chat input
user_query = st.chat_input("Ask a question about housing policies...")

if user_query:
    if len(user_query) > MAX_QUERY_LENGTH:
        st.error(f"Query too long. Maximum {MAX_QUERY_LENGTH} characters.")
    else:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_query})
        
        # Show loading
        with st.spinner("Searching documentation..."):
            # Retrieve chunks
            chunks = retriever.retrieve(user_query)
            
            # Generate response
            result = generator.generate(user_query, chunks, st.session_state.chat_history)
            
            # Add bot message
            bot_message = {
                "role": "assistant",
                "content": result['answer'],
                "sources": result['sources'],
                "is_fallback": result['is_fallback'],
                "timestamp": datetime.utcnow().isoformat(),
                "query": user_query
            }
            st.session_state.messages.append(bot_message)
            
            # Update chat history
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            st.session_state.chat_history.append({"role": "assistant", "content": result['answer']})
        
        st.rerun()

def save_feedback(message, rating):
    """Save user feedback to JSON file"""
    feedback_path = Path("data/feedback.json")
    feedback_path.parent.mkdir(exist_ok=True)
    
    if feedback_path.exists():
        with open(feedback_path, 'r') as f:
            feedback = json.load(f)
    else:
        feedback = []
    
    feedback.append({
        "timestamp": datetime.utcnow().isoformat(),
        "user_query": message.get("query", ""),
        "bot_answer": message["content"],
        "sources_used": message.get("sources", []),
        "rating": rating
    })
    
    with open(feedback_path, 'w') as f:
        json.dump(feedback, f, indent=2)

# Admin link
st.sidebar.markdown("---")
st.sidebar.markdown("[Admin Panel](admin)")
