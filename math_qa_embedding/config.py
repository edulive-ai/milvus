import os
from dotenv import load_dotenv

# Tải biến môi trường từ file .env
load_dotenv()

# Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Milvus Configuration
MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = int(os.getenv("MILVUS_PORT", 19530))
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "math_qa_collection")

# Vector dimensions cho embedding từ Gemini
EMBEDDING_DIM = 768 