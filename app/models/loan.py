from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum
from app.core.database import Base

class LoanStatus(str, enum.Enum):
    BORROWED = "BORROWED"  # Đang mượn
    RETURNED = "RETURNED"  # Đã trả
    OVERDUE = "OVERDUE"    # Quá hạn

class Loan(Base):
    """Phiếu mượn"""
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    loan_code = Column(String(50), unique=True, index=True, nullable=False) # Mã phiếu mượn ví dụ: PM-20261012-001
    member_id = Column(Integer, ForeignKey("members.id", ondelete="CASCADE"), nullable=False)
    borrow_date = Column(DateTime, default=datetime.utcnow, nullable=False)  # Ngày mượn
    due_date = Column(DateTime, nullable=False)                              # Hạn trả
    return_date = Column(DateTime, nullable=True)                           # Ngày trả thực tế
    status = Column(String(20), default=LoanStatus.BORROWED.value, nullable=False) # BORROWED, RETURNED, OVERDUE
    notes = Column(Text, nullable=True)                                     # Ghi chú
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Quan hệ
    member = relationship("Member", back_populates="loans")
    items = relationship("LoanItem", back_populates="loan", cascade="all, delete-orphan")


class LoanItem(Base):
    """Chi tiết sách mượn trong từng phiếu"""
    __tablename__ = "loan_items"

    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("loans.id", ondelete="CASCADE"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="RESTRICT"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)                  # Số lượng cuốn sách mượn
    is_returned = Column(Integer, default=0, nullable=False)                # 0: Chưa trả, 1: Đã trả
    returned_at = Column(DateTime, nullable=True)

    # Quan hệ
    loan = relationship("Loan", back_populates="items")
    book = relationship("Book", back_populates="loan_items")
