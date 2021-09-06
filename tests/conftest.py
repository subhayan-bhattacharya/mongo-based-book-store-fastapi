import asyncio
import itertools
from typing import Any, Dict, List

import pytest
import requests

from application import mongo


def check_if_web_app_is_up(ip_address, port):
    url = f"http://{ip_address}:{port}/books"
    response = requests.get(url)
    if response.status_code == 200:
        return True
    return False


@pytest.fixture(scope='session')
def docker_web_app(docker_services):
    docker_services.start('web_app')
    _ = docker_services.wait_for_service(
        "web_app",
        8000,
        check_server=check_if_web_app_is_up
    )
    return None


@pytest.fixture(scope='session')
def docker_db(docker_services):
    docker_services.start('db')
    return None


@pytest.fixture(scope='session')
def docker_compose_files(pytestconfig):
    dir_where_tests_are_run = pytestconfig.invocation_params.dir
    return [
        dir_where_tests_are_run.parents[0].joinpath('docker-compose.yml')
    ]


class MockedBackend:
    def __init__(self, books: List[Dict[str, Any]]):
        self.books = books
        self.authors = set()
        self.genres = set()

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
        if published_year is not None and book["published_year"] == published_year:
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
        return books[skips: skips + number_of_documents]

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

    async def update_one_book(self, book_id: str, data: Dict[str, Any]):
        await asyncio.sleep(0.1)  # Just to make the function an async function
        book_to_change = None
        for book in self.books:
            if book["book_id"] == book_id:
                book_to_change = book
        book_to_change.update(data)
        return book_to_change

    @staticmethod
    async def delete_one_book(book_id: str):
        await asyncio.sleep(0.1)  # Just to make the function an async function

    async def insert_authors_in_db(self, author: str):
        await asyncio.sleep(0.1)  # Just to make the function an async function
        self.authors.add(author)

    async def get_single_book_by_name(self, name: str):
        await asyncio.sleep(0.1)  # Just to make the function an async function
        for book in self.books:
            if book["name"] == name:
                return book

    async def insert_genres_in_db(self, genres: List[str]):
        await asyncio.sleep(0.1)  # Just to make the function an async function
        for genre in genres:
            self.genres.add(genre)

    async def insert_one_book(self, data: Dict[str, Any]):
        await asyncio.sleep(0.1)  # Just to make the function an async function
        name = data.get("name")
        for book in self.books:
            if name == book.get("name"):
                raise mongo.BookExistsException()
        self.authors.add(data.get("author"))
        for genre in data.get("genres"):
            self.genres.add(genre)
        self.books.append(data)


@pytest.fixture
def backend():
    def _backend(books):
        return MockedBackend(books=books)

    return _backend
