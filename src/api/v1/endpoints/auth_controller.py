from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.models.databases import get_db
from src.schemas import auth_schemas
from src.services import auth_service

router = APIRouter()


@router.post("/register")
async def register(data: auth_schemas.RegisterData, db: Session = Depends(get_db)):
    auth_service.create_user(data, db)
    return {
        "message": "User registered successfully",
        "email": data.email,
    }


@router.post("/login")
async def login(data: auth_schemas.LoginData, db: Session = Depends(get_db)):
    user = auth_service.verify_user(data.email, data.password, db)
    access_token = auth_service.create_accesstoken(
        {"sub": data.email, "role": user.role}
    )
    response = JSONResponse(
        content={"access_token": access_token, "token_type": "bearer"}
    )
    refresh_token = auth_service.create_refreshtoken(
        {"sub": data.email, "role": user.role}
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=60 * 60,
        path="/",
    )
    return response


@router.post("/refresh")
async def refresh(user_email: str = Depends(auth_service.get_user_from_refresh_token)):
    access_token = auth_service.create_accesstoken({"sub": user_email})
    response = JSONResponse(
        content={"access_token": access_token, "token_type": "bearer"}
    )

    return response


@router.post("/logout")
async def logout(user_email: str = Depends(auth_service.getCurrentUser)):
    response = JSONResponse(content={"message": "Logged out successfully"})
    response.delete_cookie(key="refresh_token")
    return response


@router.get("/user")
async def get_user(
    user_email: str = Depends(auth_service.getCurrentUser),
    db: Session = Depends(get_db),
):
    user = auth_service.get_user_by_email(user_email, db)
    return {
        "message": "User retrieved successfully",
        "user": {"name": user.name, "email": user.email, "role": user.role},
    }
