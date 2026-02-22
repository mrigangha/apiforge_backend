from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.models.databases import get_db
from src.schemas.post_schemas import PostCreate, PostUpdate
from src.services import auth_service, post_services

router = APIRouter()


@router.post("/posts")
def create_post(
    post: PostCreate,
    user_email: int = Depends(auth_service.getCurrentUser),
    db: Session = Depends(get_db),
):
    post = post_services.create_post_for_user(user_email, post, db)
    return {"message": "Post created successfully", "post": post}


@router.get("/posts/{post_id}")
def get_post(
    post_id: int,
    user_email: str = Depends(auth_service.getCurrentUser),
    db: Session = Depends(get_db),
):
    post = post_services.get_post(user_email, post_id, db)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post retrieved successfully", "post": post}


@router.put("/posts/{post_id}")
def update_post(
    post_id: int,
    post: PostUpdate,
    user_email: str = Depends(auth_service.getCurrentUser),
    db: Session = Depends(get_db),
):
    post = post_services.update_post(user_email, post_id, post, db)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post updated successfully", "post": post}


@router.delete("/posts/{post_id}")
def delete_post(
    post_id: int,
    user_email: str = Depends(auth_service.getCurrentUser),
    db: Session = Depends(get_db),
):
    post = post_services.delete_post(user_email, post_id, db)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post deleted successfully", "post": post}


@router.get("/posts")
def get_posts(
    user_email: str = Depends(auth_service.getCurrentUser),
    db: Session = Depends(get_db),
):
    posts = post_services.get_all_posts(user_email, db)
    return {"message": "Posts retrieved successfully", "posts": posts}
