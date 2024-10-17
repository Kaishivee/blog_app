from fastapi import APIRouter, Depends, status, HTTPException, Path, Form, Request
from sqlalchemy.orm import Session
from typing import Annotated
from sqlalchemy import insert, select, delete
from fastapi.templating import Jinja2Templates
from database import get_db
from models.post_user_model import User
from schemas import CreateUser

from fastapi.responses import RedirectResponse, HTMLResponse

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(
        request: Request,
        email: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    if not user or user.password != password:  # In a real app, use secure password comparison
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    return RedirectResponse(url="/my_blog", status_code=302)


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("main_page.html", {"request": request})


@router.post("/create", response_model=None)
async def create_user(
        request: Request,
        db: Session = Depends(get_db),
        email: str = Form(...),
        password: str = Form(...)
):
    # Check if the user already exists
    db_user = db.query(User).filter(User.email == email).first()
    if db_user:
        return templates.TemplateResponse("main_page.html", {"request": request, "error": "Email already registered"})

    # Create a new user
    new_user = User(email=email, password=password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Redirect to login page after registration
    return RedirectResponse(url="/user/login", status_code=302)


@router.delete("/delete/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        user_id: int = Path(..., title="The ID of the user to delete"),
        db: Session = Depends(get_db)
):
    # Fetch the user from the database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Delete the user
    db.delete(user)
    db.commit()

    return {"detail": "User deleted successfully"}
