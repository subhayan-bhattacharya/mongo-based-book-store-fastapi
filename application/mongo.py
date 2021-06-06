"""Module for handling the motor mongo package code."""
import contextlib
import os
from datetime import datetime
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

    @staticmethod
    def get_find_condition(
        authors: Optional[List[str]] = None,
        genres: Optional[List[str]] = None,
        published_year: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        find_condition = {}
        if authors is not None:
            find_condition["author"] = {"$in": authors}
        if genres is not None:
            find_condition["genres"] = {"$in": genres}
        if published_year is not None:
            find_condition["published_year"] = published_year
        return find_condition

    async def get_total_number_of_books(
        self,
        authors: Optional[List[str]] = None,
        genres: Optional[List[str]] = None,
        published_year: Optional[datetime] = None,
    ) -> int:
        return await self._client[DB][BOOKS_COLLECTION].count_documents(
            self.get_find_condition(
                authors=authors, genres=genres, published_year=published_year
            )
        )

    async def get_all_books(
        self,
        skips: int,
        number_of_documents: int,
        authors: Optional[List[str]] = None,
        genres: Optional[List[str]] = None,
        published_year: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        cursor = (
            self._client[DB][BOOKS_COLLECTION]
            .find(
                self.get_find_condition(
                    authors=authors, genres=genres, published_year=published_year
                ),
                {"_id": 0},
            )
            .skip(skips)
            .limit(number_of_documents)
        )
        return [doc async for doc in cursor]

    async def get_all_authors(self) -> List[Dict[str, Any]]:
        cursor = self._client[DB][AUTHORS_COLLECTION].find({}, {"_id": 0})
        return [doc async for doc in cursor]

    async def get_all_genres(self) -> List[Dict[str, Any]]:
        cursor = self._client[DB][GENRES_COLLECTION].find({}, {"_id": 0})
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
