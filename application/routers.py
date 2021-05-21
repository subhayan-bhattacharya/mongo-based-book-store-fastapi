"""Module for containing the routes for the application."""
import hashlib
import json
import string
import urllib
import uuid
from collections import OrderedDict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

from async_lru import alru_cache
from fastapi import APIRouter, Header, Response, status

import application.models as models
import application.mongo as mongo

router = APIRouter()


@alru_cache()
async def get_total_number_of_books(
    authors: Optional[Tuple[str]] = None,
    genres: Optional[Tuple[str]] = None,
    published_year: Optional[datetime] = None,
):
    return await mongo.BACKEND.get_total_number_of_books(
        authors=list(authors) if authors is not None else None,
        genres=list(genres) if genres is not None else None,
        published_year=published_year,
    )


def generate_hash_for_book(book: Dict[str, Any]) -> str:
    return hashlib.sha1(
        json.dumps(book, sort_keys=True, default=str).encode()
    ).hexdigest()


@router.get("/authors")
async def get_all_authors() -> List[Dict[str, Any]]:
    return [doc["name"] for doc in await mongo.BACKEND.get_all_authors()]


@router.get("/genres")
async def get_all_authors() -> List[Dict[str, Any]]:
    return [doc["name"] for doc in await mongo.BACKEND.get_all_genres()]


@router.get(
    "/books", response_model=models.AllBooksResponse, response_model_exclude_unset=True
)
async def get_the_list_of_all_books(
    authors: Optional[str] = None,
    genres: Optional[str] = None,
    published_year: Optional[str] = None,
    page: int = 1,
) -> Dict[str, Any]:
    params = OrderedDict()
    next_page_url = None
    prev_page_url = None
    number_of_documents = 3

    authors = tuple(authors.strip('"').split(",")) if authors is not None else None
    genres = tuple(genres.strip('"').split(",")) if genres is not None else None
    published_year = (
        datetime.strptime(published_year, "%Y") if published_year is not None else None
    )

    count_of_books = await get_total_number_of_books(
        authors=authors, genres=genres, published_year=published_year
    )
    skips = number_of_documents * (page - 1)
    all_books = [
        book
        for book in await mongo.BACKEND.get_all_books(
            skips=skips,
            number_of_documents=number_of_documents,
            authors=list(authors) if authors is not None else None,
            genres=list(genres) if genres is not None else None,
            published_year=published_year if published_year is not None else None,
        )
    ]

    if authors is not None:
        params["authors"] = ".".join(authors)
    if genres is not None:
        params["genres"] = ".".join(genres)
    if published_year is not None:
        params["published_year"] = published_year

    prev_page = None if page == 1 else page - 1
    if prev_page is not None:
        if not params:
            prev_page_url = f"{models.base_uri()}books?page={prev_page}"
        else:
            prev_page_url = (
                f"{models.base_uri()}books?{urllib.parse.urlencode(params).replace('.', ',')}"
                f"&page={prev_page}"
            )

    next_page = page + 1 if skips + number_of_documents < count_of_books else None
    if next_page is not None:
        if not params:
            next_page_url = f"{models.base_uri()}books?page={next_page}"
        else:
            next_page_url = (
                f"{models.base_uri()}books?{urllib.parse.urlencode(params).replace('.', ',')}"
                f"&page={next_page}"
            )

    return {
        "total_results": count_of_books,
        "prev_page": prev_page_url,
        "next_page": next_page_url,
        "books": all_books,
    }


@router.post(
    "/books",
    response_model=Union[models.SingleBookResponse, models.SingleMessageResponse],
    status_code=201,
)
async def add_a_book(book: models.Book, response: Response) -> Dict[str, Any]:
    book_to_insert = book.dict()
    book_to_insert["book_id"] = str(uuid.uuid1())
    book_to_insert["eTag"] = generate_hash_for_book(book_to_insert)
    book_to_insert["author"] = string.capwords(book_to_insert["author"])

    print(book_to_insert)

    try:
        await mongo.BACKEND.insert_one_book(data=book_to_insert)
    except mongo.BookExistsException:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": f"Book {book_to_insert.get('name')} already exists!!"}

    await mongo.BACKEND.insert_authors_in_db(book_to_insert.get("author"))
    await mongo.BACKEND.insert_genres_in_db(book_to_insert.get("genres"))

    get_total_number_of_books.cache_clear()
    return await mongo.BACKEND.get_single_book_by_name(book_to_insert.get("name"))


@router.get(
    "/book/{book_id}",
    response_model=Union[models.SingleBookResponse, models.SingleMessageResponse],
)
async def get_a_single_book(
    book_id: str, response: Response, if_none_match: Optional[str] = Header(None)
) -> Union[Dict[str, Any], Response]:
    book = await mongo.BACKEND.get_single_book_by_id(book_id=book_id)
    if book is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "No such book exist!!"}
    if if_none_match is not None:
        if book.get("eTag") == if_none_match:
            return Response(status_code=status.HTTP_304_NOT_MODIFIED)
    if book.get("eTag") is not None:
        response.headers["ETag"] = book.get("eTag")
    return book


@router.put(
    "/book/{book_id}",
    response_model=Union[models.SingleBookResponse, models.SingleMessageResponse],
)
async def update_a_book(
    book_id: str,
    book: models.Book,
    response: Response,
    if_match: Optional[str] = Header(None),
) -> Union[Dict[str, Any], Response]:
    book_in_db = await mongo.BACKEND.get_single_book_by_id(book_id=book_id)
    if book_in_db is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "No such book exist!!"}

    book_details_to_insert = book.dict()

    if if_match is not None and book_in_db.get("eTag") is not None:
        if if_match != book_in_db.get("eTag"):
            return Response(status_code=status.HTTP_412_PRECONDITION_FAILED)

    book_details_to_insert["eTag"] = generate_hash_for_book(book_details_to_insert)

    await mongo.BACKEND.update_one_book(book_id=book_id, data=book_details_to_insert)
    await mongo.BACKEND.insert_authors_in_db(
        string.capwords(book_details_to_insert["author"])
    )
    await mongo.BACKEND.insert_genres_in_db(book_details_to_insert["genres"])

    return await mongo.BACKEND.get_single_book_by_id(book_id=book_id)


@router.delete("/book/{book_id}", response_model=models.SingleMessageResponse)
async def delete_a_book(
    book_id: str, response: Response, if_match: Optional[str] = Header(None)
) -> Union[Dict[str, Any], Response]:
    book_in_db = await mongo.BACKEND.get_single_book_by_id(book_id=book_id)
    if book_in_db is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "No such book exist!!"}

    if if_match is not None and book_in_db.get("eTag") is not None:
        if if_match != book_in_db.get("eTag"):
            return Response(status_code=status.HTTP_412_PRECONDITION_FAILED)

    await mongo.BACKEND.delete_one_book(book_id=book_id)
    return {"message": "Book deleted !!"}
