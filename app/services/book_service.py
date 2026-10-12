from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.book import Book
from app.schemas.library import BookCreate, BookUpdate
from typing import Optional, List

class BookService:
    @staticmethod
    def get_all(db: Session, search: Optional[str] = None) -> List[Book]:
        query = db.query(Book)
        if search:
            search_term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Book.title.ilike(search_term),
                    Book.author.ilike(search_term),
                    Book.code.ilike(search_term),
                    Book.isbn.ilike(search_term),
                    Book.category.ilike(search_term)
                )
            )
        return query.order_by(Book.id.desc()).all()

    @staticmethod
    def get_by_id(db: Session, book_id: int) -> Optional[Book]:
        return db.query(Book).filter(Book.id == book_id).first()

    @staticmethod
    def get_by_code(db: Session, code: str) -> Optional[Book]:
        return db.query(Book).filter(Book.code == code.strip()).first()

    @staticmethod
    def get_by_isbn(db: Session, isbn: str) -> Optional[Book]:
        return db.query(Book).filter(Book.isbn == isbn.strip()).first()

    @staticmethod
    def create(db: Session, book_in: BookCreate) -> Book:
        # Kiểm tra trùng mã code hoặc isbn
        if BookService.get_by_code(db, book_in.code):
            raise ValueError(f"Mã sách '{book_in.code}' đã tồn tại!")
        if BookService.get_by_isbn(db, book_in.isbn):
            raise ValueError(f"Mã ISBN '{book_in.isbn}' đã tồn tại!")

        book = Book(
            code=book_in.code.strip().upper(),
            isbn=book_in.isbn.strip(),
            title=book_in.title.strip(),
            author=book_in.author.strip(),
            category=book_in.category.strip(),
            publisher=book_in.publisher.strip() if book_in.publisher else None,
            publish_year=book_in.publish_year,
            total_quantity=book_in.total_quantity,
            available_quantity=book_in.total_quantity, # Ban đầu số lượng còn = tổng số
            description=book_in.description
        )
        db.add(book)
        db.commit()
        db.refresh(book)
        return book

    @staticmethod
    def update(db: Session, book_id: int, book_in: BookUpdate) -> Book:
        book = BookService.get_by_id(db, book_id)
        if not book:
            raise ValueError("Không tìm thấy sách cần cập nhật!")

        # Tính toán lại available_quantity nếu total_quantity thay đổi
        if book_in.total_quantity is not None:
            borrowed_count = book.total_quantity - book.available_quantity
            if book_in.total_quantity < borrowed_count:
                raise ValueError(
                    f"Không thể giảm tổng số lượng xuống {book_in.total_quantity} vì hiện đang có {borrowed_count} cuốn đang được mượn!"
                )
            book.available_quantity = book_in.total_quantity - borrowed_count
            book.total_quantity = book_in.total_quantity

        if book_in.title is not None:
            book.title = book_in.title.strip()
        if book_in.author is not None:
            book.author = book_in.author.strip()
        if book_in.category is not None:
            book.category = book_in.category.strip()
        if book_in.publisher is not None:
            book.publisher = book_in.publisher.strip()
        if book_in.publish_year is not None:
            book.publish_year = book_in.publish_year
        if book_in.description is not None:
            book.description = book_in.description

        db.commit()
        db.refresh(book)
        return book

    @staticmethod
    def delete(db: Session, book_id: int) -> bool:
        book = BookService.get_by_id(db, book_id)
        if not book:
            raise ValueError("Không tìm thấy sách cần xóa!")

        borrowed_count = book.total_quantity - book.available_quantity
        if borrowed_count > 0:
            raise ValueError(f"Không thể xóa sách đang có {borrowed_count} lượt mượn chưa trả!")

        db.delete(book)
        db.commit()
        return True
