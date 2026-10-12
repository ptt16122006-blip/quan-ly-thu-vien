# Hướng Dẫn Vận Hành Hệ Thống Quản Lý Thư Viện

Đề tài: **Hệ thống Quản lý Thư viện**  
Môn học: **Triển khai và Quản trị Hệ thống Phần mềm**  
Công nghệ: **Python FastAPI, PostgreSQL, pgAdmin, Docker Compose**

---

## 1. Kiến Trúc & Cấu Trúc Dịch Vụ Docker

Toàn bộ hệ thống chạy tự động trong mạng Docker riêng biệt (`library_network`):

| Service | Container Name | Cổng Expose/Host | Mục Đích |
| :--- | :--- | :--- | :--- |
| **`app`** | `library_app` | `8000:8000` | Ứng dụng web FastAPI (Jinja2, HTML, CSS) |
| **`postgres`** | `library_postgres` | `5432` *(nội bộ)* | Cơ sở dữ liệu quan hệ PostgreSQL 16 Alpine |
| **`pgadmin`** | `library_pgadmin` | `5050:80` | Giao diện web quản trị cơ sở dữ liệu pgAdmin 4 |

---

## 2. Các Lệnh Điều Khiển Hệ Thống (Dành Cho Người Mới)

Mở PowerShell tại thư mục `c:\DU_AN\quan-ly-thu-vien`:

### Lệnh 1: Khởi động toàn bộ hệ thống
```powershell
docker compose up -d
```
> Hệ thống sẽ tự động khởi động PostgreSQL, kiểm tra healthcheck, khởi tạo tài khoản `library_user`, chạy ứng dụng FastAPI và pgAdmin.

### Lệnh 2: Kiểm tra trạng thái các container
```powershell
docker compose ps
```
> Trạng thái đạt yêu cầu: `library_postgres` báo `Up ... (healthy)`, `library_app` báo `Up`, `library_pgadmin` báo `Up`.

### Lệnh 3: Xem nhật ký (Logs) của hệ thống
- Xem log của ứng dụng web:
  ```powershell
  docker compose logs -f app
  ```
- Xem log của PostgreSQL:
  ```powershell
  docker compose logs -f postgres
  ```
- Xem log của pgAdmin:
  ```powershell
  docker compose logs -f pgadmin
  ```

### Lệnh 4: Dừng hệ thống an toàn (Không mất dữ liệu)
```powershell
docker compose stop
```
hoặc:
```powershell
docker compose down
```
> ⚠️ **Lưu ý quan trọng**: Không bao giờ thêm cờ `-v` (ví dụ `docker compose down -v`) vì cờ này sẽ xóa volume lưu trữ dữ liệu của CSDL!

### Lệnh 5: Khởi động lại hệ thống
```powershell
docker compose restart
```

---

## 3. Hướng Dẫn Truy Cập & Kiểm Thử Trên Trình Duyệt

1. **Ứng dụng Quản lý Thư viện**:
   - Địa chỉ: [http://localhost:8000](http://localhost:8000)
   - Chức năng: Dashboard, Quản lý Sách, Quản lý Độc Giả, Lập Phiếu Mượn & Trả Sách.

2. **Quản trị CSDL pgAdmin**:
   - Địa chỉ: [http://localhost:5050](http://localhost:5050)
   - Tài khoản đăng nhập:
     - **Email**: `admin@library.com`
     - **Password**: `admin_password_123`
   - Thông tin kết nối Server PostgreSQL:
     - **Host name/address**: `postgres` (Tên service trong Docker network)
     - **Port**: `5432`
     - **Maintenance database**: `library_db`
     - **Username**: `postgres` (Superuser) hoặc `library_user` (Tài khoản ứng dụng)
     - **Password**: `postgres_password_123` (cho postgres) hoặc `library_app_secure_pass_2026` (cho library_user)

---

## 4. Chạy Bộ Kiểm Thử Tự Động (Automated Tests)

Chạy bộ unit test bên trong container môi trường chuẩn:
```powershell
docker compose run --rm -e PYTHONPATH=/app -v ${PWD}/tests:/app/tests app pytest /app/tests -v
```
