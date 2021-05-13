"""Module for handling the motor mongo package code."""
import contextlib
import os
from typing import Any, Dict, List, Optional

import motor.motor_asyncio
from pymongo.errors import DuplicateKeyError

DB = "books"
BOOKS_COLLECTION = "books"
AUTHORS_COLLECTION = "authors"
GENRES_COLLECTION = "genres"


BACKEND: Optional["MongoBackend"] = None


class BookExistsException(Exception):
    pass


class MongoBackend:
    def __init__(self, uri: str) -> None:
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)

    async def get_all_books(self) -> List[Dict[str, Any]]:
        cursor = self._client[DB][BOOKS_COLLECTION].find({}, {"_id": 0})
        return [doc async for doc in cursor]

    async def get_single_book_by_id(self, book_id: str) -> Dict[str, Any]:
        return await self._client[DB][BOOKS_COLLECTION].find_one(
            {"book_id": book_id}, {"_id": 0}
        )

    async def insert_authors_in_db(self, author: str) -> None:
        with contextlib.suppress(DuplicateKeyError):
            await self._client[DB][AUTHORS_COLLECTION].insert_one({"name": author})

    async def insert_genres_in_db(self, genres: List[str]) -> None:
        for genre in genres:
            with contextlib.suppress(DuplicateKeyError):
                await self._client[DB][GENRES_COLLECTION].insert_one({"name": genre})

    async def get_single_book_by_name(self, book_name: str) -> Dict[str, Any]:
        return await self._client[DB][BOOKS_COLLECTION].find_one(
            {"name": book_name}, {"_id": 0}
        )

    async def update_one_book(self, book_id: str, data: Dict[str, Any]) -> None:
        data["book_id"] = book_id
        await self._client[DB][BOOKS_COLLECTION].replace_one({"book_id": book_id}, data)

    async def insert_one_book(self, data: Dict[str, Any]) -> None:
        try:
            await self._client[DB][BOOKS_COLLECTION].insert_one(data)
        except DuplicateKeyError:
            raise BookExistsException()

    async def delete_one_book(self, book_id: str) -> None:
        await self._client[DB][BOOKS_COLLECTION].delete_one({"book_id": book_id})


def backend():
    global BACKEND
    BACKEND = MongoBackend(uri=os.getenv("MONGODB_URI"))
