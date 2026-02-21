from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.models.databases import get_db
from src.services import admin_services

router = APIRouter()


@router.get("/users")
async def get_users(
    email: str = Depends(admin_services.getCurrentAdmin), db: Session = Depends(get_db)
):
    users = admin_services.get_user_for_admin(db)
    return {"message": "Get users", "users": users}


@router.patch("/users/{user_id}/promote")
async def update_user(
    user_id: int,
    email: str = Depends(admin_services.getCurrentAdmin),
    db: Session = Depends(get_db),
):
    user = admin_services.user_promote(user_id, db)
    return {"message": user.email + " promoted to admin", "user": user}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    email: str = Depends(admin_services.getCurrentAdmin),
    db: Session = Depends(get_db),
):
    admin_services.delete_user(user_id, db)
    return {"message": "User deleted successfully"}
