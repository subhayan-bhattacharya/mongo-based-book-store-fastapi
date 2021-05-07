"""Module for containing the routes for the application."""
import functools
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Tuple

from fastapi import APIRouter

import application.models as models
import application.mongo as mongo

router = APIRouter()


@functools.lru_cache()
def mongo_backend():
    return mongo.MongoBackend(uri=os.getenv("MONGODB_URI"))


@functools.lru_cache()
def base_uri():
    return os.getenv("BASE_URI")


def add_hyper_link_to_book(book: Dict[str, Any]) -> Dict[str, Any]:
    book_id = book.pop("book_id")
    book["_link"] = f"{base_uri()}book/{book_id}"
    book["published_year"] = datetime.strftime(book["published_year"], "%Y")
    return book


@router.get("/books")
async def get_all_books() -> List[Dict[str, Any]]:
    backend = mongo_backend()
    all_books = [add_hyper_link_to_book(book) for book in await backend.get_all_books()]
    return all_books


@router.post("/books", status_code=201)
async def add_a_book(book: models.Book) -> List[Dict[str, Any]]:
    backend = mongo_backend()
    book_to_insert = book.dict()
    book_to_insert["book_id"] = str(uuid.uuid1())
    await backend.insert_one_book(data=book_to_insert)
    return [add_hyper_link_to_book(book) for book in await backend.get_all_books()]


@router.get("/book/{book_id}")
async def get_a_single_book(book_id: str) -> Dict[str, Any]:
    backend = mongo_backend()
    book = await backend.get_single_book(book_id=book_id)
    if book is None:
        return {"message": "No such book exist!!"}
    return add_hyper_link_to_book(book)


@router.put("/book/{book_id}")
async def update_a_book(book_id: str, book: models.Book) -> Dict[str, Any]:
    backend = mongo_backend()
    book_in_db = await backend.get_single_book(book_id=book_id)
    if book_in_db is None:
        return {"message": "No such book exist!!"}
    await backend.update_one_book(book_id=book_id, data=book.dict())
    return add_hyper_link_to_book(await backend.get_single_book(book_id=book_id))


@router.delete("/book/{book_id}")
async def delete_a_book(book_id: str) -> Dict[str, Any]:
    backend = mongo_backend()
    if await backend.get_single_book(book_id=book_id) is None:
        return {"message": "No such book exist!!"}
    await backend.delete_one_book(book_id=book_id)
    return {"message": "Book deleted !!"}
