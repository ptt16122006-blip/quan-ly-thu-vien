FROM python:3.11-slim

# Thiết lập biến môi trường Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Cài đặt thư viện hệ thống cần thiết cho psycopg2 và curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Sao chép và cài đặt dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Tạo user và group non-root để chạy ứng dụng an toàn (Hardening Non-root)
RUN groupadd -g 10001 appuser && \
    useradd -u 10001 -g appuser -s /bin/sh -m appuser

# Sao chép toàn bộ mã nguồn với quyền sở hữu của appuser
COPY --chown=appuser:appuser . /app/app/

# Chuyển sang user non-root
USER appuser

# Khởi chạy uvicorn server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
