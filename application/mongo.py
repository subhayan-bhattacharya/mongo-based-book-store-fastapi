"""Module for handling the motor mongo package code."""
from typing import Any, Dict, List

import motor.motor_asyncio

DB = "books"
COLLECTION = "books"


class MongoBackend:
    def __init__(self, uri: str) -> None:
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)

    async def get_all_books(self) -> List[Dict[str, Any]]:
        cursor = self._client[DB][COLLECTION].find({}, {"_id": 0})
        return [doc async for doc in cursor]

    async def get_single_book(self, book_id: str) -> Dict[str, Any]:
        return await self._client[DB][COLLECTION].find_one(
            {"book_id": book_id}, {"_id": 0}
        )

    async def update_one_book(self, book_id: str, data: Dict[str, Any]) -> None:
        data["book_id"] = book_id
        await self._client[DB][COLLECTION].replace_one({"book_id": book_id}, data)

    async def insert_one_book(self, data: Dict[str, Any]) -> None:
        await self._client[DB][COLLECTION].insert_one(data)

    async def delete_one_book(self, book_id: str) -> None:
        await self._client[DB][COLLECTION].delete_one({"book_id": book_id})
