from sqlalchemy.orm import Session
from models import Book, User
from schemas import BookCreate
from auth import hash_password, verify_password


def register_user(db: Session, username: str, password: str, role: str):
    user = User(
        username=username,
        password=hash_password(password),
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password):
        return None
    return user


def create_book(db: Session, data: BookCreate):
    book = Book(**data.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def get_books(db: Session):
    return db.query(Book).all()


def get_book(db: Session, book_id: int):
    return db.query(Book).filter(Book.id == book_id).first()


def update_book(db: Session, book: BookCreate, book_id: int):
    book_db = db.query(Book).filter(Book.id == book_id).first()
    if book_db:
        for k, v in book.model_dump().items():
            setattr(book_db, k, v)
        db.commit()
        db.refresh(book_db)
    return book_db


def delete_book(db: Session, book_id: int):
    book_db = db.query(Book).filter(Book.id == book_id).first()
    if book_db:
        db.delete(book_db)
        db.commit()
    return book_db
