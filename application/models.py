"""Module for the models used in the application."""
import functools
import os
from datetime import datetime
from typing import List, Optional, Union

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


class AllBooksResponse(BaseModel):
    name: str
    author: str
    link: Optional[str] = None

    def __init__(self, name, author, **data):
        super().__init__(
            name=name, author=author, link=f"{base_uri()}book/{data['book_id']}"
        )
