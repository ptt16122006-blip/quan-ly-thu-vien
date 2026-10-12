from sqlalchemy.orm import Session
from datetime import datetime, date
import uuid
from typing import List, Optional, Dict, Any
from app.models.book import Book
from app.models.member import Member
from app.models.loan import Loan, LoanItem, LoanStatus
from app.schemas.library import LoanCreate

class LoanService:
    @staticmethod
    def update_overdue_statuses(db: Session) -> None:
        """Cập nhật trạng thái OVERDUE cho các phiếu mượn đã quá hạn trả"""
        now = datetime.utcnow()
        overdue_loans = db.query(Loan).filter(
            Loan.status == LoanStatus.BORROWED.value,
            Loan.due_date < now
        ).all()
        for loan in overdue_loans:
            loan.status = LoanStatus.OVERDUE.value
        if overdue_loans:
            db.commit()

    @staticmethod
    def get_all(db: Session, status: Optional[str] = None) -> List[Loan]:
        LoanService.update_overdue_statuses(db)
        query = db.query(Loan)
        if status:
            query = query.filter(Loan.status == status)
        return query.order_by(Loan.id.desc()).all()

    @staticmethod
    def get_by_id(db: Session, loan_id: int) -> Optional[Loan]:
        LoanService.update_overdue_statuses(db)
        return db.query(Loan).filter(Loan.id == loan_id).first()

    @staticmethod
    def create_loan(db: Session, member_id: int, due_date: date, items_data: List[Dict[str, int]], notes: Optional[str] = None) -> Loan:
        """
        Tạo phiếu mượn sử dụng Database Transaction:
        1. Kiểm tra độc giả tồn tại và thẻ đang hoạt động (is_active)
        2. Kiểm tra tồn kho của từng sách
        3. Giảm available_quantity của sách
        4. Tạo bản ghi Loan và các LoanItem
        Nếu có bất kỳ lỗi nào, rollback toàn bộ.
        """
        # 1. Kiểm tra độc giả
        member = db.query(Member).filter(Member.id == member_id).first()
        if not member:
            raise ValueError("Độc giả không tồn tại!")
        if not member.is_active:
            raise ValueError(f"Thẻ của độc giả '{member.full_name}' đang bị khóa hoặc hết hạn!")

        if not items_data:
            raise ValueError("Phiếu mượn phải có ít nhất 1 cuốn sách!")

        # Chuẩn hóa due_date sang datetime kết thúc ngày
        due_datetime = datetime.combine(due_date, datetime.max.time())
        now = datetime.utcnow()
        if due_datetime < now:
            raise ValueError("Hạn trả sách không thể ở trong quá khứ!")

        # Sinh mã phiếu mượn duy nhất
        unique_suffix = uuid.uuid4().hex[:6].upper()
        loan_code = f"PM-{datetime.utcnow().strftime('%Y%m%d')}-{unique_suffix}"

        try:
            loan = Loan(
                loan_code=loan_code,
                member_id=member_id,
                borrow_date=now,
                due_date=due_datetime,
                status=LoanStatus.BORROWED.value,
                notes=notes.strip() if notes else None
            )
            db.add(loan)
            db.flush() # Flush để lấy loan.id

            # Gom nhóm số lượng nếu cùng 1 sách xuất hiện nhiều lần
            aggregated_books: Dict[int, int] = {}
            for item in items_data:
                book_id = item["book_id"]
                qty = item.get("quantity", 1)
                if qty <= 0:
                    raise ValueError("Số lượng mượn phải lớn hơn 0!")
                aggregated_books[book_id] = aggregated_books.get(book_id, 0) + qty

            for book_id, qty in aggregated_books.items():
                # Khóa dòng (SELECT ... FOR UPDATE) để tránh race condition khi nhiều người mượn cùng lúc
                book = db.query(Book).filter(Book.id == book_id).with_for_update().first()
                if not book:
                    raise ValueError(f"Sách với ID={book_id} không tồn tại!")

                if book.available_quantity < qty:
                    raise ValueError(
                        f"Sách '{book.title}' chỉ còn {book.available_quantity} cuốn trong kho, không đủ để mượn {qty} cuốn!"
                    )

                # Giảm số lượng sách có sẵn
                book.available_quantity -= qty

                loan_item = LoanItem(
                    loan_id=loan.id,
                    book_id=book.id,
                    quantity=qty,
                    is_returned=0
                )
                db.add(loan_item)

            db.commit()
            db.refresh(loan)
            return loan
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def return_loan(db: Session, loan_id: int) -> Loan:
        """
        Trả toàn bộ sách trong phiếu mượn:
        - Kiểm tra phiếu mượn có đang ở trạng thái đã trả chưa (tránh trả 2 lần)
        - Tăng lại available_quantity cho các đầu sách tương ứng
        - Cập nhật return_date và status = RETURNED
        """
        loan = db.query(Loan).filter(Loan.id == loan_id).first()
        if not loan:
            raise ValueError("Không tìm thấy phiếu mượn!")

        if loan.status == LoanStatus.RETURNED.value:
            raise ValueError("Phiếu mượn này đã được trả sách trước đó rồi!")

        try:
            now = datetime.utcnow()
            for item in loan.items:
                if item.is_returned == 0:
                    book = db.query(Book).filter(Book.id == item.book_id).with_for_update().first()
                    if book:
                        # Cộng lại số lượng tồn kho
                        book.available_quantity = min(book.total_quantity, book.available_quantity + item.quantity)
                    item.is_returned = 1
                    item.returned_at = now

            loan.status = LoanStatus.RETURNED.value
            loan.return_date = now

            db.commit()
            db.refresh(loan)
            return loan
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def get_dashboard_stats(db: Session) -> Dict[str, Any]:
        """Thống kê tổng hợp số liệu cho Dashboard"""
        LoanService.update_overdue_statuses(db)

        total_books = db.query(Book).count()
        total_members = db.query(Member).count()

        # Số lượng sách đang mượn
        borrowed_loans_count = db.query(Loan).filter(Loan.status == LoanStatus.BORROWED.value).count()
        overdue_loans_count = db.query(Loan).filter(Loan.status == LoanStatus.OVERDUE.value).count()
        returned_loans_count = db.query(Loan).filter(Loan.status == LoanStatus.RETURNED.value).count()

        # Tính tổng số cuốn sách đang được độc giả giữ
        total_borrowed_books_count = 0
        active_items = db.query(LoanItem).join(Loan).filter(
            Loan.status.in_([LoanStatus.BORROWED.value, LoanStatus.OVERDUE.value]),
            LoanItem.is_returned == 0
        ).all()
        for item in active_items:
            total_borrowed_books_count += item.quantity

        return {
            "total_books": total_books,
            "total_members": total_members,
            "borrowed_loans_count": borrowed_loans_count,
            "overdue_loans_count": overdue_loans_count,
            "returned_loans_count": returned_loans_count,
            "total_borrowed_copies": total_borrowed_books_count,
        }
