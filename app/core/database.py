from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# Engine kết nối CSDL
# echo=False khi production, thiết lập pool_pre_ping để tự reconnect khi mất kết nối
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency cung cấp db session cho mỗi request"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
