import json
import os
from tqdm import tqdm
from utils.embedding import batch_get_embeddings
from services.milvus_service import MilvusService

def load_enhanced_qa_data(file_path):
    """Load dữ liệu câu hỏi và câu trả lời từ file JSON với cấu trúc mới."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def process_enhanced_data_to_milvus():
    """Xử lý dữ liệu có cấu trúc mới và lưu vào Milvus."""
    # Khởi tạo dịch vụ Milvus
    milvus_service = MilvusService()
    
    # Kết nối đến Milvus
    if not milvus_service.connect():
        print("Không thể kết nối với Milvus server. Hãy đảm bảo Milvus đang chạy.")
        return False
    
    # Xóa collection cũ và tạo mới để đảm bảo dữ liệu nhất quán
    print("Xóa collection cũ nếu có...")
    milvus_service.drop_collection()
    
    # Tạo collection mới với schema mới
    print("Tạo collection mới với schema mới...")
    milvus_service.create_collection()
    
    # Load dữ liệu
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "math_qa_data_v2.json")
    if not os.path.exists(data_path):
        print(f"File dữ liệu {data_path} không tồn tại. Hãy tạo dữ liệu trước.")
        return False
    
    qa_data = load_enhanced_qa_data(data_path)
    
    # Tách các trường dữ liệu
    questions = [item["question"] for item in qa_data]
    answers = [item["answer"] for item in qa_data]
    chapters = [item["chuong"] for item in qa_data]
    lessons = [item["bai"] for item in qa_data]
    image_links = [item["image_link"] for item in qa_data]
    difficulties = [item["difficulty"] for item in qa_data]
    
    print(f"Đã load {len(questions)} bản ghi dữ liệu")
    print(f"Số lượng chương: {len(set(chapters))}")
    print(f"Số lượng bài: {len(set(lessons))}")
    print(f"Số lượng link ảnh: {len(set(image_links))}")
    print(f"Số lượng độ khó: {len(set(difficulties))}")
    
    # Tạo embedding cho câu hỏi
    print("Đang tạo embeddings cho câu hỏi...")
    question_embeddings = batch_get_embeddings(questions)
    
    if len(question_embeddings) != len(questions):
        print(f"Cảnh báo: Số lượng embedding ({len(question_embeddings)}) không khớp với số lượng câu hỏi ({len(questions)})")
        # Điều chỉnh nếu cần
        min_length = min(len(question_embeddings), len(questions), len(answers))
        questions = questions[:min_length]
        answers = answers[:min_length]
        chapters = chapters[:min_length]
        lessons = lessons[:min_length]
        image_links = image_links[:min_length]
        difficulties = difficulties[:min_length]
        question_embeddings = question_embeddings[:min_length]
    
    # Insert vào Milvus với cấu trúc mới
    print("Đang lưu dữ liệu vào Milvus...")
    insert_result = milvus_service.insert_data(
        questions=questions,
        answers=answers,
        embeddings=question_embeddings,
        chapters=chapters,
        lessons=lessons,
        image_links=image_links,
        difficulties=difficulties
    )
    
    if insert_result:
        print(f"Đã lưu thành công {len(questions)} bản ghi vào Milvus")
        # Lấy thống kê
        stats = milvus_service.get_collection_stats()
        if stats:
            print(f"Số lượng bản ghi trong collection: {stats['row_count']}")
        return True
    else:
        print("Lưu dữ liệu thất bại")
        return False

if __name__ == "__main__":
    print("Bắt đầu quá trình load dữ liệu có cấu trúc mới vào Milvus...")
    process_enhanced_data_to_milvus()
    print("Hoàn thành") 