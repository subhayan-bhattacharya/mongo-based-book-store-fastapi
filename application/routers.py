"""Module for containing the routes for the application."""
import functools
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter, Response, status

import application.models as models
import application.mongo as mongo

router = APIRouter()


@functools.lru_cache()
def base_uri():
    return os.getenv("BASE_URI")


def _modify_book_details(book: Dict[str, Any]) -> Dict[str, Any]:
    book_id = book.pop("book_id")
    book["_link"] = f"{base_uri()}book/{book_id}"
    book["published_year"] = datetime.strftime(book["published_year"], "%Y")
    return book


def _shorten_book_details(book: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'name': book.get("name"),
        'author': book.get("author"),
        '_link': f"{base_uri()}book/{book.get('book_id')}"
    }


@router.get("/authors")
async def get_all_authors() -> List[Dict[str, Any]]:
    return [doc['name'] for doc in await mongo.BACKEND.get_all_authors()]


@router.get("/genres")
async def get_all_authors() -> List[Dict[str, Any]]:
    return [doc['name'] for doc in await mongo.BACKEND.get_all_genres()]


@router.get("/books")
async def get_the_list_of_all_books() -> List[Dict[str, Any]]:
    all_books = [
        _shorten_book_details(book) for book in await mongo.BACKEND.get_all_books()
    ]
    return all_books


@router.post("/books", status_code=201)
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

    return _modify_book_details(
        await mongo.BACKEND.get_single_book_by_name(book_to_insert.get("name"))
    )


@router.get("/book/{book_id}")
async def get_a_single_book(book_id: str, response: Response) -> Dict[str, Any]:
    book = await mongo.BACKEND.get_single_book_by_id(book_id=book_id)
    if book is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "No such book exist!!"}
    return _modify_book_details(book)


@router.put("/book/{book_id}")
async def update_a_book(
    book_id: str, book: models.Book, response: Response
) -> Dict[str, Any]:
    book_in_db = await mongo.BACKEND.get_single_book_by_id(book_id=book_id)
    if book_in_db is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "No such book exist!!"}
    await mongo.BACKEND.update_one_book(book_id=book_id, data=book.dict())
    return _modify_book_details(await mongo.BACKEND.get_single_book_by_id(book_id=book_id))


@router.delete("/book/{book_id}")
async def delete_a_book(book_id: str, response: Response) -> Dict[str, Any]:
    book = await mongo.BACKEND.get_single_book_by_id(book_id=book_id)
    if book is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "No such book exist!!"}
    await mongo.BACKEND.delete_one_book(book_id=book_id)
    return {"message": "Book deleted !!"}
