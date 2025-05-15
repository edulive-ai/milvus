# Hệ thống Question-Answering Toán học sử dụng Vector Database

Đây là hệ thống Question-Answering chuyên về Toán học sử dụng Milvus (Vector Database) kết hợp với Google Gemini để tạo embeddings và tìm kiếm ngữ nghĩa.

## Tổng quan hệ thống

Hệ thống bao gồm các thành phần chính:

1. **Database Vector (Milvus)**: Lưu trữ vector embeddings của các câu hỏi và câu trả lời toán học
2. **API Embedding (Google Gemini)**: Tạo vector embeddings từ văn bản
3. **API RESTful (Flask)**: Cung cấp endpoints để tìm kiếm câu hỏi và câu trả lời

## Luồng xử lý

### Quá trình load dữ liệu:
1. Đọc dữ liệu từ file JSON (`data/math_qa_data.json`)
2. Tạo embeddings cho mỗi câu hỏi bằng API Gemini
3. Lưu trữ câu hỏi, câu trả lời và embeddings vào Milvus

### Quá trình tìm kiếm:
1. Nhận câu hỏi từ người dùng thông qua API
2. Tạo embedding cho câu hỏi đó bằng API Gemini
3. Thực hiện vector search trong Milvus để tìm các câu hỏi tương tự
4. Trả về câu hỏi và câu trả lời có độ tương đồng cao nhất

## Cài đặt

### Yêu cầu
- Python 3.8+
- Milvus Server
- API key Google Gemini

### Cài đặt thư viện
```bash
pip install -r requirements.txt
```

### Cấu hình
Tạo file `.env` trong thư mục gốc với nội dung:
```
# Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Milvus Configuration
MILVUS_HOST=localhost
MILVUS_PORT=19530
COLLECTION_NAME=math_qa_collection
```

## Cấu trúc thư mục

```
math_qa_embedding/
├── app.py              # API server Flask
├── config.py           # Cấu hình hệ thống
├── load_data.py        # Script load dữ liệu vào Milvus
├── requirements.txt    # Thư viện yêu cầu
├── data/               # Thư mục chứa dữ liệu
│   └── math_qa_data.json  # Dữ liệu về câu hỏi-trả lời
├── services/           # Các service
│   └── milvus_service.py  # Xử lý tương tác với Milvus
└── utils/              # Tiện ích
    └── embedding.py    # Tạo embeddings với Google Gemini
```

## Chi tiết kỹ thuật

### Vector Database (Milvus)

Milvus được sử dụng để lưu trữ và tìm kiếm vector embeddings. Milvus collection có cấu trúc:
- `id`: ID tự động tăng (primary key)
- `question`: Câu hỏi toán học
- `answer`: Câu trả lời tương ứng
- `embedding`: Vector embedding của câu hỏi (768 chiều)

Collection được tạo với index HNSW (Hierarchical Navigable Small World) để tối ưu hóa tìm kiếm gần đúng (ANN).

### Embedding (Google Gemini)

Chúng tôi sử dụng API Gemini của Google để tạo vector embeddings từ câu hỏi:
- Model: `models/embedding-001`
- Task type: `RETRIEVAL_QUERY` cho câu hỏi tìm kiếm
- Kích thước vector: 768 chiều

Quá trình tạo embedding được thực hiện trong `utils/embedding.py`, bao gồm:
- Tạo đơn lẻ với `get_embedding()`
- Tạo hàng loạt với `batch_get_embeddings()`

### API REST (Flask)

API server cung cấp các endpoints:
- `GET /health`: Kiểm tra trạng thái hoạt động
- `GET /initialize`: Khởi tạo kết nối với Milvus và load collection
- `POST /search`: Tìm kiếm câu hỏi và câu trả lời tương tự
- `GET /stats`: Lấy thống kê về collection

#### Chi tiết API /search:
- **Request**: 
  ```json
  {
    "query": "Tính 5 + 7 = ?",
    "top_k": 5
  }
  ```
- **Response**:
  ```json
  {
    "query": "Tính 5 + 7 = ?",
    "results": [
      {
        "question": "Tính 5 + 7 = ?",
        "answer": "5 + 7 = 12",
        "distance": 0.123
      },
      ...
    ],
    "status": "success"
  }
  ```

## Cách sử dụng

### Load dữ liệu

```bash
source venv/bin/activate  # Kích hoạt môi trường ảo
python load_data.py
```

### Chạy API server

```bash
source venv/bin/activate
python app.py
```

API server mặc định chạy ở địa chỉ http://localhost:5000

### Truy vấn API

```bash
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Bình có 2 quyển sách. Nam có 8 quyển sách. Hỏi hai bạn có tất cả bao nhiêu quyển sách?"}'
```

## Quy trình tối ưu hóa tìm kiếm

1. **Chuẩn hóa dữ liệu**: Đảm bảo câu hỏi được chuẩn hóa trước khi tạo embedding
2. **Vector similarity**: Sử dụng khoảng cách L2 (Euclidean) để đo độ tương đồng
3. **Index optimization**: Sử dụng tham số HNSW để tối ưu hóa tốc độ tìm kiếm
   - M = 8: Số lượng kết nối tối đa mỗi node
   - efConstruction = 64: Độ chính xác khi xây dựng index
   - ef = 64: Độ chính xác khi tìm kiếm

