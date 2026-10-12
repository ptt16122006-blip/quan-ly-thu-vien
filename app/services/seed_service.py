from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.book import Book
from app.models.member import Member
from app.models.loan import Loan, LoanItem, LoanStatus

def seed_initial_data(db: Session) -> bool:
    """Nạp dữ liệu mẫu ban đầu một cách an toàn (Idempotent: chỉ thêm khi chưa có)"""
    # 1. Thêm sách mẫu nếu bảng trống
    if db.query(Book).count() == 0:
        sample_books = [
            Book(
                code="BK-001",
                isbn="978-604-58-9123-1",
                title="Lập Trình Python Từ Cơ Bản Đến Nâng Cao",
                author="Nguyễn Văn An",
                category="Công nghệ thông tin",
                publisher="NXB Thông Tin và Truyền Thông",
                publish_year=2023,
                total_quantity=10,
                available_quantity=8,
                description="Giáo trình học Python hoàn chỉnh dành cho sinh viên và lập trình viên."
            ),
            Book(
                code="BK-002",
                isbn="978-604-77-4567-2",
                title="Kiến Trúc Microservices và Docker",
                author="Trần Minh Tuấn",
                category="Công nghệ thông tin",
                publisher="NXB Bách Khoa Hà Nội",
                publish_year=2024,
                total_quantity=5,
                available_quantity=4,
                description="Hướng dẫn thiết kế, đóng gói container và triển khai hệ thống lớn."
            ),
            Book(
                code="BK-003",
                isbn="978-604-98-3333-3",
                title="Thiết Kế Cơ Sở Dữ Liệu Quan Hệ với PostgreSQL",
                author="Lê Quang Đạo",
                category="Cơ sở dữ liệu",
                publisher="NXB Khoa Học Tự Nhiên",
                publish_year=2022,
                total_quantity=7,
                available_quantity=7,
                description="Phân tích chuẩn hóa, index, transaction và tối ưu hóa truy vấn."
            ),
            Book(
                code="BK-004",
                isbn="978-013-23-5088-4",
                title="Clean Code - Mã Sạch",
                author="Robert C. Martin",
                category="Kỹ nghệ phần mềm",
                publisher="Prentice Hall",
                publish_year=2008,
                total_quantity=6,
                available_quantity=6,
                description="Cẩm nang viết code dễ đọc, dễ bảo trì và chuẩn mực công nghiệp."
            ),
            Book(
                code="BK-005",
                isbn="978-604-56-7890-5",
                title="Giải Thuật và Cấu Trúc Dữ Liệu Thực Hành",
                author="Phạm Đình Nam",
                category="Khoa học máy tính",
                publisher="NXB Giáo Dục",
                publish_year=2021,
                total_quantity=8,
                available_quantity=8,
                description="Tổng hợp các cấu trúc dữ liệu kinh điển và thuật toán tìm kiếm, sắp xếp."
            )
        ]
        db.add_all(sample_books)
        db.commit()

    # 2. Thêm độc giả mẫu nếu bảng trống
    if db.query(Member).count() == 0:
        sample_members = [
            Member(
                code="DG-001",
                full_name="Nguyễn Văn A",
                email="nguyenvana@gmail.com",
                phone="0912345678",
                address="Quận 1, TP. Hồ Chí Minh",
                is_active=True
            ),
            Member(
                code="DG-002",
                full_name="Trần Thị Mai",
                email="tranthimai@outlook.com",
                phone="0987654321",
                address="Cầu Giấy, Hà Nội",
                is_active=True
            ),
            Member(
                code="DG-003",
                full_name="Lê Hoàng Long",
                email="lehoanglong@yahoo.com",
                phone="0905123987",
                address="Hải Châu, Đà Nẵng",
                is_active=True
            )
        ]
        db.add_all(sample_members)
        db.commit()

    # 3. Thêm một số phiếu mượn mẫu đại diện cho các trạng thái (Đang mượn, Quá hạn, Đã trả)
    if db.query(Loan).count() == 0:
        member1 = db.query(Member).filter(Member.code == "DG-001").first()
        member2 = db.query(Member).filter(Member.code == "DG-002").first()
        book1 = db.query(Book).filter(Book.code == "BK-001").first()
        book2 = db.query(Book).filter(Book.code == "BK-002").first()

        now = datetime.utcnow()

        if member1 and book1:
            # Phiếu 1: Đang mượn
            loan1 = Loan(
                loan_code="PM-SAMPLE-001",
                member_id=member1.id,
                borrow_date=now - timedelta(days=3),
                due_date=now + timedelta(days=7),
                status=LoanStatus.BORROWED.value,
                notes="Mượn nghiên cứu học kỳ"
            )
            db.add(loan1)
            db.flush()
            item1 = LoanItem(loan_id=loan1.id, book_id=book1.id, quantity=1, is_returned=0)
            db.add(item1)

        if member2 and book2:
            # Phiếu 2: Quá hạn
            loan2 = Loan(
                loan_code="PM-SAMPLE-002",
                member_id=member2.id,
                borrow_date=now - timedelta(days=20),
                due_date=now - timedelta(days=5),
                status=LoanStatus.OVERDUE.value,
                notes="Mượn làm đồ án tốt nghiệp"
            )
            db.add(loan2)
            db.flush()
            item2 = LoanItem(loan_id=loan2.id, book_id=book2.id, quantity=1, is_returned=0)
            db.add(item2)

        db.commit()
    return True
