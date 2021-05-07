"""Module for containing the routes for the application."""
import uuid
from typing import Dict, Any, Tuple, List

from fastapi import APIRouter
import application.models as models
import application.mongo as mongo
import os
import functools


router = APIRouter()


@functools.lru_cache()
def mongo_backend():
    return mongo.MongoBackend(uri=os.getenv("MONGODB_URI"))


@functools.lru_cache()
def base_uri():
    return os.getenv("BASE_URI")


def add_hyper_link_to_book(book: Dict[str, Any]) -> Dict[str, Any]:
    book_id = book.pop("book_id")
    book["_link"] = f"{base_uri()}/book/{book_id}"
    return book


@router.get("/books")
async def get_all_books():
    backend = mongo_backend()
    print(id(backend))
    all_books = [
        add_hyper_link_to_book(book)
        for book in await backend.get_all_books()
    ]
    return all_books


@router.post("/books")
async def post(book: models.Book) -> Tuple[List[Dict[str, Any]], int]:
    backend = mongo_backend()
    book_to_insert = book.dict()
    book_to_insert["book_id"] = str(uuid.uuid1())
    await  backend.insert_one_book(data=book_to_insert)
    return [
        add_hyper_link_to_book(book)
        for book in await backend.get_all_books()
    ], 201
