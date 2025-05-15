from flask import Flask, request, jsonify
from services.milvus_service import MilvusService
from utils.embedding import get_embedding
import os

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
        
        return jsonify({
            "status": "success",
            "query": query,
            "results": results
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