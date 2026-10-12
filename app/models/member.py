from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False) # Mã thẻ độc giả ví dụ: DG001
    full_name = Column(String(255), nullable=False)                    # Họ và tên
    email = Column(String(255), unique=True, index=True, nullable=False) # Email
    phone = Column(String(20), nullable=True)                          # Số điện thoại
    address = Column(String(255), nullable=True)                       # Địa chỉ
    is_active = Column(Boolean, default=True)                          # Trạng thái thẻ
    registered_at = Column(DateTime, default=datetime.utcnow)          # Ngày đăng ký
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Quan hệ với các phiếu mượn
    loans = relationship("Loan", back_populates="member", cascade="all, delete-orphan")
