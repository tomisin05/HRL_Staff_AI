# import streamlit as st
# from datetime import datetime
# import json
# from pathlib import Path
# from core.retrieval import Retriever
# from core.generation import Generator
# from config.settings import MAX_QUERY_LENGTH

# # Page config
# st.set_page_config(page_title="RA HousingBot", page_icon="🏠", layout="centered")

# # Custom CSS
# st.markdown("""
# <style>
#     .main-header {
#         background-color: #1A3A5C;
#         padding: 1rem;
#         border-radius: 8px;
#         color: white;
#         margin-bottom: 2rem;
#     }
#     .user-message {
#         background-color: #DCE8F5;
#         padding: 12px 16px;
#         border-radius: 12px 12px 2px 12px;
#         margin: 8px 0;
#         text-align: right;
#     }
#     .bot-message {
#         background-color: white;
#         border: 1px solid #E2E8F0;
#         padding: 16px;
#         border-radius: 12px 12px 12px 2px;
#         margin: 8px 0;
#     }
#     .citation {
#         background-color: #EFF6FF;
#         border: 1px solid #BFDBFE;
#         border-radius: 6px;
#         padding: 8px;
#         margin-top: 8px;
#         font-size: 12px;
#         font-style: italic;
#         color: #2563EB;
#     }
#     .fallback-message {
#         border-left: 4px solid #E67E22;
#         background-color: #FFF7ED;
#         padding: 12px;
#         margin: 8px 0;
#     }
# </style>
# """, unsafe_allow_html=True)

# # Initialize session state
# if 'chat_history' not in st.session_state:
#     st.session_state.chat_history = []
# if 'messages' not in st.session_state:
#     st.session_state.messages = []

# # Initialize components
# @st.cache_resource
# def init_components():
#     retriever = Retriever(st.secrets["PINECONE_API_KEY"])
#     generator = Generator(st.secrets["GEMINI_API_KEY"])
#     return retriever, generator

# try:
#     retriever, generator = init_components()
# except Exception as e:
#     st.error("Failed to initialize. Please check your API keys.")
#     st.stop()

# # Header
# st.markdown('<div class="main-header"><h1>🏠 RA HousingBot</h1><p>Ask me anything about housing policies...</p></div>', unsafe_allow_html=True)

# # Suggested questions
# if not st.session_state.messages:
#     st.markdown("### 💡 Suggested Questions:")
#     col1, col2 = st.columns(2)
#     with col1:
#         if st.button("What's the guest policy?"):
#             st.session_state.messages.append({"role": "user", "content": "What's the guest policy?"})
#             st.rerun()
#         if st.button("What are quiet hours?"):
#             st.session_state.messages.append({"role": "user", "content": "What are quiet hours?"})
#             st.rerun()
#     with col2:
#         if st.button("How do I file an incident report?"):
#             st.session_state.messages.append({"role": "user", "content": "How do I file an incident report?"})
#             st.rerun()

# # Display chat history
# for message in st.session_state.messages:
#     if message["role"] == "user":
#         st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
#     else:
#         if message.get("is_fallback"):
#             st.markdown(f'<div class="fallback-message">⚠️ {message["content"]}</div>', unsafe_allow_html=True)
#         else:
#             st.markdown(f'<div class="bot-message">🤖 {message["content"]}</div>', unsafe_allow_html=True)
#             if message.get("sources"):
#                 sources_html = "<div class='citation'>📄 Sources: " + ", ".join(message["sources"]) + "</div>"
#                 st.markdown(sources_html, unsafe_allow_html=True)
        
#         # Feedback buttons
#         col1, col2, col3 = st.columns([6, 1, 1])
#         with col2:
#             if st.button("👍", key=f"up_{len(st.session_state.messages)}_{message.get('timestamp', '')}"):
#                 save_feedback(message, "thumbs_up")
#                 st.toast("Thanks for your feedback!")
#         with col3:
#             if st.button("👎", key=f"down_{len(st.session_state.messages)}_{message.get('timestamp', '')}"):
#                 save_feedback(message, "thumbs_down")
#                 st.toast("Thanks for your feedback!")

# # Chat input
# user_query = st.chat_input("Ask a question about housing policies...")

