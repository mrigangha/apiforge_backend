from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from src.models.databases import get_db
from src.models.user import User
from src.services.auth_service import getCurrentUser


def getCurrentAdmin(
    admin_email: str = Depends(getCurrentUser), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == admin_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Admin not found")

    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    return user


def get_user_for_admin(db: Session):
    users = db.query(User).filter(User.role != "admin").all()
    return users


def get_user_by_id(user_id: int, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def user_promote(user_id: int, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = "admin"
    db.commit()
    db.refresh(user)
    return user


def delete_user(user_id: int, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted"}
