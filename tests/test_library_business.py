import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import date, timedelta

from app.core.database import Base
from app.models.book import Book
from app.models.member import Member
from app.models.loan import Loan, LoanStatus
from app.schemas.library import BookCreate, BookUpdate, MemberCreate, MemberUpdate
from app.services.book_service import BookService
from app.services.member_service import MemberService
from app.services.loan_service import LoanService

# CSDL SQLite in-memory dùng riêng cho test độc lập và chạy siêu nhanh
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def db_session():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

# --- 1. TEST NGHIỆP VỤ SÁCH ---
def test_book_crud_and_validation(db_session):
    # Thêm sách
    book_in = BookCreate(
        code="TEST-B1",
        isbn="111-222-333",
        title="Lập Trình Python Test",
        author="Tác Giả A",
        category="CNTT",
        total_quantity=5
    )
    created = BookService.create(db_session, book_in)
    assert created.id is not None
    assert created.available_quantity == 5

    # Kiểm tra trùng mã sách
    with pytest.raises(ValueError, match="đã tồn tại"):
        BookService.create(db_session, book_in)

    # Cập nhật sách
    update_in = BookUpdate(title="Lập Trình Python Cập Nhật", total_quantity=8)
    updated = BookService.update(db_session, created.id, update_in)
    assert updated.title == "Lập Trình Python Cập Nhật"
    assert updated.total_quantity == 8
    assert updated.available_quantity == 8

    # Tìm kiếm
    results = BookService.get_all(db_session, search="Cập Nhật")
    assert len(results) == 1
    assert results[0].code == "TEST-B1"

# --- 2. TEST NGHIỆP VỤ ĐỘC GIẢ ---
def test_member_crud_and_validation(db_session):
    member_in = MemberCreate(
        code="TEST-M1",
        full_name="Nguyễn Văn Test",
        email="test@library.com",
        phone="0901234567"
    )
    member = MemberService.create(db_session, member_in)
    assert member.id is not None
    assert member.is_active is True

    # Trùng mã độc giả
    with pytest.raises(ValueError, match="đã tồn tại"):
        MemberService.create(db_session, member_in)

    # Cập nhật thông tin
    update_in = MemberUpdate(full_name="Nguyễn Văn Test Đổi Tên")
    updated = MemberService.update(db_session, member.id, update_in)
    assert updated.full_name == "Nguyễn Văn Test Đổi Tên"

# --- 3. TEST TRANSACTION MƯỢN TRẢ & KIỂM TRA TỒN KHO ---
def test_loan_borrow_and_return_flow(db_session):
    # Khởi tạo 1 độc giả và 1 cuốn sách có 2 cuốn
    member = MemberService.create(db_session, MemberCreate(
        code="M-LOAN", full_name="Độc Giả Mượn", email="borrower@gmail.com"
    ))
    book = BookService.create(db_session, BookCreate(
        code="B-LOAN", isbn="999-888-777", title="Sách Giới Hạn", author="Tác Giả B", category="Sách Giáo Khoa", total_quantity=2
    ))

    due_date = date.today() + timedelta(days=7)

    # Mượn 1 cuốn thành công
    loan = LoanService.create_loan(
        db=db_session,
        member_id=member.id,
        due_date=due_date,
        items_data=[{"book_id": book.id, "quantity": 1}],
        notes="Mượn thử nghiệm"
    )
    assert loan.status == LoanStatus.BORROWED.value
    # Sách trong kho phải giảm còn 1
    db_session.refresh(book)
    assert book.available_quantity == 1

    # Thử mượn thêm 2 cuốn (vượt quá tồn kho còn lại là 1) -> Phải ném ngoại lệ
    with pytest.raises(ValueError, match="chỉ còn 1 cuốn trong kho"):
        LoanService.create_loan(
            db=db_session,
            member_id=member.id,
            due_date=due_date,
            items_data=[{"book_id": book.id, "quantity": 2}]
        )

    # Trả sách thành công
    returned_loan = LoanService.return_loan(db_session, loan.id)
    assert returned_loan.status == LoanStatus.RETURNED.value
    assert returned_loan.return_date is not None

    # Tồn kho phải hồi phục về 2
    db_session.refresh(book)
    assert book.available_quantity == 2

    # Trả lại lần thứ 2 -> Phải báo lỗi không được trả nhiều lần
    with pytest.raises(ValueError, match="đã được trả sách trước đó rồi"):
        LoanService.return_loan(db_session, loan.id)