# if user_query:
#     if len(user_query) > MAX_QUERY_LENGTH:
#         st.error(f"Query too long. Maximum {MAX_QUERY_LENGTH} characters.")
#     else:
#         # Add user message
#         st.session_state.messages.append({"role": "user", "content": user_query})
        
#         # Show loading
#         with st.spinner("Searching documentation..."):
#             # Retrieve chunks
#             chunks = retriever.retrieve(user_query)
            
#             # Generate response
#             result = generator.generate(user_query, chunks, st.session_state.chat_history)
            
#             # Add bot message
#             bot_message = {
#                 "role": "assistant",
#                 "content": result['answer'],
#                 "sources": result['sources'],
#                 "is_fallback": result['is_fallback'],
#                 "timestamp": datetime.utcnow().isoformat(),
#                 "query": user_query
#             }
#             st.session_state.messages.append(bot_message)
            
#             # Update chat history
#             st.session_state.chat_history.append({"role": "user", "content": user_query})
#             st.session_state.chat_history.append({"role": "assistant", "content": result['answer']})
        
#         st.rerun()

# def save_feedback(message, rating):
#     """Save user feedback to JSON file"""
#     feedback_path = Path("data/feedback.json")
#     feedback_path.parent.mkdir(exist_ok=True)
    
#     if feedback_path.exists():
#         with open(feedback_path, 'r') as f:
#             feedback = json.load(f)
#     else:
#         feedback = []
    
#     feedback.append({
#         "timestamp": datetime.utcnow().isoformat(),
#         "user_query": message.get("query", ""),
#         "bot_answer": message["content"],
#         "sources_used": message.get("sources", []),
#         "rating": rating
#     })
    
#     with open(feedback_path, 'w') as f:
#         json.dump(feedback, f, indent=2)

# # Admin link
# st.sidebar.markdown("---")
# st.sidebar.markdown("[Admin Panel](admin)")


import streamlit as st
from datetime import datetime, timezone
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
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    /* Hide Streamlit chrome */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 2rem; max-width: 780px; }

    /* Header */
    .app-header {
        border-bottom: 2px solid #1C3557;
        padding-bottom: 1.25rem;
        margin-bottom: 2rem;
    }
    .app-header h1 {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1C3557;
        margin: 0 0 0.25rem 0;
        letter-spacing: -0.02em;
    }
    .app-header p {
        font-size: 0.875rem;
        color: #64748B;
        margin: 0;
    }

    /* Suggestion chips */
    .suggestion-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.75rem;
    }

    /* Messages */
    .msg-user {
        background-color: #1C3557;
        color: #F8FAFC;
        padding: 0.75rem 1rem;
        border-radius: 12px 12px 2px 12px;
        margin: 0.5rem 0 0.5rem 20%;
        font-size: 0.9rem;
        line-height: 1.55;
    }
    .msg-bot {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        color: #1E293B;
        padding: 1rem 1.125rem;
        border-radius: 12px 12px 12px 2px;
        margin: 0.5rem 20% 0.5rem 0;
        font-size: 0.9rem;
        line-height: 1.65;
    }
    .msg-fallback {
        background-color: #FFF7ED;
        border-left: 3px solid #F59E0B;
        color: #78350F;
        padding: 0.75rem 1rem;
        border-radius: 0 8px 8px 0;
        margin: 0.5rem 20% 0.5rem 0;
        font-size: 0.875rem;
        line-height: 1.6;
    }

    /* Sources */
    .sources-block {
        margin: 0.5rem 20% 1rem 0;
        padding: 0.6rem 0.875rem;
        background-color: #EFF6FF;
        border-radius: 6px;
        font-size: 0.78rem;
        font-family: 'DM Mono', monospace;
        color: #2563EB;
        border: 1px solid #BFDBFE;
    }
    .sources-label {
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-size: 0.7rem;
        margin-bottom: 2px;
        opacity: 0.7;
    }

    /* Feedback row */
    .feedback-row {
        margin: -0.25rem 20% 1.25rem 0;
    }

    /* Divider between turns */
    .turn-divider {
        border: none;
        border-top: 1px solid #F1F5F9;
        margin: 0.25rem 0 1rem 0;
    }

    /* Chat input override */
    .stChatInput textarea {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.9rem !important;
        border-radius: 10px !important;
    }

    /* Sidebar */
    .css-1d391kg { background-color: #F8FAFC; }
    .sidebar-link {
        font-size: 0.8rem;
        color: #94A3B8;
        text-decoration: none;
    }

    /* Streamlit button styling for chips */
    div[data-testid="column"] .stButton button {
        background: #F1F5F9;
        color: #334155;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        font-size: 0.82rem;
        font-family: 'DM Sans', sans-serif;
        padding: 0.4rem 0.75rem;
        font-weight: 400;
        width: 100%;
        text-align: left;
        transition: all 0.15s ease;
    }
    div[data-testid="column"] .stButton button:hover {
        background: #E2E8F0;
        border-color: #CBD5E1;
    }

    /* Feedback buttons */
    .feedback-btn .stButton button {
        background: transparent;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        font-size: 0.78rem;
        color: #94A3B8;
        padding: 0.2rem 0.5rem;
    }
    .feedback-btn .stButton button:hover {
        background: #F1F5F9;
        color: #475569;
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
st.markdown("""
<div class="app-header">
    <h1>RA Housing Assistant</h1>
    <p>Ask questions about housing policies, procedures, and guidelines.</p>
</div>
""", unsafe_allow_html=True)

# Suggested questions — only show when no conversation yet
if not st.session_state.messages:
    st.markdown('<div class="suggestion-label">Suggested questions</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    suggestions = [
        ("What is the guest policy?", col1),
        ("What are quiet hours?", col2),
        ("How do I file an incident report?", col1),
        ("What are the move-out procedures?", col2),
    ]
    for text, col in suggestions:
        with col:
            if st.button(text):
                st.session_state.messages.append({"role": "user", "content": text})
                st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)

# Display chat history
def save_feedback(message, rating):
    feedback_path = Path("data/feedback.json")
    feedback_path.parent.mkdir(exist_ok=True)
    if feedback_path.exists():
        with open(feedback_path, 'r') as f:
            feedback = json.load(f)
    else:
        feedback = []
    feedback.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_query": message.get("query", ""),
        "bot_answer": message["content"],
        "sources_used": message.get("sources", []),
        "rating": rating
    })
    with open(feedback_path, 'w') as f:
        json.dump(feedback, f, indent=2)

