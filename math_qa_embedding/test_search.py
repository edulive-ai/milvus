import requests
import json

def test_search_api():
    """Test API tìm kiếm câu hỏi tương tự."""
    base_url = "http://localhost:5000"
    
    # 1. Kiểm tra health
    health_response = requests.get(f"{base_url}/health")
    print(f"Health check: {health_response.status_code}")
    print(health_response.json())
    print("-" * 50)
    
    # 2. Khởi tạo kết nối với Milvus
    init_response = requests.get(f"{base_url}/initialize")
    print(f"Initialize: {init_response.status_code}")
    print(json.dumps(init_response.json(), indent=2, ensure_ascii=False))
    print("-" * 50)
    
    # 3. Lấy thống kê
    stats_response = requests.get(f"{base_url}/stats")
    print(f"Stats: {stats_response.status_code}")
    print(json.dumps(stats_response.json(), indent=2, ensure_ascii=False))
    print("-" * 50)
    
    # 4. Tìm kiếm các câu hỏi tương tự
    queries = [
        "Tính 5 + 7 = ?",
        "Tính 15 - 7 = ?",
        "So sánh 12 và 15",
        "Nam có 5 quả táo, được cho thêm 3 quả. Hỏi Nam có bao nhiêu quả táo?"
    ]
    
    for query in queries:
        search_data = {
            "query": query,
            "top_k": 3
        }
        
        search_response = requests.post(
            f"{base_url}/search",
            json=search_data
        )
        
        print(f"Search query '{query}': {search_response.status_code}")
        if search_response.status_code == 200:
            results = search_response.json()
            print(f"Câu hỏi tìm kiếm: {results['query']}")
            print("Kết quả tìm kiếm:")
            for i, result in enumerate(results["results"]):
                print(f"{i+1}. Q: {result['question']}")
                print(f"   A: {result['answer']}")
                print(f"   Độ tương đồng: {1 - result['distance']:.4f}")
            print("-" * 50)
        else:
            print(f"Lỗi: {search_response.json()}")
            print("-" * 50)

if __name__ == "__main__":
    print("Bắt đầu test API tìm kiếm...")
    test_search_api()
    print("Hoàn thành") 