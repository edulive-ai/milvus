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
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "toan-lop1-canh-dieu.json")
    if not os.path.exists(data_path):
        print(f"File dữ liệu {data_path} không tồn tại. Hãy tạo dữ liệu trước.")
        return False
    
    qa_data = load_enhanced_qa_data(data_path)
    
    # Tách các trường dữ liệu
    grades = [item["grade"] for item in qa_data]
    chapters = [item["chaper"] for item in qa_data]  # Note: using "chaper" as it's in the data
    titles = [item["title"] for item in qa_data]
    lessons = [item["lessons"] for item in qa_data]
    questions = [item["questions"] for item in qa_data]
    answers = [item["answers"] for item in qa_data]
    image_questions = [item["image_question"] for item in qa_data]
    image_answers = [item["image_answer"] for item in qa_data]
    difficulties = [item["difficulty"] for item in qa_data]
    pages = [item["page"] for item in qa_data]
    
    print(f"Đã load {len(questions)} bản ghi dữ liệu")
    print(f"Số lượng grade: {len(set(grades))}")
    print(f"Số lượng chapter: {len(set(chapters))}")
    print(f"Số lượng title: {len(set(titles))}")
    print(f"Số lượng lessons: {len(set(lessons))}")
    print(f"Số lượng image_question: {len(set(image_questions))}")
    print(f"Số lượng image_answer: {len(set(image_answers))}")
    print(f"Số lượng difficulty: {len(set(difficulties))}")
    print(f"Số lượng page: {len(set(pages))}")
    
    # Tạo embedding cho câu hỏi
    print("Đang tạo embeddings cho câu hỏi...")
    question_embeddings = batch_get_embeddings(questions)
    
    if len(question_embeddings) != len(questions):
        print(f"Cảnh báo: Số lượng embedding ({len(question_embeddings)}) không khớp với số lượng câu hỏi ({len(questions)})")
        # Điều chỉnh nếu cần
        min_length = min(len(question_embeddings), len(questions), len(answers))
        grades = grades[:min_length]
        chapters = chapters[:min_length]
        titles = titles[:min_length]
        lessons = lessons[:min_length]
        questions = questions[:min_length]
        answers = answers[:min_length]
        image_questions = image_questions[:min_length]
        image_answers = image_answers[:min_length]
        difficulties = difficulties[:min_length]
        pages = pages[:min_length]
        question_embeddings = question_embeddings[:min_length]
    
    # Insert vào Milvus với cấu trúc mới
    print("Đang lưu dữ liệu vào Milvus...")
    insert_result = milvus_service.insert_data(
        questions=questions,
        answers=answers,
        embeddings=question_embeddings,
        grades=grades,
        chapters=chapters,
        titles=titles,
        lessons=lessons,
        image_questions=image_questions,
        image_answers=image_answers,
        difficulties=difficulties,
        pages=pages
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