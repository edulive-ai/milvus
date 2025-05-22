from services.milvus_service import MilvusService
from utils.embedding import get_embedding
import re

milvus_service = MilvusService()

def search_by_metadata(chapter=None, lesson=None, difficulty=None, page=None, top_k=5):
    """Tìm kiếm câu hỏi theo metadata."""
    try:
        # Kết nối đến Milvus
        connected = milvus_service.connect()
        if not connected:
            return {"status": "error", "message": "Không thể kết nối với Milvus server"}

        # Xây dựng điều kiện tìm kiếm
        search_conditions = []
        
        if chapter:
            search_conditions.append(f"chapter like '%Chương {chapter}%'")
            
        if lesson:
            search_conditions.append(f"lessons like '%Bài {lesson}%'")
            
        if difficulty:
            search_conditions.append(f"difficulty == '{difficulty}'")

        if page:
            search_conditions.append(f"page == {page}")

        # Kiểm tra xem có ít nhất một điều kiện metadata không
        if not search_conditions:
            return {"status": "error", "message": "Cần ít nhất một điều kiện tìm kiếm"}

        try:
            expr = " and ".join(search_conditions)
            
            # Thử tìm kiếm với điều kiện chính xác trước
            results = milvus_service.collection.query(
                expr=expr,
                output_fields=["grade", "chapter", "title", "lessons", "question", "answer", "image_question", "image_answer", "difficulty", "page"]
            )
            
            # Nếu không tìm thấy kết quả và đang tìm theo chương/bài, thử tìm kiếm linh hoạt hơn
            if not results and (chapter or lesson):
                flexible_conditions = []
                
                if chapter:
                    flexible_conditions.append(f"chapter like '%{chapter}%'")
                if lesson:
                    flexible_conditions.append(f"lessons like '%{lesson}%'")
                if difficulty:
                    flexible_conditions.append(f"difficulty == '{difficulty}'")
                if page:
                    flexible_conditions.append(f"page == {page}")
                
                flexible_expr = " and ".join(flexible_conditions)
                
                results = milvus_service.collection.query(
                    expr=flexible_expr,
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
                        "page": result["page"]
                    }
                    formatted_results.append(formatted_result)
                
                return {
                    "status": "success",
                    "results": formatted_results[:top_k] if top_k < len(formatted_results) else formatted_results
                }
            else:
                return {"status": "error", "message": "Không tìm thấy kết quả phù hợp"}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

def search_by_similarity(query, top_k=5):
    """Tìm kiếm câu hỏi tương tự dựa trên embedding."""
    try:
        # Kết nối đến Milvus
        connected = milvus_service.connect()
        if not connected:
            return {"status": "error", "message": "Không thể kết nối với Milvus server"}

        # Tạo embedding cho câu hỏi
        query_embedding = get_embedding(query)
        if query_embedding is None:
            return {"status": "error", "message": "Không thể tạo embedding cho câu hỏi"}

        # Tìm kiếm trong Milvus
        results = milvus_service.search(query_embedding, top_k=top_k)
        
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
                    "similarity_score": 1 - result["distance"]
                }
                formatted_results.append(formatted_result)
            
            return {
                "status": "success",
                "results": formatted_results
            }
        else:
            return {"status": "error", "message": "Không tìm thấy kết quả phù hợp"}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

def extract_metadata_from_query(query):
    """Trích xuất thông tin metadata từ câu query."""
    query_lower = query.lower()
    metadata = {}
    
    # Trích xuất số chương
    chapter_match = re.search(r'chương\s*(\d+)', query_lower)
    if chapter_match:
        metadata["chapter"] = int(chapter_match.group(1))
    
    # Trích xuất số bài
    lesson_match = re.search(r'bài\s*(\d+)', query_lower)
    if lesson_match:
        metadata["lesson"] = int(lesson_match.group(1))
    
    # Trích xuất độ khó
    difficulty_match = re.search(r'(dễ|trung bình|khó)', query_lower)
    if difficulty_match:
        metadata["difficulty"] = difficulty_match.group(1)
    
    # Trích xuất số trang
    page_match = re.search(r'trang\s*(\d+)', query_lower)
    if page_match:
        metadata["page"] = int(page_match.group(1))
    
    # Trích xuất số lượng câu hỏi
    num_match = re.search(r'(\d+)\s*câu', query_lower)
    if num_match:
        metadata["top_k"] = int(num_match.group(1))
    
    return metadata 