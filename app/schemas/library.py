from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime, date

# --- SCHEMAS CHO SÁCH ---
class BookBase(BaseModel):
    code: str = Field(..., min_length=2, max_length=50, description="Mã sách duy nhất")
    isbn: str = Field(..., min_length=5, max_length=50, description="Mã ISBN")
    title: str = Field(..., min_length=1, max_length=255, description="Tên sách")
    author: str = Field(..., min_length=1, max_length=255, description="Tác giả")
    category: str = Field(..., min_length=1, max_length=100, description="Thể loại sách")
    publisher: Optional[str] = None
    publish_year: Optional[int] = Field(None, ge=1000, le=2100)
    total_quantity: int = Field(1, ge=0, description="Tổng số lượng sách")
    description: Optional[str] = None

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    publisher: Optional[str] = None
    publish_year: Optional[int] = Field(None, ge=1000, le=2100)
    total_quantity: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None

class BookResponse(BookBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    available_quantity: int
    created_at: datetime
    updated_at: datetime


# --- SCHEMAS CHO ĐỘC GIẢ ---
class MemberBase(BaseModel):
    code: str = Field(..., min_length=2, max_length=50, description="Mã thẻ độc giả")
    full_name: str = Field(..., min_length=2, max_length=255, description="Họ và tên")
    email: EmailStr = Field(..., description="Email hợp lệ")
    phone: Optional[str] = Field(None, max_length=20, description="Số điện thoại")
    address: Optional[str] = Field(None, max_length=255, description="Địa chỉ")

class MemberCreate(MemberBase):
    pass

class MemberUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None

class MemberResponse(MemberBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_active: bool
    registered_at: datetime


# --- SCHEMAS CHO MƯỢN TRẢ ---
class LoanItemCreate(BaseModel):
    book_id: int
    quantity: int = Field(1, ge=1, description="Số lượng mượn")

class LoanCreate(BaseModel):
    member_id: int
    due_date: date
    notes: Optional[str] = None
    items: List[LoanItemCreate] = Field(..., min_length=1, description="Danh sách sách cần mượn")
