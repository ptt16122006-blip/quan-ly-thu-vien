from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.services.seed_service import seed_initial_data
from app.routers import books, members, loans, dashboard

# Quản lý vòng đời khởi động ứng dụng (Lifespan event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Tự động tạo bảng database nếu chưa tồn tại
    Base.metadata.create_all(bind=engine)
    
    # Nạp dữ liệu mẫu ban đầu nếu CSDL hoàn toàn trống
    db = SessionLocal()
    try:
        seed_initial_data(db)
    except Exception as e:
        print(f"Lưu ý: Không thể auto-seed dữ liệu: {e}")
    finally:
        db.close()
    
    yield

app = FastAPI(
    title=settings.APP_NAME,
    description="Ứng dụng Quản lý Thư viện - Môn Triển khai và Quản trị Hệ thống Phần mềm",
    version="1.0.0",
    lifespan=lifespan
)

# Phục vụ file tĩnh (CSS, JS)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

# Xử lý trang lỗi 404 thân thiện
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse(request, "404.html", status_code=404)
    return templates.TemplateResponse(request, "base.html", {
        "error_msg": f"Lỗi {exc.status_code}: {exc.detail}"
    }, status_code=exc.status_code)

# Đăng ký các Router nghiệp vụ
app.include_router(dashboard.router)
app.include_router(books.router)
app.include_router(members.router)
app.include_router(loans.router)
