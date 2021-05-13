"""Module for containing the routes for the application."""
import functools
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Response, status

import application.models as models
import application.mongo as mongo

router = APIRouter()


@functools.lru_cache()
def base_uri():
    return os.getenv("BASE_URI")


def _add_hyper_link_to_book(book: Dict[str, Any]) -> Dict[str, Any]:
    book_id = book.pop("book_id")
    book["_link"] = f"{base_uri()}book/{book_id}"
    book["published_year"] = datetime.strftime(book["published_year"], "%Y")
    return book


async def get_book_by_id_if_in_db(book_id: str) -> Optional[Dict[str, Any]]:
    book = await mongo.BACKEND.get_single_book_by_id(book_id=book_id)
    return book if book is not None else None


async def get_book_by_name_if_in_db(name: str) -> Optional[Dict[str, Any]]:
    book = await mongo.BACKEND.get_single_book_by_name(book_name=name)
    return book if book is not None else None


@router.get("/books")
async def get_the_list_of_all_books() -> List[Dict[str, Any]]:
    all_books = [
        _add_hyper_link_to_book(book) for book in await mongo.BACKEND.get_all_books()
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

    book_in_db = await get_book_by_name_if_in_db(book_to_insert.get("name"))
    if book_in_db is None:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Sorry could not add book to db !!"}
    return _add_hyper_link_to_book(book_in_db)


@router.get("/book/{book_id}")
async def get_a_single_book(book_id: str, response: Response) -> Dict[str, Any]:
    book = await get_book_by_id_if_in_db(book_id=book_id)
    if book is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "No such book exist!!"}
    return _add_hyper_link_to_book(book)


@router.put("/book/{book_id}")
async def update_a_book(
    book_id: str, book: models.Book, response: Response
) -> Dict[str, Any]:
    if await get_book_by_id_if_in_db(book_id=book_id) is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "No such book exist!!"}
    await mongo.BACKEND.update_one_book(book_id=book_id, data=book.dict())
    return _add_hyper_link_to_book(await mongo.BACKEND.get_single_book(book_id=book_id))


@router.delete("/book/{book_id}")
async def delete_a_book(book_id: str, response: Response) -> Dict[str, Any]:
    if await get_book_by_id_if_in_db(book_id=book_id) is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "No such book exist!!"}
    await mongo.BACKEND.delete_one_book(book_id=book_id)
    return {"message": "Book deleted !!"}
