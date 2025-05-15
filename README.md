# Hướng dẫn cài đặt và chạy Milvus Standalone với Docker Compose

## Yêu cầu trước khi cài đặt

1. Đã cài đặt Docker
2. Đã cài đặt Docker Compose (V2 được khuyến nghị)
3. Ít nhất 2 CPU và 8GB RAM

## Các bước cài đặt

### 1. Tải file Docker Compose

```bash
wget https://github.com/milvus-io/milvus/releases/download/v2.5.10/milvus-standalone-docker-compose.yml -O docker-compose.yml
```

### 2. Khởi chạy Milvus

Tại thư mục chứa file `docker-compose.yml`, chạy lệnh:

```bash
sudo docker compose up -d
```

> **Lưu ý**: Nếu hệ thống của bạn sử dụng Docker Compose V1 thay vì V2, hãy sử dụng lệnh `sudo docker-compose up -d`

### 3. Kiểm tra trạng thái

Sau khi khởi chạy, bạn có thể kiểm tra trạng thái các container:

```bash
sudo docker compose ps
```

Kết quả sẽ hiển thị 3 container đang chạy:
- milvus-etcd
- milvus-minio
- milvus-standalone

Milvus sẽ phục vụ trên cổng 19530, và giao diện WebUI có thể truy cập tại http://localhost:9091/webui/

## Dừng và xóa Milvus

### Dừng dịch vụ

```bash
sudo docker compose down
```

### Xóa dữ liệu

```bash
sudo rm -rf volumes
```

## Thông tin thêm

- **Cấu trúc thư mục**: Dữ liệu sẽ được lưu trong thư mục `volumes` với các thư mục con:
  - `volumes/etcd`: Dữ liệu etcd
  - `volumes/minio`: Dữ liệu MinIO
  - `volumes/milvus`: Dữ liệu Milvus

- **Cổng mặc định**:
  - 19530: API Milvus
  - 9091: WebUI Milvus

## Tài liệu tham khảo

- [Tài liệu chính thức của Milvus](https://milvus.io/docs)
- [GitHub Milvus](https://github.com/milvus-io/milvus)
