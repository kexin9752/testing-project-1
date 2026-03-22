from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserListResponse,
    BatchRequest, BatchResult
)

router = APIRouter(prefix="/users", tags=["Users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


@router.post("", response_model=UserResponse, status_code=201)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role.value,
        department_id=user_data.department_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("", response_model=UserListResponse)
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    department_id: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(User)

    if search:
        query = query.filter(
            (User.username.contains(search)) |
            (User.email.contains(search)) |
            (User.full_name.contains(search))
        )
    if department_id:
        query = query.filter(User.department_id == department_id)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    total = query.count()
    users = query.offset((page - 1) * page_size).limit(page_size).all()

    return UserListResponse(total=total, page=page, page_size=page_size, items=users)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: str, user_data: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_data.model_dump(exclude_unset=True)
    if "role" in update_data and update_data["role"]:
        update_data["role"] = update_data["role"].value

    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()


@router.post("/{user_id}/activate", response_model=UserResponse)
def activate_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = True
    db.commit()
    db.refresh(user)
    return user


@router.post("/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user


@router.post("/batch", response_model=BatchResult)
def batch_operations(batch: BatchRequest, db: Session = Depends(get_db)):
    results = []
    success_count = 0
    failed_count = 0

    for op in batch.operations:
        try:
            if op.action == "create":
                user = User(
                    username=op.data["username"],
                    email=op.data["email"],
                    hashed_password=hash_password(op.data["password"]),
                    full_name=op.data["full_name"],
                    role=op.data.get("role", "user")
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                results.append({"action": "create", "id": user.id, "status": "success"})
                success_count += 1

            elif op.action == "update":
                user = db.query(User).filter(User.id == op.id).first()
                if user:
                    for key, value in op.data.items():
                        if key != "password":
                            setattr(user, key, value)
                    db.commit()
                    results.append({"action": "update", "id": op.id, "status": "success"})
                    success_count += 1
                else:
                    results.append({"action": "update", "id": op.id, "status": "failed", "error": "Not found"})
                    failed_count += 1

            elif op.action == "delete":
                user = db.query(User).filter(User.id == op.id).first()
                if user:
                    db.delete(user)
                    db.commit()
                    results.append({"action": "delete", "id": op.id, "status": "success"})
                    success_count += 1
                else:
                    results.append({"action": "delete", "id": op.id, "status": "failed", "error": "Not found"})
                    failed_count += 1
        except Exception as e:
            db.rollback()
            results.append({"action": op.action, "id": op.id, "status": "failed", "error": str(e)})
            failed_count += 1

    return BatchResult(success_count=success_count, failed_count=failed_count, results=results)
