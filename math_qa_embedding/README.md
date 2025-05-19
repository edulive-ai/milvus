# Math QA Embedding Project

Dự án này sử dụng Milvus để lưu trữ và tìm kiếm các câu hỏi toán học dựa trên embedding, kết hợp với Gemini để tạo câu hỏi mới và tìm kiếm ngữ nghĩa.

## Cấu trúc thư mục

```
.
├── app.py                 # API server chính
├── config.py             # Cấu hình và biến môi trường
├── check_collections.py  # Công cụ kiểm tra collections trong Milvus
├── load_data.py         # Script load dữ liệu vào Milvus
├── data/                # Thư mục chứa dữ liệu
│   └── math_qa_data_v2.json  # Dữ liệu câu hỏi đã được xử lý
├── services/           # Các service
│   └── milvus_service.py  # Service tương tác với Milvus
└── utils/             # Các utility function
    └── embedding.py   # Hàm tạo embedding với Gemini
```

## Cài đặt

1. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

2. Cấu hình biến môi trường trong file `.env`:
```
MILVUS_HOST=localhost
MILVUS_PORT=19530
COLLECTION_NAME=math_qa_collection
GEMINI_API_KEY=your_gemini_api_key
```

## Sử dụng

### 1. Tạo dữ liệu câu hỏi
```bash
python data/generate_data_v2.py
```
Script này sẽ tạo 100 câu hỏi toán học với các thông tin:
- Chương và bài học
- Câu hỏi và đáp án
- Link hình ảnh minh họa
- Độ khó (dễ/trung bình/khó)

### 2. Load dữ liệu vào Milvus
```bash
python load_data.py
```
Script này sẽ:
- Kết nối với Milvus
- Tạo collection mới với schema phù hợp
- Tạo embeddings cho các câu hỏi
- Lưu dữ liệu vào Milvus

### 3. Kiểm tra collections
```bash
python check_collections.py
```
Công cụ này giúp:
- Liệt kê tất cả collections trong Milvus
- Hiển thị thông tin chi tiết về mỗi collection
- Kiểm tra số lượng entities và schema

### 4. Khởi động API server
```bash
python app.py
```

### Các API Endpoints

1. **Health Check**
```bash
GET /health
```

2. **Khởi tạo Collection**
```bash
GET /initialize
```

3. **Tìm kiếm câu hỏi tương tự**
```bash
POST /search
{
    "query": "Câu hỏi cần tìm kiếm",
    "top_k": 5
}
```

4. **Tạo câu hỏi mới với LLM**
```bash
POST /generate
{
    "query": "Yêu cầu tạo câu hỏi (ví dụ: tạo cho tôi 2 câu trong chương 1, bài số 1, độ khó dễ)"
}
```

5. **Xem thống kê**
```bash
GET /stats
```

6. **Lấy danh sách chương**
```bash
GET /chapters
```

7. **Lấy danh sách bài học theo chương**
```bash
GET /lessons?chapter=Chương 1
```

## Chi tiết kỹ thuật

### Vector Database (Milvus)
- Sử dụng HNSW index cho tìm kiếm vector
- Các tham số index:
  - M = 8: Số lượng kết nối tối đa mỗi node
  - efConstruction = 64: Độ chính xác khi xây dựng index
  - ef = 64: Độ chính xác khi tìm kiếm

### Embedding (Gemini)
- Model: `models/embedding-001`
- Task type: `RETRIEVAL_QUERY`
- Vector dimensions: 768
- Batch processing với delay 0.1s để tránh rate limit

### Schema Collection
```python
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="question", dtype=DataType.VARCHAR, max_length=500),
    FieldSchema(name="answer", dtype=DataType.VARCHAR, max_length=500),
    FieldSchema(name="chapter", dtype=DataType.VARCHAR, max_length=200),
    FieldSchema(name="lesson", dtype=DataType.VARCHAR, max_length=200),
    FieldSchema(name="image_url", dtype=DataType.VARCHAR, max_length=500),
    FieldSchema(name="difficulty", dtype=DataType.VARCHAR, max_length=50),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768)
]
```

## Lưu ý

- Đảm bảo Milvus server đang chạy trước khi khởi động ứng dụng
- Cần có API key của Gemini để sử dụng tính năng tạo câu hỏi mới và embedding
- Dữ liệu câu hỏi được lưu trong file `data/math_qa_data_v2.json`
- Khi tạo câu hỏi mới, hệ thống sẽ tự động chọn hình ảnh phù hợp từ các câu hỏi mẫu
- Độ khó của câu hỏi được xác định dựa trên loại câu hỏi và các tham số 