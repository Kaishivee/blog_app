from fastapi import APIRouter, Request, Form, Response, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from typing import Annotated
from models.post_user_model import Post
from sqlalchemy import insert, select, delete

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/posts/", response_class=HTMLResponse)
async def get_posts(request: Request, db: Annotated[Session, Depends(get_db)]):
    posts = db.scalars(select(Post)).all()
    return templates.TemplateResponse("page_blog.html", {"request": request, "posts": posts})


@router.post("/posts/", response_class=HTMLResponse)
async def create_post(request: Request, db: Annotated[Session, Depends(get_db)], content: str = Form(...)):
    new_post = Post(content=content)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    posts = db.scalars(select(Post)).all()
    return templates.TemplateResponse("page_blog.html", {"request": request, "posts": posts})


@router.get("/posts/{post_id}/edit", response_class=HTMLResponse)
async def edit_post(request: Request, post_id: int, db: Annotated[Session, Depends(get_db)]):
    post = db.query(Post).filter(Post.id == post_id).first()
    return templates.TemplateResponse("edit_post.html", {"request": request, "post": post})


@router.post("/posts/{post_id}/edit", response_class=RedirectResponse)
async def update_post(request: Request, post_id: int, db: Annotated[Session, Depends(get_db)],
                      content: str = Form(...)):
    post = db.query(Post).filter(Post.id == post_id).first()
    post.content = content
    db.commit()
    db.refresh(post)
    return RedirectResponse(url="/posts/", status_code=302)


@router.post("/posts/{post_id}/delete", response_class=RedirectResponse)
async def delete_post(request: Request, post_id: int, db: Annotated[Session, Depends(get_db)]):
    post = db.query(Post).filter(Post.id == post_id).first()
    db.delete(post)
    db.commit()
    return RedirectResponse(url="/posts/", status_code=302)
