from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models.post import Post
from src.models.user import User
from src.schemas.post_schemas import PostCreate, PostUpdate


def create_post_for_user(user_email: str, post_data: PostCreate, db: Session):
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    post = Post(title=post_data.title, content=post_data.content, owner_id=user.id)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def get_all_posts(user_email: str, db: Session):
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return db.query(Post).filter(Post.owner_id == user.id).all()


def get_post(user_email: str, post_id: int, db: Session):
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return db.query(Post).filter(Post.id == post_id, Post.owner_id == user.id).first()


def get_post_by_title(title: str, db: Session):
    return db.query(Post).filter(Post.title == title).first()


def update_post(user_email: str, post_id: int, post_data: PostUpdate, db: Session):
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    post = db.query(Post).filter(Post.id == post_id, Post.owner_id == user.id).first()
    if post:
        post.title = post_data.title
        post.content = post_data.content
        db.commit()
        db.refresh(post)
    return post


def delete_post(user_email: str, post_id: int, db: Session):
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    post = db.query(Post).filter(Post.id == post_id, Post.owner_id == user.id).first()
    if post:
        db.delete(post)
        db.commit()
    return post