## Cải tiến trong tương lai

- Hỗ trợ nhiều ngôn ngữ
- Thêm khả năng tạo câu trả lời động từ LLM
- Tối ưu hóa hiệu suất bằng caching
- Cải thiện độ chính xác bằng cách tinh chỉnh tham số embedding

## Xử lý lỗi phổ biến

1. **Lỗi kết nối Milvus**: Đảm bảo Milvus server đang chạy và có thể truy cập
2. **Lỗi API Gemini**: Kiểm tra API key và tham số task_type
3. **Không tìm thấy kết quả**: Kiểm tra collection đã được loaded và có dữ liệu

## Hướng dẫn chi tiết các file và cách chạy

### 1. Cấu hình (`config.py`)

File này chứa các cấu hình chính của hệ thống:
```python
import os
from dotenv import load_dotenv

# Tải biến môi trường từ file .env
load_dotenv()

# Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your_gemini_api_key_here")

# Milvus Configuration
MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = int(os.getenv("MILVUS_PORT", 19530))
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "math_qa_collection")

# Vector dimensions cho embedding từ Gemini
EMBEDDING_DIM = 768
```

### 2. Tạo Embeddings (`utils/embedding.py`)

File này chứa các hàm để tạo vector embeddings:
```python
# Cấu hình API Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Tạo embedding cho một câu hỏi
def get_embedding(text):
    result = genai.embed_content(
        model=MODEL_NAME,
        content=text,
        task_type="RETRIEVAL_QUERY"
    )
    embedding = np.array(result["embedding"])
    return embedding

# Tạo embedding cho nhiều câu hỏi cùng lúc
def batch_get_embeddings(texts, batch_size=10):
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        batch_embeddings = []
        for text in batch:
            embedding = get_embedding(text)
            # ...
        all_embeddings.extend(batch_embeddings)
    return all_embeddings
```

### 3. Dịch vụ Milvus (`services/milvus_service.py`)

File này quản lý tương tác với Milvus Vector Database:
```python
class MilvusService:
    def __init__(self):
        # Khởi tạo kết nối với Milvus
        # ...
    
    def connect(self):
        # Kết nối đến Milvus server
        # ...
    
    def create_collection(self):
        # Tạo collection nếu chưa tồn tại
        # ...
    
    def insert_data(self, questions, answers, embeddings):
        # Thêm dữ liệu QA và embeddings vào Milvus
        # ...
    
    def search(self, query_embedding, top_k=5):
        # Tìm kiếm câu hỏi và câu trả lời tương tự
        # ...
```

### 4. Load dữ liệu (`load_data.py`)

File này đọc dữ liệu từ JSON, tạo embeddings và lưu vào Milvus:
```python
def process_data_to_milvus():
    # Khởi tạo kết nối
    milvus_service = MilvusService()
    milvus_service.connect()
    
    # Xóa collection cũ và tạo mới
    milvus_service.drop_collection()
    milvus_service.create_collection()
    
    # Load dữ liệu từ JSON
    qa_data = load_qa_data(data_path)
    questions = [item["question"] for item in qa_data]
    answers = [item["answer"] for item in qa_data]
    
    # Tạo embeddings
    question_embeddings = batch_get_embeddings(questions)
    
    # Lưu vào Milvus
    milvus_service.insert_data(questions, answers, question_embeddings)
```

**Cách chạy**: `python load_data.py`
- Thực hiện một lần khi khởi tạo hệ thống
- Thực hiện khi cập nhật dữ liệu mới

### 5. API Server (`app.py`)

File này cung cấp RESTful API cho người dùng:
```python
@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    query = data["query"]
    
    # Tạo embedding
    query_embedding = get_embedding(query)
    
    # Tìm kiếm trong Milvus
    results = milvus_service.search(query_embedding)
    
    return jsonify({
        "status": "success",
        "query": query,
        "results": results
    })
```

**Cách chạy**: `python app.py`
- Chạy liên tục để phục vụ API 
- Khởi động sau khi đã load dữ liệu

### Quy trình thực hiện đầy đủ

1. **Khởi tạo ban đầu**:
   ```bash
   # Cài đặt môi trường
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Tạo file .env với API key
   echo "GEMINI_API_KEY=your_key_here" > .env
   
   # Khởi động Milvus server (nếu chưa chạy)
   # ...
   
   # Load dữ liệu ban đầu
   python load_data.py
   
   # Khởi động API server
   python app.py
   ```

2. **Sử dụng hàng ngày** (sau khi đã setup):
   ```bash
   source venv/bin/activate
   python app.py
   ```

3. **Cập nhật dữ liệu**:
   ```bash
   source venv/bin/activate
   # Cập nhật file data/math_qa_data.json
   python load_data.py
   ```

## Nguồn và tài liệu tham khảo

- [Milvus Documentation](https://milvus.io/docs)
- [Google Generative AI Python SDK](https://ai.google.dev/tutorials/python_quickstart)
- [Flask Documentation](https://flask.palletsprojects.com/) 