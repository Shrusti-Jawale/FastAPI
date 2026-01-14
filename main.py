from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from db import get_db, Base, engine
from schemas import UserRegister, UserLogin, BookCreate, Book
from services import (
    register_user,
    authenticate_user,
    create_book,
    get_books,
    get_book,
    update_book,
    delete_book
)
from auth import create_token, get_current_user

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    return register_user(db, user.username, user.password, user.role)


@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    auth_user = authenticate_user(db, user.username, user.password)
    if not auth_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token(auth_user.username)
    return {"token": token, "role": auth_user.role}


@app.get("/books/", response_model=list[Book])
def get_all_books(db: Session = Depends(get_db)):
    return get_books(db)


@app.get("/books/{id}", response_model=Book)
def get_single_book(id: int, db: Session = Depends(get_db)):
    book = get_book(db, id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.post("/books/", response_model=Book)
def create_book_api(
    book: BookCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role != "author":
        raise HTTPException(status_code=403, detail="Author access required")
    return create_book(db, book)


@app.put("/books/{id}", response_model=Book)
def update_book_api(
    id: int,
    book: BookCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role != "author":
        raise HTTPException(status_code=403, detail="Author access required")

    updated = update_book(db, book, id)
    if not updated:
        raise HTTPException(status_code=404, detail="Book not found")
    return updated


@app.delete("/books/{id}", response_model=Book)
def delete_book_api(
    id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role != "author":
        raise HTTPException(status_code=403, detail="Author access required")

    deleted = delete_book(db, id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Book not found")
    return deleted
