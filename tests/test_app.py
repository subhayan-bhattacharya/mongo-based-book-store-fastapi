import pytest
from fastapi.testclient import TestClient
from application import app
from application import mongo
from datetime import datetime

client = TestClient(app)

all_books = [
    {
        "name": "Tell me your dreams",
        "author": "Sidney Sheldon",
        "genres": [
            "Fiction",
            "Thriller"
        ],
        "published_year": datetime.strptime("1997", "%Y"),
        "description": "Some description",
        "book_id": "book_1",
        "eTag": "book_1"
    },
    {
        "name": "The eye of the needle",
        "author": "Ken Follet",
        "genres": [
            "Fiction",
            "Thriller"
        ],
        "published_year": datetime.strptime("2000", "%Y"),
        "description": "Some description",
        "book_id": "book_2",
        "eTag": "book_2"
    }
]


def test_get_authors(backend):
    mongo.BACKEND = backend(books=all_books)
    response = client.get("/authors")
    assert response.status_code == 200
    assert response.json() == sorted(["Sidney Sheldon", "Ken Follet"])


def test_get_all_genres(backend):
    mongo.BACKEND = backend(books=all_books)
    response = client.get("/genres")
    assert response.status_code == 200
    assert response.json() == sorted(["Thriller", "Fiction"])


def _check_book_correctness_book_1(response_book):
    assert "link" in response_book
    assert response_book["link"].endswith("book_1")
    response_book.pop("link")
    assert response_book == {
        "name": "Tell me your dreams",
        "author": "Sidney Sheldon",
        "genres": [
            "Fiction",
            "Thriller"
        ],
        "published_year": "1997",
        "description": "Some description",
    }


@pytest.mark.get_single_book
def test_get_single_book_by_id(backend):
    mongo.BACKEND = backend(books=all_books)
    response = client.get("/book/book_1")
    assert response.status_code == 200
    jsonified_response = response.json()
    _check_book_correctness_book_1(jsonified_response)


@pytest.mark.get_single_book
def test_get_single_book_if_it_does_not_exist(backend):
    mongo.BACKEND = backend(books=all_books)
    response = client.get("/book/book_100")
    assert response.status_code == 400
    assert response.json() == {"message": "No such book exist!!"}


@pytest.mark.get_single_book
def test_get_single_book_with_correct_etag(backend):
    mongo.BACKEND = backend(books=all_books)
    response = client.get("/book/book_1", headers={"If-None-Match": "book_1"})
    assert response.status_code == 304


@pytest.mark.get_single_book
def test_get_single_book_with_wrong_etag(backend):
    mongo.BACKEND = backend(books=all_books)
    response = client.get("/book/book_1", headers={"If-None-Match": "book_10"})
    assert response.status_code == 200
    jsonified_response = response.json()
    _check_book_correctness_book_1(jsonified_response)


@pytest.mark.delete_single_book
def test_delete_book_if_not_exists(backend):
    mongo.BACKEND = backend(books=all_books)
    response = client.delete("/book/book_100")
    assert response.status_code == 400
    assert response.json() == {"message": "No such book exist!!"}


@pytest.mark.delete_single_book
def test_delete_book_with_correct_etag(backend):
    mongo.BACKEND = backend(books=all_books)
    response = client.delete("/book/book_1", headers={"If-Match": "book_1"})
    assert response.status_code == 200
    assert response.json() == {"message": "Book deleted !!"}


@pytest.mark.delete_single_book
def test_delete_book_with_wrong_etag(backend):
    mongo.BACKEND = backend(books=all_books)
    response = client.delete("/book/book_1", headers={"If-Match": "book_100"})
    assert response.status_code == 412


