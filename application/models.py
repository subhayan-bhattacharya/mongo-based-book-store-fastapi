"""Module for the models used in the application."""
import functools
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, validator


@functools.lru_cache()
def base_uri():
    return os.getenv("BASE_URI")


class Book(BaseModel):
    name: str
    author: str
    description: str
    published_year: datetime
    genres: List[str]

    @validator("published_year", pre=True)
    def parse_birthdate(cls, value: Union[str, int]):
        return datetime.strptime(str(value), "%Y")


class SingleBookResponse(BaseModel):
    name: str
    author: str
    description: str
    genres: List[str]
    published_year: Optional[str] = None
    link: Optional[str] = None

    def __init__(self, name, author, description, genres, **data):
        super().__init__(
            name=name,
            author=author,
            description=description,
            published_year=datetime.strftime(data["published_year"], "%Y"),
            genres=genres,
            link=f"{base_uri()}book/{data['book_id']}",
        )


class SingleBookInAllBooksResponse(BaseModel):
    name: str
    author: str
    link: str


class AllBooksResponse(BaseModel):
    total_results: int
    prev_page: Optional[str] = None
    next_page: Optional[str] = None
    books: List[SingleBookInAllBooksResponse]

    def __init__(
        self,
        total_results: int,
        books: List[Dict[str, Any]],
        prev_page: Optional[str] = None,
        next_page: Optional[str] = None,
    ):
        kwargs = {
            "total_results": total_results,
            "books": [
                SingleBookInAllBooksResponse(
                    name=book.get("name"),
                    author=book.get("author"),
                    link=f"{base_uri()}book/{book.get('book_id')}",
                )
                for book in books
            ],
        }
        if next_page is not None:
            kwargs["next_page"] = next_page
        if prev_page is not None:
            kwargs["prev_page"] = prev_page

        super().__init__(**kwargs)
