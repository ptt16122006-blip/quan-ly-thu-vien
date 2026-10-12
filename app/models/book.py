from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False) # Mã sách ví dụ: B001
    isbn = Column(String(50), unique=True, index=True, nullable=False) # Mã chuẩn quốc tế ISBN
    title = Column(String(255), index=True, nullable=False)           # Tên sách
    author = Column(String(255), index=True, nullable=False)          # Tác giả
    category = Column(String(100), index=True, nullable=False)        # Thể loại (CNTT, Văn học...)
    publisher = Column(String(255), nullable=True)                    # Nhà xuất bản
    publish_year = Column(Integer, nullable=True)                     # Năm xuất bản
    total_quantity = Column(Integer, nullable=False, default=1)       # Tổng số lượng
    available_quantity = Column(Integer, nullable=False, default=1)   # Số lượng còn trong kho
    description = Column(Text, nullable=True)                         # Tóm tắt/Mô tả
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Quan hệ với chi tiết mượn sách
    loan_items = relationship("LoanItem", back_populates="book", cascade="all, delete-orphan")
