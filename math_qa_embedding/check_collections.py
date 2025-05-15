from pymilvus import connections, Collection, utility
import sys
import os

# Thêm thư mục cha vào sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

def connect_to_milvus():
    """Kết nối đến Milvus server"""
    try:
        connections.connect(
            alias="default", 
            host='localhost', 
            port='19530'
        )
        print("Kết nối thành công đến Milvus!")
        return True
    except Exception as e:
        print(f"Lỗi kết nối: {e}")
        return False

def list_collections():
    """Liệt kê tất cả các collection trong Milvus"""
    try:
        collections = utility.list_collections()
        if not collections:
            print("Không có collection nào trong Milvus")
            return
        
        print("\nDanh sách các collection:")
        for collection in collections:
            print(f"\nCollection: {collection}")
            # Lấy thông tin chi tiết của collection
            coll = Collection(collection)
            coll.load()
            print(f"- Số lượng entities: {coll.num_entities}")
            print("- Schema:")
            for field in coll.schema.fields:
                print(f"  + {field.name}: {field.dtype}")
            
    except Exception as e:
        print(f"Lỗi khi liệt kê collections: {e}")

def main():
    if connect_to_milvus():
        list_collections()

if __name__ == "__main__":
    main() 