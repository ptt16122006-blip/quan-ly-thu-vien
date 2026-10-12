from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.loan_service import LoanService
from app.services.book_service import BookService
from app.services.member_service import MemberService
from typing import Optional, List
from datetime import datetime, date, timedelta

router = APIRouter(prefix="/loans", tags=["Loans"])
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse)
def list_loans(
    request: Request,
    status: Optional[str] = None,
    success: Optional[str] = None,
    error: Optional[str] = None,
    db: Session = Depends(get_db)
):
    loans = LoanService.get_all(db, status=status)
    return templates.TemplateResponse(request, "loans/list.html", {
        "active_tab": "loans",
        "loans": loans,
        "status_filter": status,
        "success_msg": success,
        "error_msg": error
    })

@router.get("/create", response_class=HTMLResponse)
def show_create_loan_form(
    request: Request,
    error: Optional[str] = None,
    db: Session = Depends(get_db)
):
    members = MemberService.get_all(db)
    books = BookService.get_all(db)
    default_due_date = (date.today() + timedelta(days=14)).isoformat()

    return templates.TemplateResponse(request, "loans/form.html", {
        "active_tab": "loans",
        "members": members,
        "books": books,
        "default_due_date": default_due_date,
        "error_msg": error
    })

@router.post("/create")
def create_loan(
    request: Request,
    member_id: int = Form(...),
    due_date: str = Form(...),
    book_ids: List[int] = Form(...),
    quantities: List[int] = Form(...),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    try:
        parsed_due_date = datetime.strptime(due_date, "%Y-%m-%d").date()

        # Tạo danh sách các mặt hàng mượn
        items_data = []
        for b_id, qty in zip(book_ids, quantities):
            if b_id:
                items_data.append({"book_id": int(b_id), "quantity": int(qty)})

        LoanService.create_loan(
            db=db,
            member_id=member_id,
            due_date=parsed_due_date,
            items_data=items_data,
            notes=notes
        )
        return RedirectResponse(url="/loans?success=Tạo+phiếu+mượn+sách+thành+công!", status_code=303)
    except Exception as e:
        members = MemberService.get_all(db)
        books = BookService.get_all(db)
        default_due_date = due_date or (date.today() + timedelta(days=14)).isoformat()
        return templates.TemplateResponse(request, "loans/form.html", {
            "active_tab": "loans",
            "members": members,
            "books": books,
            "default_due_date": default_due_date,
            "error_msg": f"Không thể tạo phiếu mượn: {str(e)}"
        }, status_code=400)

@router.post("/{loan_id}/return")
def return_loan(loan_id: int, db: Session = Depends(get_db)):
    try:
        LoanService.return_loan(db, loan_id)
        return RedirectResponse(url="/loans?success=Đã+xác+nhận+trả+sách+thành+công!", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/loans?error={str(e)}", status_code=303)