for idx, message in enumerate(st.session_state.messages):
    if message["role"] == "user":
        st.markdown(f'<div class="msg-user">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        if message.get("is_fallback"):
            st.markdown(
                f'<div class="msg-fallback">{message["content"]}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="msg-bot">{message["content"]}</div>',
                unsafe_allow_html=True
            )
            if message.get("sources"):
                source_list = "<br>".join(message["sources"])
                st.markdown(
                    f'<div class="sources-block"><div class="sources-label">Sources</div>{source_list}</div>',
                    unsafe_allow_html=True
                )

        # Feedback
        ts = message.get("timestamp", str(idx))
        col_gap, col_up, col_down = st.columns([8, 1, 1])
        with col_up:
            if st.button("+ Helpful", key=f"up_{idx}_{ts}"):
                save_feedback(message, "thumbs_up")
                st.toast("Feedback saved.")
        with col_down:
            if st.button("- Not helpful", key=f"down_{idx}_{ts}"):
                save_feedback(message, "thumbs_down")
                st.toast("Feedback saved.")

        st.markdown('<hr class="turn-divider">', unsafe_allow_html=True)

# Chat input
user_query = st.chat_input("Ask about housing policies...")

if user_query:
    if len(user_query) > MAX_QUERY_LENGTH:
        st.error(f"Query too long. Please keep it under {MAX_QUERY_LENGTH} characters.")
    else:
        st.session_state.messages.append({"role": "user", "content": user_query})

        with st.spinner("Searching documentation..."):
            chunks = retriever.retrieve(user_query)
            result = generator.generate(user_query, chunks, st.session_state.chat_history)

            bot_message = {
                "role": "assistant",
                "content": result['answer'],
                "sources": result['sources'],
                "is_fallback": result['is_fallback'],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "query": user_query
            }
            st.session_state.messages.append(bot_message)
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            st.session_state.chat_history.append({"role": "assistant", "content": result['answer']})

        st.rerun()

# Sidebar
st.sidebar.markdown("---")
st.sidebar.markdown('<a class="sidebar-link" href="admin">Admin Panel</a>', unsafe_allow_html=True)