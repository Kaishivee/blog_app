from fastapi import APIRouter, Depends, status, HTTPException, Path, Form, Request
from sqlalchemy.orm import Session
from typing import Annotated
from sqlalchemy import select
from fastapi.templating import Jinja2Templates
from database import get_db
from models.post_user_model import User
from passlib.context import CryptContext
from fastapi.responses import RedirectResponse, HTMLResponse

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == username).first()
    if not user or not pwd_context.verify(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

    response = RedirectResponse(url="/my_blog", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="user_id", value=str(user.id), httponly=True)
    return response


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("main_page.html", {"request": request})


@router.post("/create", response_model=None)
async def create_user(
        request: Request,
        db: Session = Depends(get_db),
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
):
    db_user = db.query(User).filter(User.email == email).first()
    if db_user:
        return templates.TemplateResponse("main_page.html", {"request": request, "error": "Email already registered"})

    db_username = db.query(User).filter(User.username == username).first()
    if db_username:
        return templates.TemplateResponse("main_page.html", {"request": request, "error": "Username already taken"})

    hashed_password = pwd_context.hash(password)
    new_user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return RedirectResponse(url="/user/login", status_code=302)


@router.delete("/delete/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        user_id: int = Path(..., title="The ID of the user to delete"),
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()
    return {"detail": "User deleted successfully"}