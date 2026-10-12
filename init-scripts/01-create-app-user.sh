#!/bin/bash
set -e

# Script khởi tạo người dùng ứng dụng với quyền tối thiểu (Non-superuser)
# Biến môi trường được truyền tự động từ Docker Compose:
# APP_DB_USER, APP_DB_PASSWORD, POSTGRES_DB

echo "Đang khởi tạo tài khoản ứng dụng với quyền tối thiểu: ${APP_DB_USER} trên CSDL: ${POSTGRES_DB}..."

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${APP_DB_USER}') THEN
            CREATE ROLE ${APP_DB_USER} WITH LOGIN PASSWORD '${APP_DB_PASSWORD}' NOSUPERUSER NOCREATEDB NOCREATEROLE;
            RAISE NOTICE 'Đã tạo tài khoản % thành công', '${APP_DB_USER}';
        ELSE
            ALTER ROLE ${APP_DB_USER} WITH LOGIN PASSWORD '${APP_DB_PASSWORD}' NOSUPERUSER NOCREATEDB NOCREATEROLE;
            RAISE NOTICE 'Tài khoản % đã tồn tại, đã cập nhật quyền hạn tối thiểu', '${APP_DB_USER}';
        END IF;
    END
    \$\$;

    -- Cấp quyền kết nối vào database
    GRANT CONNECT ON DATABASE ${POSTGRES_DB} TO ${APP_DB_USER};

    -- Cấp quyền trên schema public
    GRANT USAGE, CREATE ON SCHEMA public TO ${APP_DB_USER};

    -- Cấp quyền thao tác dữ liệu (SELECT, INSERT, UPDATE, DELETE) trên các bảng hiện tại
    GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ${APP_DB_USER};

    -- Cấp quyền trên các sequence (cho trường tự tăng ID serial/identity)
    GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO ${APP_DB_USER};

    -- Cấp quyền mặc định cho các bảng và sequence được tạo trong tương lai
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ${APP_DB_USER};
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT, UPDATE ON SEQUENCES TO ${APP_DB_USER};
EOSQL

echo "Hoàn tất phân quyền tối thiểu cho ${APP_DB_USER}!"
