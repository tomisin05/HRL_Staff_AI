# Configuration settings for RA HousingBot

# Chunking parameters
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# Retrieval parameters
TOP_K = 5
SIMILARITY_THRESHOLD = 0.40

# Model names
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
PINECONE_INDEX_NAME = "ra-housingbot"
GEMINI_MODEL = "gemini-1.5-flash"

# File constraints
MAX_FILE_SIZE_MB = 20
ALLOWED_EXTENSIONS = [".pdf", ".docx"]

# Chat parameters
MAX_CHAT_HISTORY = 6
MAX_QUERY_LENGTH = 1000
