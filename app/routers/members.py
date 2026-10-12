from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.member_service import MemberService
from app.schemas.library import MemberCreate, MemberUpdate
from typing import Optional

router = APIRouter(prefix="/members", tags=["Members"])
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse)
def list_members(
    request: Request,
    search: Optional[str] = None,
    success: Optional[str] = None,
    error: Optional[str] = None,
    db: Session = Depends(get_db)
):
    members = MemberService.get_all(db, search=search)
    return templates.TemplateResponse(request, "members/list.html", {
        "active_tab": "members",
        "members": members,
        "search_query": search,
        "success_msg": success,
        "error_msg": error
    })

@router.get("/create", response_class=HTMLResponse)
def show_create_member_form(request: Request):
    return templates.TemplateResponse(request, "members/form.html", {
        "active_tab": "members",
        "member": None,
        "is_edit": False
    })

@router.post("/create")
def create_member(
    request: Request,
    code: str = Form(...),
    full_name: str = Form(...),
    email: str = Form(...),
    phone: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    try:
        member_in = MemberCreate(
            code=code,
            full_name=full_name,
            email=email,
            phone=phone,
            address=address
        )
        MemberService.create(db, member_in)
        return RedirectResponse(url="/members?success=Thêm+độc+giả+thành+công!", status_code=303)
    except Exception as e:
        return templates.TemplateResponse(request, "members/form.html", {
            "active_tab": "members",
            "member": {
                "code": code,
                "full_name": full_name,
                "email": email,
                "phone": phone,
                "address": address
            },
            "is_edit": False,
            "error_msg": f"Lỗi khi thêm độc giả: {str(e)}"
        }, status_code=400)

@router.get("/{member_id}/edit", response_class=HTMLResponse)
def show_edit_member_form(member_id: int, request: Request, db: Session = Depends(get_db)):
    member = MemberService.get_by_id(db, member_id)
    if not member:
        return RedirectResponse(url="/members?error=Không+tìm+thấy+độc+giả!", status_code=303)
    return templates.TemplateResponse(request, "members/form.html", {
        "active_tab": "members",
        "member": member,
        "is_edit": True
    })

@router.post("/{member_id}/edit")
def edit_member(
    member_id: int,
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    phone: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    is_active: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    try:
        member_in = MemberUpdate(
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            is_active=True if is_active == "true" else False
        )
        MemberService.update(db, member_id, member_in)
        return RedirectResponse(url="/members?success=Cập+nhật+thông+tin+thành+công!", status_code=303)
    except Exception as e:
        member = MemberService.get_by_id(db, member_id)
        return templates.TemplateResponse(request, "members/form.html", {
            "active_tab": "members",
            "member": member,
            "is_edit": True,
            "error_msg": f"Lỗi cập nhật: {str(e)}"
        }, status_code=400)

@router.post("/{member_id}/delete")
def delete_member(member_id: int, db: Session = Depends(get_db)):
    try:
        MemberService.delete(db, member_id)
        return RedirectResponse(url="/members?success=Xóa+độc+giả+thành+công!", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/members?error={str(e)}", status_code=303)
