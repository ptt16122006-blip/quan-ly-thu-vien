# Hướng Dẫn Vận Hành Hệ Thống Quản Lý Thư Viện

Đề tài: **Hệ thống Quản lý Thư viện**  
Môn học: **Triển khai và Quản trị Hệ thống Phần mềm**  
Công nghệ: **Python FastAPI, PostgreSQL, pgAdmin, Nginx Reverse Proxy, Docker Compose**

---

## 1. Kiến Trúc & Cấu Trúc Dịch Vụ Docker

Hệ thống được thiết kế theo kiến trúc phân tầng an ninh với 3 mạng Docker bridge riêng biệt:
- **`frontend_network`**: Mạng ingress tiếp nhận request người dùng (kết nối `nginx` và `app`).
- **`backend_network`**: Mạng cô lập bảo vệ CSDL (kết nối `app`, `postgres`, `pgadmin`, `postgres_exporter`). Cổng 5432 hoàn toàn không expose ra ngoài.
- **`monitoring_network`**: Mạng giám sát nội bộ (kết nối `prometheus`, `grafana`, `loki`, `promtail`, `postgres_exporter`, `app`).

| Service | Container Name | Mạng Docker | Cổng Host | Cổng Nội Bộ | Mục Đích |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`nginx`** | `library_nginx` | `frontend_network` | `80`, `443` | `80`, `443` | **Reverse Proxy & SSL Termination**: Tiếp nhận request chính, điều hướng HTTP sang HTTPS, gắn security headers, định tuyến đến FastAPI app |
| **`app`** | `library_app` | `frontend`, `backend`, `monitoring` | *Không expose* | `8000` | Ứng dụng web FastAPI (Jinja2, HTML, CSS, `/metrics`) - Chạy non-root user `appuser` (UID 10001) |
| **`postgres`** | `library_postgres` | `backend_network` | *Không expose* | `5432` | Cơ sở dữ liệu PostgreSQL 16 Alpine - Bảo mật, chỉ kết nối nội bộ |
| **`pgadmin`** | `library_pgadmin` | `backend_network` | `5050` | `80` | Giao diện web quản trị cơ sở dữ liệu pgAdmin 4 |
| **`prometheus`** | `library_prometheus` | `monitoring_network` | `9090` | `9090` | Thu thập và lưu trữ metrics chuỗi thời gian (FastAPI, Postgres, Prometheus) |
| **`grafana`** | `library_grafana` | `monitoring_network` | `3000` | `3000` | Trực quan hóa dữ liệu giám sát và tra cứu log tập trung |
| **`postgres_exporter`** | `library_postgres_exporter` | `backend`, `monitoring` | *Không expose* | `9187` | Thu thập chỉ số hiệu năng CSDL PostgreSQL nội bộ |
| **`loki`** | `library_loki` | `monitoring_network` | *Không expose* | `3100` | Hệ thống lưu trữ và lập chỉ mục nhật ký (log) tập trung |
| **`promtail`** | `library_promtail` | `monitoring_network` | *Không expose* | `9080` | Thu thập log thực tế từ Docker containers qua socket và chuyển tiếp đến Loki |

---

## 2. Hướng Dẫn Tạo Chứng Chỉ SSL Demo (HTTPS Tự Ký)

Chứng chỉ SSL tự ký dùng cho môi trường thử nghiệm và phát triển được lưu trong thư mục `nginx/ssl/` (đã được cấu hình trong `.gitignore` để không bao giờ bị đưa lên Git).

Nếu bạn cần tạo mới hoặc tạo lại cặp chứng chỉ:
```powershell
docker run --rm -v ${PWD}/nginx/ssl:/certs alpine/openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /certs/selfsigned.key -out /certs/selfsigned.crt -subj "/C=VN/ST=HCM/L=HCM/O=Library/OU=IT/CN=localhost"
```

---

## 3. Các Lệnh Điều Khiển Hệ Thống

Mở **PowerShell** tại thư mục `c:\DU_AN\quan-ly-thu-vien`:

### Lệnh 1: Kiểm tra cú pháp cấu hình Docker Compose
```powershell
docker compose config
```

### Lệnh 2: Khởi động toàn bộ hệ thống
```powershell
docker compose up -d
```

### Lệnh 3: Kiểm tra trạng thái các container
```powershell
docker compose ps
```
> Trạng thái chuẩn:
> - `library_nginx`: `Up` (Cổng 80, 443)
> - `library_app`: `Up` (Cổng 8000 nội bộ)
> - `library_postgres`: `Up ... (healthy)` (Cổng 5432 nội bộ)
> - `library_pgadmin`: `Up` (Cổng 5050)

