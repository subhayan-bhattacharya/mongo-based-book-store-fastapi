import asyncio
import itertools
from typing import Any, Dict, List

import pytest


class MockedBackend:
    def __init__(self, books: List[Dict[str, Any]]):
        self.books = books

    async def get_total_number_of_books(self, authors, genres, published_year):
        await asyncio.sleep(0.1)  # Just to make the function an async function
        return len(self._filter_books(authors, genres, published_year))

    def _filter_books(self, authors, genres, published_year):
        if authors is None and genres is None and published_year is None:
            return self.books
        books = []
        if authors is not None:
            for book in self.books:
                if book["author"] in authors:
                    books.append(book)
        if genres is not None:
            book_genres = set(book["genres"])
            if book_genres.intersection(set(genres)):
                books.append(book)
        if published_year is not None:
            if book["published_year"] == published_year:
                books.append(book)
        return books

    async def get_all_books(
        self,
        skips,
        number_of_documents,
        authors=None,
        genres=None,
        published_year=None,
    ):
        await asyncio.sleep(0.1)  # Just to make the function an async function
        books = self._filter_books(authors, genres, published_year)
        return books[skips : skips + number_of_documents]

    async def get_all_authors(self):
        await asyncio.sleep(0.1)  # Just to make the function an async function
        all_authors = set([book["author"] for book in self.books])
        return [{"name": author} for author in sorted(all_authors)]

    async def get_all_genres(self):
        await asyncio.sleep(0.1)  # Just to make the function an async function
        all_genres = sorted(
            list(
                set(
                    itertools.chain.from_iterable(
                        [book["genres"] for book in self.books]
                    )
                )
            )
        )
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
