from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.member import Member
from app.models.loan import Loan, LoanStatus
from app.schemas.library import MemberCreate, MemberUpdate
from typing import Optional, List

class MemberService:
    @staticmethod
    def get_all(db: Session, search: Optional[str] = None) -> List[Member]:
        query = db.query(Member)
        if search:
            search_term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Member.full_name.ilike(search_term),
                    Member.code.ilike(search_term),
                    Member.email.ilike(search_term),
                    Member.phone.ilike(search_term)
                )
            )
        return query.order_by(Member.id.desc()).all()

    @staticmethod
    def get_by_id(db: Session, member_id: int) -> Optional[Member]:
        return db.query(Member).filter(Member.id == member_id).first()

    @staticmethod
    def get_by_code(db: Session, code: str) -> Optional[Member]:
        return db.query(Member).filter(Member.code == code.strip()).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[Member]:
        return db.query(Member).filter(Member.email == email.strip().lower()).first()

    @staticmethod
    def create(db: Session, member_in: MemberCreate) -> Member:
        if MemberService.get_by_code(db, member_in.code):
            raise ValueError(f"Mã độc giả '{member_in.code}' đã tồn tại!")
        if MemberService.get_by_email(db, str(member_in.email)):
            raise ValueError(f"Email '{member_in.email}' đã được đăng ký!")

        member = Member(
            code=member_in.code.strip().upper(),
            full_name=member_in.full_name.strip(),
            email=str(member_in.email).strip().lower(),
            phone=member_in.phone.strip() if member_in.phone else None,
            address=member_in.address.strip() if member_in.address else None,
            is_active=True
        )
        db.add(member)
        db.commit()
        db.refresh(member)
        return member

    @staticmethod
    def update(db: Session, member_id: int, member_in: MemberUpdate) -> Member:
        member = MemberService.get_by_id(db, member_id)
        if not member:
            raise ValueError("Không tìm thấy độc giả cần cập nhật!")

        if member_in.email:
            existing = MemberService.get_by_email(db, str(member_in.email))
            if existing and existing.id != member_id:
                raise ValueError(f"Email '{member_in.email}' đã được sử dụng bởi độc giả khác!")
            member.email = str(member_in.email).strip().lower()

        if member_in.full_name is not None:
            member.full_name = member_in.full_name.strip()
        if member_in.phone is not None:
            member.phone = member_in.phone.strip() if member_in.phone else None
        if member_in.address is not None:
            member.address = member_in.address.strip() if member_in.address else None
        if member_in.is_active is not None:
            member.is_active = member_in.is_active

        db.commit()
        db.refresh(member)
        return member

    @staticmethod
    def delete(db: Session, member_id: int) -> bool:
        member = MemberService.get_by_id(db, member_id)
        if not member:
            raise ValueError("Không tìm thấy độc giả cần xóa!")

        # Kiểm tra xem độc giả có phiếu mượn nào chưa hoàn tất trả không
        active_loans = db.query(Loan).filter(
            Loan.member_id == member_id,
            Loan.status != LoanStatus.RETURNED.value
        ).count()

        if active_loans > 0:
            raise ValueError(f"Không thể xóa độc giả đang có {active_loans} phiếu mượn sách chưa trả!")

        db.delete(member)
        db.commit()
        return True
