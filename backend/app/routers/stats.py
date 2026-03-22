from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.user import User
from app.models.department import Department

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get("/users/count")
def get_user_count(db: Session = Depends(get_db)):
    total = db.query(User).count()
    active = db.query(User).filter(User.is_active == True).count()
    inactive = db.query(User).filter(User.is_active == False).count()

    return {
        "total": total,
        "active": active,
        "inactive": inactive
    }


@router.get("/departments/count")
def get_department_count(db: Session = Depends(get_db)):
    total = db.query(Department).count()
    return {"total": total}


@router.get("/system/info")
def get_system_info(db: Session = Depends(get_db)):
    user_count = db.query(User).count()
    dept_count = db.query(Department).count()

    return {
        "app_name": "User Management System",
        "version": "1.0.0",
        "database": "SQLite",
        "stats": {
            "users": user_count,
            "departments": dept_count
        }
    }
