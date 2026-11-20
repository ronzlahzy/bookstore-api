import json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

FILE_NAME = "books.json"

initial_books = [
    {
        "id": 1,
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "price": 35.0,
        "is_available": True,
    },
    {
        "id": 2,
        "title": "The Pragmatic Programmer",
        "author": "Andrew Hunt",
        "price": 42.5,
        "is_available": True,
    },
]


class BookSchema(BaseModel):
    title: str
    author: str
    price: float
    is_available: bool = True


def save_books():
    with open(FILE_NAME, "w") as f:
        json.dump(books, f, indent=4)


def load_books():
    try:
        with open(FILE_NAME, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        with open(FILE_NAME, "w") as f:
            json.dump(initial_books, f, indent=4)
        return list(initial_books)


books = load_books()


def find_book(book_id):
    for book in books:
        if book["id"] == book_id:
            return book
    return None


@app.get("/books", status_code=200)
def get_books(limit: int = 10):
    return books[:limit]


@app.get("/books/{book_id}", status_code=200)
def get_book(book_id: int):
    book = find_book(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.post("/books", status_code=201)
def add_book(data: BookSchema):
    if len(books) == 0:
        new_id = 1
    else:
        new_id = max(b["id"] for b in books) + 1

    new_book = {
        "id": new_id,
        "title": data.title,
        "author": data.author,
        "price": data.price,
        "is_available": data.is_available,
    }
    books.append(new_book)
    save_books()
    return new_book


@app.put("/books/{book_id}", status_code=200)
def update_book(book_id: int, data: BookSchema):
    book = find_book(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    book["title"] = data.title
    book["author"] = data.author
    book["price"] = data.price
    book["is_available"] = data.is_available
    save_books()
    return book


@app.delete("/books/{book_id}", status_code=200)
def delete_book(book_id: int):
    book = find_book(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    books.remove(book)
    save_books()
    return {"message": "Book deleted successfully"}
