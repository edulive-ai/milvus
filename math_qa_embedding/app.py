from flask import Flask, request, jsonify, render_template
from services.milvus_service import MilvusService
from utils.embedding import get_embedding
from utils.llm_functions import search_by_metadata, search_by_similarity, extract_metadata_from_query
import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai
from pymilvus import Collection
import json
import re

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

app = Flask(__name__, static_url_path='/static', static_folder='static')
milvus_service = MilvusService()

@app.route('/')
def index():
    return render_template('index.html')

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
    """API tìm kiếm câu hỏi tương tự dựa trên embedding và metadata."""
    try:
        data = request.get_json()
        if not data or "query" not in data:
            return jsonify({"status": "error", "message": "Thiếu trường 'query' trong request"}), 400
        
        query = data["query"]
        top_k = data.get("top_k", 5)
        
        # Các tham số tìm kiếm metadata
        chapter = data.get("chapter")  # Số chương
        lesson = data.get("lesson")    # Số bài
        difficulty = data.get("difficulty")  # Độ khó: "dễ", "trung bình", "khó"
        page = data.get("page")        # Số trang
        
        print(f"Đang tìm kiếm cho câu hỏi: {query}")
        print(f"Tham số tìm kiếm: chapter={chapter}, lesson={lesson}, difficulty={difficulty}, page={page}")
        
        # Kết nối đến Milvus
        connected = milvus_service.connect()
        if not connected:
            return jsonify({"status": "error", "message": "Không thể kết nối với Milvus server"}), 500

        # Xây dựng điều kiện tìm kiếm
        search_conditions = []
        
        if chapter:
            search_conditions.append(f"chapter like 'Chương {chapter}:%'")
            print(f"Tìm kiếm trong chương {chapter}")
            
        if lesson:
            search_conditions.append(f"lessons like '%Bài {lesson}:%'")
            print(f"Tìm kiếm trong bài {lesson}")
            
        if difficulty:
            search_conditions.append(f"difficulty == '{difficulty}'")
            print(f"Tìm kiếm độ khó: {difficulty}")

        if page:
            search_conditions.append(f"page == {page}")
            print(f"Tìm kiếm trang {page}")

        # Nếu có điều kiện metadata, tìm kiếm theo metadata
        if search_conditions:
            try:
                expr = " and ".join(search_conditions)
                print(f"Điều kiện tìm kiếm: {expr}")
                
                results = milvus_service.collection.query(
                    expr=expr,
                    output_fields=["grade", "chapter", "title", "lessons", "question", "answer", "image_question", "image_answer", "difficulty", "page"]
                )
                
                if results:
                    formatted_results = []
                    for result in results:
                        formatted_result = {
                            "grade": result["grade"],
                            "chapter": result["chapter"],
                            "title": result["title"],
                            "lessons": result["lessons"],
                            "question": result["question"],
                            "answer": result["answer"],
                            "image_question": result["image_question"],
                            "image_answer": result["image_answer"],
                            "difficulty": result["difficulty"],
                            "page": result["page"],
                            "similarity_score": 1.0  # Kết quả chính xác theo metadata
                        }
                        formatted_results.append(formatted_result)
                    
                    return jsonify({
                        "status": "success",
                        "query": query,
                        "results": formatted_results[:top_k] if top_k < len(formatted_results) else formatted_results
                    }), 200
            except Exception as e:
                print(f"Lỗi khi tìm kiếm theo metadata: {str(e)}")
        
        # Nếu không có điều kiện metadata, tìm kiếm theo embedding
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
                "grade": result["grade"],
                "chapter": result["chapter"],
                "title": result["title"],
                "lessons": result["lessons"],
                "question": result["question"],
                "answer": result["answer"],
                "image_question": result["image_question"],
                "image_answer": result["image_answer"],
                "difficulty": result["difficulty"],
                "page": result["page"],
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
            output_fields=["lessons"]
        )
        
        # Lấy danh sách bài học duy nhất
        lessons = list(set(item["lessons"] for item in results))
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
    """API để xử lý các yêu cầu tìm kiếm và truy vấn dữ liệu từ database."""
    try:
        data = request.get_json()
        if not data or "query" not in data:
            return jsonify({"status": "error", "message": "Thiếu trường 'query' trong request"}), 400

        query = data["query"]
        print(f"Received query: {query}")  # Debug log
        
        # Trích xuất metadata từ query
        metadata = extract_metadata_from_query(query)
        print(f"Extracted metadata: {metadata}")  # Debug log
        
        # Kiểm tra xem có ít nhất một điều kiện tìm kiếm không
        has_metadata = any([
            metadata.get("chapter"),
            metadata.get("lesson"),
            metadata.get("difficulty"),
            metadata.get("page")
        ])
        
        # Nếu có metadata, tìm kiếm theo metadata
        if has_metadata:
            results = search_by_metadata(
                chapter=metadata.get("chapter"),
                lesson=metadata.get("lesson"),
                difficulty=metadata.get("difficulty"),
                page=metadata.get("page"),
                top_k=metadata.get("top_k", 5)
            )
            
            if results["status"] == "success":
                return jsonify({
                    "status": "success",
                    "result": results["results"]
                }), 200
        
        # Nếu không tìm thấy theo metadata hoặc không có metadata, tìm kiếm theo nội dung
        results = search_by_similarity(query, top_k=metadata.get("top_k", 5))
        
        if results["status"] == "success":
            return jsonify({
                "status": "success",
                "result": results["results"]
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Không tìm thấy câu hỏi phù hợp trong database"
            }), 404
            
    except Exception as e:
        print(f"Unexpected error: {str(e)}")  # Debug log
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/search_by_metadata', methods=['POST'])
def search_by_metadata():
    """API tìm kiếm câu hỏi chỉ dựa trên metadata."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Thiếu dữ liệu trong request"}), 400
        
        # Các tham số tìm kiếm metadata
        grade = data.get("grade")      # Lớp
        chapter = data.get("chapter")  # Số chương
        lesson = data.get("lesson")    # Số bài
        difficulty = data.get("difficulty")  # Độ khó: "dễ", "trung bình", "khó"
        page = data.get("page")        # Số trang
        top_k = data.get("top_k", 10)  # Số lượng kết quả mỗi trang
        current_page = data.get("page", 1)  # Trang hiện tại
        
        print(f"Tham số tìm kiếm: grade={grade}, chapter={chapter}, lesson={lesson}, difficulty={difficulty}, page={page}")
        
        # Kết nối đến Milvus
        connected = milvus_service.connect()
        if not connected:
            return jsonify({"status": "error", "message": "Không thể kết nối với Milvus server"}), 500

        # Xây dựng điều kiện tìm kiếm
        search_conditions = []
        
        if grade:
            search_conditions.append(f"grade == '{grade}'")
            print(f"Tìm kiếm lớp {grade}")
            
        if chapter:
            search_conditions.append(f"chapter like '%{chapter}%'")
            print(f"Tìm kiếm trong chương {chapter}")
            
        if lesson:
            search_conditions.append(f"lessons like '%{lesson}%'")
            print(f"Tìm kiếm trong bài {lesson}")
            
        if difficulty:
            search_conditions.append(f"difficulty == '{difficulty}'")
            print(f"Tìm kiếm độ khó: {difficulty}")

        if page:
            search_conditions.append(f"page == {page}")
            print(f"Tìm kiếm trang {page}")

        try:
            # Lấy tổng số kết quả
            expr = " and ".join(search_conditions) if search_conditions else "grade != ''"
            print(f"Điều kiện tìm kiếm: {expr}")
            
            # Lấy kết quả với phân trang
            results = milvus_service.collection.query(
                expr=expr,
                output_fields=["grade", "chapter", "title", "lessons", "question", "answer", "image_question", "image_answer", "difficulty", "page"]
            )
            
            if results:
                # Tính toán phân trang
                total = len(results)
                start_idx = (current_page - 1) * top_k
                end_idx = start_idx + top_k
                paginated_results = results[start_idx:end_idx]
                
                formatted_results = []
                for result in paginated_results:
                    formatted_result = {
                        "grade": result["grade"],
                        "chapter": result["chapter"],
                        "title": result["title"],
                        "lessons": result["lessons"],
                        "question": result["question"],
                        "answer": result["answer"],
                        "image_question": result["image_question"],
                        "image_answer": result["image_answer"],
                        "difficulty": result["difficulty"],
                        "page": result["page"]
                    }
                    formatted_results.append(formatted_result)
                
                return jsonify({
                    "status": "success",
                    "results": formatted_results,
                    "total": total,
                    "current_page": current_page,
                    "per_page": top_k,
                    "total_pages": (total + top_k - 1) // top_k
                }), 200
            else:
                return jsonify({
                    "status": "error",
                    "message": "Không tìm thấy kết quả phù hợp"
                }), 404
                
        except Exception as e:
            print(f"Lỗi khi tìm kiếm theo metadata: {str(e)}")
            return jsonify({"status": "error", "message": str(e)}), 500
            
    except Exception as e:
        print(f"Lỗi không xác định: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/fetch_all_data', methods=['GET'])
@app.route('/fetch_all_data', methods=['GET'])
def fetch_all_data():
    """API để lấy tất cả dữ liệu từ Milvus."""
    try:
        print("=== Starting fetch_all_data ===")  # Debug log
        
        # Kết nối đến Milvus
        connected = milvus_service.connect()
        if not connected:
            print("ERROR: Cannot connect to Milvus")  # Debug log
            return jsonify({"status": "error", "message": "Không thể kết nối với Milvus server"}), 500

        print("Connected to Milvus successfully")  # Debug log

        # Lấy tất cả dữ liệu từ collection
        results = milvus_service.collection.query(
            expr="grade != ''",
            output_fields=["grade", "chapter", "title", "lessons", "question", "answer", "image_question", "image_answer", "difficulty", "page"]
        )

        print(f"Query returned {len(results)} results")  # Debug log

        if results:
            formatted_results = []
            for i, result in enumerate(results):
                try:
                    formatted_result = {
                        "grade": result.get("grade", ""),
                        "chapter": result.get("chapter", ""),
                        "title": result.get("title", ""),
                        "lessons": result.get("lessons", ""),
                        "question": result.get("question", ""),
                        "answer": result.get("answer", ""),
                        "image_question": result.get("image_question", ""),
                        "image_answer": result.get("image_answer", ""),
                        "difficulty": result.get("difficulty", ""),
                        "page": result.get("page", "")
                    }
                    formatted_results.append(formatted_result)
                except Exception as e:
                    print(f"Error formatting result {i}: {str(e)}")  # Debug log
                    continue

            print(f"Successfully formatted {len(formatted_results)} results")  # Debug log
            
            return jsonify({
                "status": "success",
                "results": formatted_results,
                "total": len(formatted_results)
            }), 200
        else:
            print("No results found")  # Debug log
            return jsonify({"status": "error", "message": "Không tìm thấy dữ liệu"}), 404

    except Exception as e:
        print(f"ERROR in fetch_all_data: {str(e)}")  # Debug log
        import traceback
        traceback.print_exc()  # Print full stack trace
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
        app.run(host='0.0.0.0', port=5001, debug=False)
    else:
        print("Không thể kết nối với Milvus server. Hãy đảm bảo Milvus đang chạy.") 