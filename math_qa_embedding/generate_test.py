import json
import random
from pymilvus import connections, Collection
import google.generativeai as genai
import os
import sys
from dotenv import load_dotenv

# Load biến môi trường
load_dotenv()
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from config import GEMINI_API_KEY

# Cấu hình Gemini
genai.configure(api_key=GEMINI_API_KEY)

def connect_to_milvus():
    """Kết nối đến Milvus server"""
    try:
        connections.connect(
            alias="default", 
            host='localhost', 
            port='19530'
        )
        print("Kết nối thành công đến Milvus!")
        return True
    except Exception as e:
        print(f"Lỗi kết nối: {e}")
        return False

def get_random_questions(collection_name, num_questions=10):
    """Lấy ngẫu nhiên một số câu hỏi từ collection"""
    try:
        collection = Collection(collection_name)
        collection.load()
        
        # Lấy tổng số entities
        total_entities = collection.num_entities
        print(f"Tổng số câu hỏi trong collection: {total_entities}")
        
        # Tạo danh sách ID ngẫu nhiên
        random_ids = random.sample(range(total_entities), min(num_questions, total_entities))
        print(f"Đang lấy các ID: {random_ids}")
        
        # Query dữ liệu với điều kiện đơn giản hơn
        results = collection.query(
            expr="id >= 0",  # Lấy tất cả các bản ghi
            output_fields=["id", "question", "answer"],
            limit=num_questions  # Giới hạn số lượng kết quả
        )
        
        if not results:
            print("Không tìm thấy kết quả nào")
            return []
            
        print(f"Đã lấy được {len(results)} câu hỏi")
        return results
    except Exception as e:
        print(f"Lỗi khi lấy câu hỏi: {e}")
        return []

def generate_test_prompt(questions):
    """Tạo prompt cho LLM để tạo đề kiểm tra"""
    prompt = """Hãy tạo một đề kiểm tra toán lớp 1 từ các câu hỏi sau. 
    Chỉ trả về đề kiểm tra, không cần giải thích thêm.
    chỉ cần in đúng câu hỏi ra không cần thêm gì nữa
    Các câu hỏi:
    """
    
    for i, q in enumerate(questions, 1):
        prompt += f"\n{i}. {q['question']}"
    
    return prompt

def create_test_with_llm(questions):
    """Sử dụng Gemini để tạo đề kiểm tra"""
    try:
        prompt = generate_test_prompt(questions)
        
        # Khởi tạo model Gemini
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Tạo response
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                top_p=0.8,
                top_k=40
            )
        )
        
        return response.text
    except Exception as e:
        print(f"Lỗi khi tạo đề kiểm tra: {e}")
        return None

def save_test(test_content, filename="de_kiem_tra.txt"):
    """Lưu đề kiểm tra vào file"""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(test_content)
        print(f"Đã lưu đề kiểm tra vào file {filename}")
    except Exception as e:
        print(f"Lỗi khi lưu file: {e}")

def main():
    if not connect_to_milvus():
        return
    
    # Lấy tên collection
    collection_name = input("Nhập tên collection chứa dữ liệu câu hỏi: ")
    
    # Lấy số lượng câu hỏi muốn tạo
    num_questions = int(input("Nhập số lượng câu hỏi muốn tạo (mặc định 10): ") or "10")
    
    # Lấy câu hỏi ngẫu nhiên
    questions = get_random_questions(collection_name, num_questions)
    
    if not questions:
        print("Không thể lấy câu hỏi từ collection")
        return
    
    # Tạo đề kiểm tra
    test_content = create_test_with_llm(questions)
    
    if test_content:
        # Lưu đề kiểm tra
        save_test(test_content)
        
        # In đề kiểm tra ra màn hình
        print("\nĐề kiểm tra:")
        print(test_content)

if __name__ == "__main__":
    main() 