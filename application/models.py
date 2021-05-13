"""Module for the models used in the application."""
from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, validator


class Book(BaseModel):
    name: str
    author: str
    published_year: datetime
    genres: List[str]

    @validator("published_year", pre=True)
    def parse_birthdate(cls, value: Union[str, int]):
        return datetime.strptime(str(value), "%Y")
