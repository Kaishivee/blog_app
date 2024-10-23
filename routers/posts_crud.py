from fastapi import APIRouter, Request, Form, Response, Depends, Cookie, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from typing import Annotated, Optional
from models.post_user_model import Post, User
from sqlalchemy import select

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/posts/", response_class=HTMLResponse)
async def get_posts(request: Request, db: Annotated[Session, Depends(get_db)], user_id: Optional[int] = Cookie(None),
                    error_message: Optional[str] = None):
    posts = db.scalars(select(Post)).all()
    return templates.TemplateResponse("page_blog.html", {"request": request, "posts": posts, "user_id": user_id,
                                                         "error_message": error_message})


@router.post("/posts/", response_class=HTMLResponse)
async def create_post(request: Request, db: Annotated[Session, Depends(get_db)], content: str = Form(...),
                      user_id: Optional[int] = Cookie(None)):
    if user_id is None:
        error_message = "User ID cookie is missing"
        return templates.TemplateResponse("page_blog.html",
                                          {"request": request, "posts": db.scalars(select(Post)).all(),
                                           "user_id": user_id, "error_message": error_message})

    new_post = Post(content=content, user_id=user_id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    posts = db.scalars(select(Post).join(User)).all()
    return templates.TemplateResponse("page_blog.html", {"request": request, "posts": posts, "user_id": user_id})


@router.get("/posts/{post_id}/edit", response_class=HTMLResponse)
async def edit_post(request: Request, post_id: int, db: Annotated[Session, Depends(get_db)],
                    user_id: Optional[int] = Cookie(None)):
    if user_id is None:
        error_message = "User ID cookie is missing"
        return templates.TemplateResponse("page_blog.html",
                                          {"request": request, "posts": db.scalars(select(Post)).all(),
                                           "user_id": user_id, "error_message": error_message})

    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        error_message = "Post not found"
        return templates.TemplateResponse("page_blog.html",
                                          {"request": request, "posts": db.scalars(select(Post)).all(),
                                           "user_id": user_id, "error_message": error_message})
    if post.user_id != user_id:
        error_message = "You are not allowed to edit this post"
        return templates.TemplateResponse("page_blog.html",
                                          {"request": request, "posts": db.scalars(select(Post)).all(),
                                           "user_id": user_id, "error_message": error_message})

    return templates.TemplateResponse("edit_post.html", {"request": request, "post": post})


@router.post("/posts/{post_id}/edit", response_class=RedirectResponse)
async def update_post(request: Request, post_id: int, db: Annotated[Session, Depends(get_db)], content: str = Form(...),
                      user_id: Optional[int] = Cookie(None)):
    if user_id is None:
        error_message = "User ID cookie is missing"
        return templates.TemplateResponse("page_blog.html",
                                          {"request": request, "posts": db.scalars(select(Post)).all(),
                                           "user_id": user_id, "error_message": error_message})

    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        error_message = "Post not found"
        return templates.TemplateResponse("page_blog.html",
                                          {"request": request, "posts": db.scalars(select(Post)).all(),
                                           "user_id": user_id, "error_message": error_message})
    if post.user_id != user_id:
        error_message = "You are not allowed to edit this post"
        return templates.TemplateResponse("page_blog.html",
                                          {"request": request, "posts": db.scalars(select(Post)).all(),
                                           "user_id": user_id, "error_message": error_message})

    post.content = content
    db.commit()
    db.refresh(post)
    return RedirectResponse(url="/posts/", status_code=302)


@router.post("/posts/{post_id}/delete", response_class=HTMLResponse)
async def delete_post(request: Request, post_id: int, db: Annotated[Session, Depends(get_db)],
                      user_id: Optional[int] = Cookie(None)):
    if user_id is None:
        error_message = "User ID cookie is missing"
        posts = db.scalars(select(Post)).all()
        return templates.TemplateResponse("page_blog.html", {"request": request, "posts": posts, "user_id": user_id,
                                                             "error_message": error_message})

    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        error_message = "Post not found"
        posts = db.scalars(select(Post)).all()
        return templates.TemplateResponse("page_blog.html", {"request": request, "posts": posts, "user_id": user_id,
                                                             "error_message": error_message})
    if post.user_id != user_id:
        error_message = "You are not allowed to delete this post"
        posts = db.scalars(select(Post)).all()
        return templates.TemplateResponse("page_blog.html", {"request": request, "posts": posts, "user_id": user_id,
                                                             "error_message": error_message})

    db.delete(post)
    db.commit()
    posts = db.scalars(select(Post)).all()
    return templates.TemplateResponse("page_blog.html", {"request": request, "posts": posts, "user_id": user_id})
