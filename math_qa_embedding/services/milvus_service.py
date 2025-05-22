from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
)
import numpy as np
import time
import os
import sys

# Thêm thư mục cha vào sys.path để có thể import từ thư mục gốc
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from config import MILVUS_HOST, MILVUS_PORT, COLLECTION_NAME, EMBEDDING_DIM

class MilvusService:
    def __init__(self):
        self.host = MILVUS_HOST
        self.port = MILVUS_PORT
        self.collection_name = COLLECTION_NAME
        self.dim = EMBEDDING_DIM
        self.collection = None
        
    def connect(self):
        """Kết nối đến Milvus server."""
        try:
            connections.connect(
                alias="default", 
                host=self.host, 
                port=self.port
            )
            print(f"Kết nối thành công đến Milvus tại {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Lỗi khi kết nối đến Milvus: {e}")
            return False
    
    def create_collection(self):
        """Tạo collection cho dữ liệu QA nếu chưa tồn tại."""
        if utility.has_collection(self.collection_name):
            print(f"Collection {self.collection_name} đã tồn tại.")
            self.collection = Collection(self.collection_name)
            return self.collection
        
        # Định nghĩa schema cho collection với các trường mới
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="grade", dtype=DataType.VARCHAR, max_length=50),
            FieldSchema(name="chapter", dtype=DataType.VARCHAR, max_length=500),
            FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=1000),
            FieldSchema(name="lessons", dtype=DataType.VARCHAR, max_length=1000),
            FieldSchema(name="question", dtype=DataType.VARCHAR, max_length=1000),
            FieldSchema(name="answer", dtype=DataType.VARCHAR, max_length=1000),
            FieldSchema(name="image_question", dtype=DataType.VARCHAR, max_length=1000),
            FieldSchema(name="image_answer", dtype=DataType.VARCHAR, max_length=1000),
            FieldSchema(name="difficulty", dtype=DataType.VARCHAR, max_length=50),
            FieldSchema(name="page", dtype=DataType.INT64),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dim)
        ]
        
        schema = CollectionSchema(fields=fields, description="Math QA embeddings with enhanced fields")
        
        # Tạo collection
        self.collection = Collection(name=self.collection_name, schema=schema)
        
        # Tạo index cho vector search
        index_params = {
            "metric_type": "L2",
            "index_type": "HNSW",
            "params": {"M": 8, "efConstruction": 64}
        }
        
        self.collection.create_index(field_name="embedding", index_params=index_params)
        print(f"Đã tạo collection {self.collection_name} và index thành công")
        
        return self.collection
    
    def insert_data(self, questions, answers, embeddings, grades=None, chapters=None, titles=None, lessons=None, image_questions=None, image_answers=None, difficulties=None, pages=None):
        """Thêm dữ liệu QA và embeddings vào Milvus với các trường mới."""
        if self.collection is None:
            self.create_collection()
        
        # Chuyển embeddings về định dạng list
        if isinstance(embeddings, np.ndarray):
            embeddings = embeddings.tolist()
        
        # Chuẩn bị dữ liệu để insert
        data = [
            grades if grades else [""] * len(questions),
            chapters if chapters else [""] * len(questions),
            titles if titles else [""] * len(questions),
            lessons if lessons else [""] * len(questions),
            questions,
            answers,
            image_questions if image_questions else [""] * len(questions),
            image_answers if image_answers else [""] * len(questions),
            difficulties if difficulties else [""] * len(questions),
            pages if pages else [0] * len(questions),
            embeddings
        ]
        
        # In debug
        print(f"Số lượng questions: {len(questions)}")
        print(f"Số lượng answers: {len(answers)}")
        print(f"Số lượng grades: {len(grades) if grades else 0}")
        print(f"Số lượng chapters: {len(chapters) if chapters else 0}")
        print(f"Số lượng titles: {len(titles) if titles else 0}")
        print(f"Số lượng lessons: {len(lessons) if lessons else 0}")
        print(f"Số lượng image_questions: {len(image_questions) if image_questions else 0}")
        print(f"Số lượng image_answers: {len(image_answers) if image_answers else 0}")
        print(f"Số lượng difficulties: {len(difficulties) if difficulties else 0}")
        print(f"Số lượng pages: {len(pages) if pages else 0}")
        print(f"Số lượng embeddings: {len(embeddings)}")
        print(f"Kích thước embedding đầu tiên: {len(embeddings[0])}")
        
        # Insert dữ liệu
        try:
            insert_result = self.collection.insert(data)
            print(f"Đã insert {len(questions)} bản ghi vào Milvus")
            
            # Đảm bảo dữ liệu được lưu vào disk
            self.collection.flush()
            
            # Đảm bảo các index được xây dựng
            print("Đang xây dựng lại index...")
            index_params = {
                "metric_type": "L2",
                "index_type": "HNSW",
                "params": {"M": 8, "efConstruction": 64}
            }
            
            if not self.collection.has_index():
                self.collection.create_index(field_name="embedding", index_params=index_params)
            
            # Load collection vào memory để sẵn sàng tìm kiếm
            self.load_collection()
            
            return insert_result
        except Exception as e:
            print(f"Lỗi khi insert dữ liệu: {e}")
            return None
    
    def load_collection(self):
        """Load collection vào memory để tìm kiếm."""
        if self.collection is None:
            if utility.has_collection(self.collection_name):
                self.collection = Collection(self.collection_name)
            else:
                print(f"Collection {self.collection_name} không tồn tại")
                return False
        
        self.collection.load()
        print(f"Đã load collection {self.collection_name} vào memory")
        return True
    
    def search(self, query_embedding, top_k=5):
        """Tìm kiếm các câu hỏi và câu trả lời tương tự với embedding đầu vào."""
        if self.collection is None or not utility.has_collection(self.collection_name):
            print(f"Collection {self.collection_name} không tồn tại")
            return []
        
        try:
            # Luôn load collection trước khi tìm kiếm
            self.load_collection()
            
            # Chuyển embedding về list nếu là numpy array
            if isinstance(query_embedding, np.ndarray):
                query_embedding = query_embedding.tolist()
            
            # In thông tin debug
            print(f"Đang tìm kiếm trong collection {self.collection_name} với {self.collection.num_entities} entities")
            print(f"Kích thước vector embedding: {len(query_embedding)}")
            
            # Tìm kiếm với các tham số cụ thể hơn
            search_params = {
                "metric_type": "L2", 
                "params": {"ef": 64}  # Tăng ef lên để cải thiện độ chính xác
            }
            
            print(f"Tham số tìm kiếm: {search_params}")
            
            results = self.collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                output_fields=["grade", "chapter", "title", "lessons", "question", "answer", "image_question", "image_answer", "difficulty", "page"]
            )
            
            # Xử lý kết quả
            qa_results = []
            for hits in results:
                print(f"Tìm thấy {len(hits)} kết quả")
                for hit in hits:
                    qa_results.append({
                        "grade": hit.entity.get("grade"),
                        "chapter": hit.entity.get("chapter"),
                        "title": hit.entity.get("title"),
                        "lessons": hit.entity.get("lessons"),
                        "question": hit.entity.get("question"),
                        "answer": hit.entity.get("answer"),
                        "image_question": hit.entity.get("image_question"),
                        "image_answer": hit.entity.get("image_answer"),
                        "difficulty": hit.entity.get("difficulty"),
                        "page": hit.entity.get("page"),
                        "distance": hit.distance
                    })
            
            return qa_results
        
        except Exception as e:
            print(f"Lỗi khi tìm kiếm: {e}")
            return []
    
    def drop_collection(self):
        """Xóa collection."""
        if utility.has_collection(self.collection_name):
            utility.drop_collection(self.collection_name)
            print(f"Đã xóa collection {self.collection_name}")
            self.collection = None
            return True
        else:
            print(f"Collection {self.collection_name} không tồn tại")
            return False
    
    def get_collection_stats(self):
        """Lấy thông tin thống kê của collection."""
        if self.collection is None:
            if utility.has_collection(self.collection_name):
                self.collection = Collection(self.collection_name)
            else:
                print(f"Collection {self.collection_name} không tồn tại")
                return None
        
        row_count = self.collection.num_entities
        return {
            "name": self.collection_name,
            "row_count": row_count
        } 