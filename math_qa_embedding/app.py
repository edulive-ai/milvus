from flask import Flask, request, jsonify
from services.milvus_service import MilvusService
from utils.embedding import get_embedding
import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai
from pymilvus import Collection
import json

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

app = Flask(__name__)
milvus_service = MilvusService()

@app.route('/health', methods=['GET'])
def health_check():
    """API kiểm tra trạng thái hoạt động."""
    return jsonify({"status": "ok", "message": "Service is running"}), 200

@app.route('/initialize', methods=['GET'])
def initialize():
    """API để khởi tạo kết nối với Milvus và load collection."""
    try:
        connected = milvus_service.connect()
        if not connected:
            return jsonify({"status": "error", "message": "Không thể kết nối với Milvus server"}), 500
        
        collection = milvus_service.create_collection()
        loaded = milvus_service.load_collection()
        
        stats = milvus_service.get_collection_stats()
        
        return jsonify({
            "status": "success", 
            "message": "Đã khởi tạo thành công",
            "stats": stats
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/search', methods=['POST'])
def search():
    """API tìm kiếm câu hỏi tương tự dựa trên embedding."""
    try:
        data = request.get_json()
        if not data or "query" not in data:
            return jsonify({"status": "error", "message": "Thiếu trường 'query' trong request"}), 400
        
        query = data["query"]
        top_k = data.get("top_k", 5)
        
        print(f"Đang tìm kiếm cho câu hỏi: {query}")
        
        # Tạo embedding cho câu hỏi
        query_embedding = get_embedding(query)
        
        if query_embedding is None:
            return jsonify({"status": "error", "message": "Không thể tạo embedding cho câu hỏi"}), 500
        
        print(f"Đã tạo embedding với shape: {query_embedding.shape}")
        
        # Tìm kiếm trong Milvus
        results = milvus_service.search(query_embedding, top_k=top_k)
        
        print(f"Kết quả tìm kiếm: {len(results)} kết quả")
        
        # Format kết quả với các trường mới
        formatted_results = []
        for result in results:
            formatted_result = {
                "question": result["question"],
                "answer": result["answer"],
                "chapter": result["chapter"],
                "lesson": result["lesson"],
                "image_url": result["image_url"],
                "difficulty": result["difficulty"],
                "similarity_score": 1 - result["distance"]  # Chuyển đổi distance thành similarity score
            }
            formatted_results.append(formatted_result)
        
        return jsonify({
            "status": "success",
            "query": query,
            "results": formatted_results
        }), 200
    except Exception as e:
        print(f"Lỗi khi tìm kiếm: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/stats', methods=['GET'])
def stats():
    """API lấy thống kê về collection."""
    try:
        connected = milvus_service.connect()
        if not connected:
            return jsonify({"status": "error", "message": "Không thể kết nối với Milvus server"}), 500
        
        stats = milvus_service.get_collection_stats()
        if stats is None:
            return jsonify({"status": "error", "message": "Collection không tồn tại"}), 404
        
        return jsonify({
            "status": "success",
            "stats": stats
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/chapters', methods=['GET'])
def get_chapters():
    """API lấy danh sách các chương."""
    try:
        connected = milvus_service.connect()
        if not connected:
            return jsonify({"status": "error", "message": "Không thể kết nối với Milvus server"}), 500
        
        # Lấy tất cả các chương từ collection
        results = milvus_service.collection.query(
            expr="chapter != ''",
            output_fields=["chapter"]
        )
        
        # Lấy danh sách chương duy nhất
        chapters = list(set(item["chapter"] for item in results))
        chapters.sort()  # Sắp xếp theo thứ tự
        
        return jsonify({
            "status": "success",
            "chapters": chapters
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/lessons', methods=['GET'])
def get_lessons():
    """API lấy danh sách các bài học theo chương."""
    try:
        chapter = request.args.get('chapter')
        if not chapter:
            return jsonify({"status": "error", "message": "Thiếu tham số 'chapter'"}), 400
        
        connected = milvus_service.connect()
        if not connected:
            return jsonify({"status": "error", "message": "Không thể kết nối với Milvus server"}), 500
        
        # Lấy tất cả các bài học của chương
        results = milvus_service.collection.query(
            expr=f"chapter == '{chapter}'",
            output_fields=["lesson"]
        )
        
        # Lấy danh sách bài học duy nhất
        lessons = list(set(item["lesson"] for item in results))
        lessons.sort()  # Sắp xếp theo thứ tự
        
        return jsonify({
            "status": "success",
            "chapter": chapter,
            "lessons": lessons
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/generate', methods=['POST'])
def generate_content():
    """API để tạo nội dung mới dựa trên yêu cầu của người dùng sử dụng LLM."""
    try:
        data = request.get_json()
        if not data or "query" not in data:
            return jsonify({"status": "error", "message": "Thiếu trường 'query' trong request"}), 400

        query = data["query"]
        print(f"Received query: {query}")  # Debug log
        
        # Kết nối đến Milvus
        connected = milvus_service.connect()
        if not connected:
            return jsonify({"status": "error", "message": "Không thể kết nối với Milvus server"}), 500

        # Lấy metadata options
        collection = Collection(milvus_service.collection_name)
        collection.load()
        
        # Lấy tất cả các chương
        chapters = collection.query(
            expr="chapter != ''",
            output_fields=["chapter"]
        )
        chapters = list(set(item["chapter"] for item in chapters))
        chapters.sort()
        
        # Lấy tất cả các bài học
        lessons = collection.query(
            expr="lesson != ''",
            output_fields=["lesson"]
        )
        lessons = list(set(item["lesson"] for item in lessons))
        lessons.sort()
        
        # Lấy tất cả các độ khó
        difficulties = collection.query(
            expr="difficulty != ''",
            output_fields=["difficulty"]
        )
        difficulties = list(set(item["difficulty"] for item in difficulties))
        difficulties.sort()
        
        metadata_options = {
            "chapters": chapters,
            "lessons": lessons,
            "difficulties": difficulties
        }

        # Lấy câu hỏi mẫu
        sample_questions = collection.query(
            expr="id >= 0",
            output_fields=["id", "question", "answer", "chapter", "lesson", "difficulty", "image_url"],
            limit=20
        )

        if not sample_questions:
            return jsonify({"status": "error", "message": "Không thể lấy câu hỏi mẫu từ collection"}), 500

        # Tạo prompt
        prompt = """Dựa trên các câu hỏi mẫu sau, hãy phân tích yêu cầu của người dùng và trả về kết quả phù hợp theo định dạng JSON.
        Có thể là một trong các loại sau:
        1. Đề kiểm tra đầy đủ (cho nhiều câu hỏi):
        {
            "questions": [
                {
                    "chuong": "Chương X: Tên chương",
                    "bai": "Bài Y: Tên bài",
                    "question": "Câu hỏi",
                    "answer": "Đáp án",
                    "image_link": "URL hình ảnh từ câu hỏi mẫu",
                    "difficulty": "Độ khó (dễ/trung bình/khó)"
                }
            ]
        }
        
        2. Câu hỏi đơn lẻ:
        {
            "question": "Câu hỏi",
            "answer": "Đáp án",
            "image_link": "URL hình ảnh từ câu hỏi mẫu"
        }
        
        3. Hình ảnh:
        {
            "question": "Câu hỏi",
            "image_link": "URL hình ảnh từ câu hỏi mẫu",
            "description": "Mô tả ngắn về hình ảnh"
        }
        
        Lưu ý: 
        - Luôn sử dụng URL hình ảnh từ các câu hỏi mẫu, không tự tạo URL mới
        - Nếu không có hình ảnh phù hợp, sử dụng URL từ câu hỏi mẫu có nội dung tương tự
        - Đảm bảo URL hình ảnh luôn tồn tại trong câu hỏi mẫu
        - Khi yêu cầu tạo nhiều câu hỏi, sử dụng format 1 với mảng questions
        - Đảm bảo các câu hỏi được tạo phù hợp với chương, bài và độ khó được yêu cầu
        
        Các chương có sẵn:
        """
        
        # Thêm danh sách các options
        for chapter in metadata_options["chapters"]:
            prompt += f"\n- {chapter}"
        
        prompt += "\n\nCác bài học có sẵn:"
        for lesson in metadata_options["lessons"]:
            prompt += f"\n- {lesson}"
        
        prompt += "\n\nCác độ khó có sẵn:"
        for difficulty in metadata_options["difficulties"]:
            prompt += f"\n- {difficulty}"
        
        prompt += "\n\nCác câu hỏi mẫu:"
        for i, q in enumerate(sample_questions, 1):
            prompt += f"\n{i}. {q['question']} (Đáp án: {q['answer']}, Hình ảnh: {q.get('image_url', 'Không có')})"
        
        # Thêm yêu cầu của người dùng
        prompt += f"\n\n{query}\n\nHãy phân tích yêu cầu trên và trả về kết quả phù hợp theo một trong các định dạng JSON đã cho. Chỉ trả về JSON, không cần giải thích thêm."

        print("Generated prompt:", prompt)  # Debug log

        # Khởi tạo model Gemini
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Tạo response
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                top_p=0.8,
                top_k=1
            )
        )

        print("Raw response:", response.text)  # Debug log

        # Parse JSON từ response
        try:
            response_text = response.text.strip()
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                return jsonify({"status": "error", "message": "Không tìm thấy JSON trong response"}), 500
                
            json_str = response_text[start_idx:end_idx]
            result_data = json.loads(json_str)
            
            return jsonify({
                "status": "success",
                "result": result_data
            }), 200
            
        except json.JSONDecodeError as e:
            print(f"JSON Parse Error: {str(e)}")  # Debug log
            print(f"Response text: {response_text}")  # Debug log
            return jsonify({"status": "error", "message": f"Lỗi khi parse JSON: {str(e)}"}), 500
            
    except Exception as e:
        print(f"Unexpected error: {str(e)}")  # Debug log
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    # Đảm bảo đã kết nối với Milvus và load collection
    print("Khởi tạo kết nối với Milvus...")
    connected = milvus_service.connect()
    if connected:
        milvus_service.create_collection()
        milvus_service.load_collection()
        
        # Lấy thống kê ban đầu
        stats = milvus_service.get_collection_stats()
        if stats:
            print(f"Collection {stats['name']} có {stats['row_count']} bản ghi")
        
        # Khởi động Flask server
        print("Khởi động API server...")
        app.run(host='0.0.0.0', port=5001, debug=True)
    else:
        print("Không thể kết nối với Milvus server. Hãy đảm bảo Milvus đang chạy.") 