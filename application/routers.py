"""Module for containing the routes for the application."""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Response, status

import application.models as models
import application.mongo as mongo

router = APIRouter()


@router.get("/authors")
async def get_all_authors() -> List[Dict[str, Any]]:
    return [doc["name"] for doc in await mongo.BACKEND.get_all_authors()]


@router.get("/genres")
async def get_all_authors() -> List[Dict[str, Any]]:
    return [doc["name"] for doc in await mongo.BACKEND.get_all_genres()]


@router.get("/books", response_model=List[models.AllBooksResponse])
async def get_the_list_of_all_books(
    authors: Optional[str] = None,
    genres: Optional[str] = None,
    published_year: Optional[str] = None,
) -> List[Dict[str, Any]]:
    if authors is None and genres is None and published_year is None:
        all_books = [book for book in await mongo.BACKEND.get_all_books()]
    else:
        all_books = [
            book
            for book in await mongo.BACKEND.get_all_books(
                authors=authors.strip('"').split(",") if authors is not None else None,
                genres=genres.strip('"').split(",") if genres is not None else None,
                published_year=datetime.strptime(published_year, "%Y")
                if published_year is not None
                else None,
            )
        ]

    return all_books


@router.post("/books", response_model=models.SingleBookResponse, status_code=201)
async def add_a_book(book: models.Book, response: Response) -> Dict[str, Any]:
    book_to_insert = book.dict()
    book_to_insert["book_id"] = str(uuid.uuid1())

    try:
        await mongo.BACKEND.insert_one_book(data=book_to_insert)
    except mongo.BookExistsException:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": f"Book {book_to_insert.get('name')} already exists!!"}

    await mongo.BACKEND.insert_authors_in_db(book_to_insert.get("author"))
    await mongo.BACKEND.insert_genres_in_db(book_to_insert.get("genres"))

    return await mongo.BACKEND.get_single_book_by_name(book_to_insert.get("name"))


@router.get("/book/{book_id}", response_model=models.SingleBookResponse)
async def get_a_single_book(book_id: str, response: Response) -> Dict[str, Any]:
    book = await mongo.BACKEND.get_single_book_by_id(book_id=book_id)
    if book is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "No such book exist!!"}
    return book


@router.put("/book/{book_id}", response_model=models.SingleBookResponse)
async def update_a_book(
    book_id: str, book: models.Book, response: Response
) -> Dict[str, Any]:
    book_in_db = await mongo.BACKEND.get_single_book_by_id(book_id=book_id)
    if book_in_db is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "No such book exist!!"}
    await mongo.BACKEND.update_one_book(book_id=book_id, data=book.dict())
    return await mongo.BACKEND.get_single_book_by_id(book_id=book_id)


@router.delete("/book/{book_id}")
async def delete_a_book(book_id: str, response: Response) -> Dict[str, Any]:
    book = await mongo.BACKEND.get_single_book_by_id(book_id=book_id)
    if book is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "No such book exist!!"}
    await mongo.BACKEND.delete_one_book(book_id=book_id)
    return {"message": "Book deleted !!"}
