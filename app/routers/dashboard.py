from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.loan_service import LoanService
from app.services.seed_service import seed_initial_data
from typing import Optional

router = APIRouter(tags=["Dashboard"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
def dashboard(
    request: Request,
    success: Optional[str] = None,
    error: Optional[str] = None,
    db: Session = Depends(get_db)
):
    stats = LoanService.get_dashboard_stats(db)
    recent_loans = LoanService.get_all(db)[:5] # 5 phiếu mượn mới nhất

    return templates.TemplateResponse(request, "index.html", {
        "active_tab": "dashboard",
        "stats": stats,
        "recent_loans": recent_loans,
        "success_msg": success,
        "error_msg": error
    })

@router.get("/seed-data")
def trigger_seed(db: Session = Depends(get_db)):
    try:
        seed_initial_data(db)
        return RedirectResponse(url="/?success=Đã+nạp+dữ+liệu+mẫu+thành+công!", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/?error=Lỗi+nạp+dữ+liệu:+{str(e)}", status_code=303)
