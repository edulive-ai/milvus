import google.generativeai as genai
import numpy as np
import os
import sys
import json
import time

# Thêm thư mục cha vào sys.path để có thể import từ thư mục gốc
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from config import GEMINI_API_KEY

# Cấu hình API Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Tên model embedding
MODEL_NAME = "models/embedding-001"

def get_embedding(text):
    """Tạo embedding cho văn bản sử dụng Gemini API."""
    try:
        # Thêm delay nhỏ để tránh rate limit
        time.sleep(0.1)
        
        # In thông tin debug
        print(f"Tạo embedding cho: {text[:50]}...")
        
        # Sử dụng phương thức embedding mới
        result = genai.embed_content(
            model=MODEL_NAME,
            content=text,
            task_type="RETRIEVAL_QUERY"
        )
        
        # Trả về embedding vector dưới dạng numpy array
        embedding = np.array(result["embedding"])
        
        # Kiểm tra shape của embedding
        print(f"Đã tạo embedding với shape: {embedding.shape}")
        
        return embedding
    except Exception as e:
        print(f"Lỗi khi tạo embedding: {e}")
        return None

def batch_get_embeddings(texts, batch_size=10):
    """Tạo embeddings cho nhiều văn bản với xử lý theo batch."""
    all_embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        batch_embeddings = []
        
        for text in batch:
            embedding = get_embedding(text)
            if embedding is not None:
                batch_embeddings.append(embedding)
            else:
                # Nếu có lỗi, thêm một vector 0 với kích thước phù hợp
                batch_embeddings.append(np.zeros(768))
        
        all_embeddings.extend(batch_embeddings)
    
    return all_embeddings 