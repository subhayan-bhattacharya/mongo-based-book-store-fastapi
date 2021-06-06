import asyncio
import itertools
from typing import List, Dict, Any

import pytest


class MockedBackend:
    def __init__(self, books: List[Dict[str, Any]]):
        self.books = books

    async def get_all_authors(self):
        await asyncio.sleep(0.1)  # Just to make the function an async function
        all_authors = sorted([book["author"] for book in self.books])
        return [{"name": author} for author in all_authors]

    async def get_all_genres(self):
        await asyncio.sleep(0.1)  # Just to make the function an async function
        all_genres = sorted(list(set(itertools.chain.from_iterable([book["genres"] for book in self.books]))))
        return [{"name": genre} for genre in all_genres]

    async def get_single_book_by_id(self, book_id: str):
        await asyncio.sleep(0.1)  # Just to make the function an async function
        for book in self.books:
            if book["book_id"] == book_id:
                return book

    @staticmethod
    async def delete_one_book(book_id: str):
        await asyncio.sleep(0.1)  # Just to make the function an async function
        pass


@pytest.fixture
def backend():
    def _backend(books):
        return MockedBackend(books=books)
    return _backend

