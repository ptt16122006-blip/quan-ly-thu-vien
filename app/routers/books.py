from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.book_service import BookService
from app.schemas.library import BookCreate, BookUpdate
from typing import Optional

router = APIRouter(prefix="/books", tags=["Books"])
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse)
def list_books(
    request: Request,
    search: Optional[str] = None,
    success: Optional[str] = None,
    error: Optional[str] = None,
    db: Session = Depends(get_db)
):
    books = BookService.get_all(db, search=search)
    return templates.TemplateResponse(request, "books/list.html", {
        "active_tab": "books",
        "books": books,
        "search_query": search,
        "success_msg": success,
        "error_msg": error
    })

@router.get("/create", response_class=HTMLResponse)
def show_create_book_form(request: Request):
    return templates.TemplateResponse(request, "books/form.html", {
        "active_tab": "books",
        "book": None,
        "is_edit": False
    })

@router.post("/create")
def create_book(
    request: Request,
    code: str = Form(...),
    isbn: str = Form(...),
    title: str = Form(...),
    author: str = Form(...),
    category: str = Form(...),
    publisher: Optional[str] = Form(None),
    publish_year: Optional[int] = Form(None),
    total_quantity: int = Form(1),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    try:
        book_in = BookCreate(
            code=code,
            isbn=isbn,
            title=title,
            author=author,
            category=category,
            publisher=publisher,
            publish_year=publish_year,
            total_quantity=total_quantity,
            description=description
        )
        BookService.create(db, book_in)
        return RedirectResponse(url="/books?success=Thêm+sách+thành+công!", status_code=303)
    except Exception as e:
        return templates.TemplateResponse(request, "books/form.html", {
            "active_tab": "books",
            "book": {
                "code": code,
                "isbn": isbn,
                "title": title,
                "author": author,
                "category": category,
                "publisher": publisher,
                "publish_year": publish_year,
                "total_quantity": total_quantity,
                "description": description
            },
            "is_edit": False,
            "error_msg": f"Lỗi khi thêm sách: {str(e)}"
        }, status_code=400)

@router.get("/{book_id}/edit", response_class=HTMLResponse)
def show_edit_book_form(book_id: int, request: Request, db: Session = Depends(get_db)):
    book = BookService.get_by_id(db, book_id)
    if not book:
        return RedirectResponse(url="/books?error=Không+tìm+thấy+sách!", status_code=303)
    return templates.TemplateResponse(request, "books/form.html", {
        "active_tab": "books",
        "book": book,
        "is_edit": True
    })

@router.post("/{book_id}/edit")
def edit_book(
    book_id: int,
    request: Request,
    title: str = Form(...),
    author: str = Form(...),
    category: str = Form(...),
    publisher: Optional[str] = Form(None),
    publish_year: Optional[int] = Form(None),
    total_quantity: int = Form(1),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    try:
        book_in = BookUpdate(
            title=title,
            author=author,
            category=category,
            publisher=publisher,
            publish_year=publish_year,
            total_quantity=total_quantity,
            description=description
        )
        BookService.update(db, book_id, book_in)
        return RedirectResponse(url="/books?success=Cập+nhật+sách+thành+công!", status_code=303)
    except Exception as e:
        book = BookService.get_by_id(db, book_id)
        return templates.TemplateResponse(request, "books/form.html", {
            "active_tab": "books",
            "book": book,
            "is_edit": True,
            "error_msg": f"Lỗi cập nhật: {str(e)}"
        }, status_code=400)

@router.post("/{book_id}/delete")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    try:
        BookService.delete(db, book_id)
        return RedirectResponse(url="/books?success=Xóa+sách+thành+công!", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/books?error={str(e)}", status_code=303)