### Lệnh 4: Kiểm tra cú pháp file Nginx
```powershell
docker compose exec nginx nginx -t
```

### Lệnh 5: Xem nhật ký (Logs)
- Xem log Nginx:
  ```powershell
  docker compose logs -f nginx
  ```
- Xem log FastAPI App:
  ```powershell
  docker compose logs -f app
  ```

### Lệnh 6: Dừng hệ thống an toàn (Giữ nguyên dữ liệu)
```powershell
docker compose stop
```
hoặc:
```powershell
docker compose down
```
> ⚠️ **Tuyệt đối không dùng** `docker compose down -v` vì sẽ xóa volume dữ liệu của database!

---

## 4. Hướng Dẫn Truy Cập & Kiểm Thử Trên Trình Duyệt

1. **Truy cập Website Thư viện qua Nginx**:
   - Truy cập HTTP: **[http://localhost](http://localhost)** &rarr; Nginx tự động chuyển hướng (`301 Moved Permanently`) sang HTTPS.
   - Truy cập HTTPS: **[https://localhost](https://localhost)** (Bấm *Advanced / Nâng cao* &rarr; *Proceed to localhost / Tiếp tục* do chứng chỉ tự ký).
   - Kiểm tra các chức năng: Xem Dashboard, Tìm kiếm sách, Thêm/Sửa/Xóa sách, Thêm độc giả, Lập phiếu mượn và Trả sách.

2. **Quản trị CSDL qua pgAdmin**:
   - Địa chỉ: **[http://localhost:5050](http://localhost:5050)**
   - Đăng nhập:
     - **Email**: `admin@library.com`
     - **Password**: `admin_password_123`
   - Thông tin kết nối Server PostgreSQL:
     - **Host**: `postgres` (Tên service trong Docker network)
     - **Port**: `5432`
     - **Database**: `library_db`
     - **User**: `postgres` hoặc `library_user`

---

## 5. Security Headers Đã Được Thiết Lập Trong Nginx

- `X-Content-Type-Options: nosniff` (Chống MIME-type sniffing).
- `X-Frame-Options: SAMEORIGIN` (Chống Clickjacking).
- `Referrer-Policy: strict-origin-when-cross-origin` (Bảo mật referrer).
- `Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; connect-src 'self'; frame-ancestors 'self';` (Bảo vệ XSS mà không làm gián đoạn CSS/JS giao diện).
- `X-XSS-Protection: 1; mode=block` (Lọc XSS cho trình duyệt cũ).

---

## 6. Giám Sát (Prometheus & Grafana) & Quản Lý Log Tập Trung (Loki & Promtail)

### A. Truy cập giao diện giám sát & log
1. **Grafana Dashboard & Log Explorer**:
   - Địa chỉ: **[http://localhost:3000](http://localhost:3000)**
   - Tài khoản: `admin` / Mật khẩu: `admin`
   - **Dashboard Giám sát**: Vào Menu &rarr; **Dashboards** &rarr; thư mục **Library Management** &rarr; **Hệ Thống Quản Lý Thư Viện - Giám Sát Tổng Quan** (Hiển thị trạng thái services, latency, request rate, database size, connection pool).
   - **Tra cứu Log (Grafana Explore)**: Vào Menu &rarr; **Explore** &rarr; chọn Datasource **Loki**.
2. **Prometheus Web UI**:
   - Địa chỉ: **[http://localhost:9090](http://localhost:9090)**
   - Kiểm tra các targets thu thập metrics: Menu **Status** &rarr; **Targets** (Gồm: `fastapi_app`, `postgres`, `prometheus` đều ở trạng thái `UP`).

### B. 3 Câu truy vấn LogQL mẫu tra cứu Log thực tế trong Grafana Explore
1. **Truy vấn toàn bộ log của ứng dụng FastAPI**:
   ```logql
   {service="app"}
   ```
2. **Truy vấn log truy cập Nginx Reverse Proxy**:
   ```logql
   {service="nginx"}
   ```
3. **Lọc log nghiệp vụ có chứa phương thức HTTP GET**:
   ```logql
   {service="app"} |= "GET"
   ```

### C. Lưu ý kỹ thuật về Promtail (EOL)
> **Lưu ý đánh giá môn học:**  
> Promtail đã bước vào giai đoạn End-Of-Life (EOL) từ ngày 02/03/2026 và Grafana Labs khuyến nghị chuyển sang Grafana Alloy. Trong dự án này, Promtail được triển khai theo đúng chuẩn yêu cầu đề bài và rubric môn học (`grafana/promtail:3.0.0`), kết nối qua socket Docker để đọc log container thực tế và chuyển tiếp về Loki qua mạng nội bộ.
