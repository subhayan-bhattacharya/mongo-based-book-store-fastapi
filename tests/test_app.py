import string
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from application import app, mongo

client = TestClient(app)

all_books = [
    {
        "name": "Tell me your dreams",
        "author": "Sidney Sheldon",
        "genres": ["Fiction", "Thriller"],
        "published_year": datetime.strptime("1997", "%Y"),
        "description": "Some description",
        "book_id": "book_1",
        "eTag": "book_1",
    },
    {
        "name": "The eye of the needle",
        "author": "Ken Follet",
        "genres": ["Fiction", "Thriller"],
        "published_year": datetime.strptime("2000", "%Y"),
        "description": "Some description",
        "book_id": "book_2",
        "eTag": "book_2",
    },
    {
        "name": "Master of the game",
        "author": "Sidney Sheldon",
        "genres": ["Fiction", "Thriller"],
        "published_year": datetime.strptime("1997", "%Y"),
        "description": "Some description",
        "book_id": "book_3",
        "eTag": "book_3",
    },
    {
        "name": "The pillars of the earth",
        "author": "Ken Follet",
        "genres": ["Fiction", "Thriller"],
        "published_year": datetime.strptime("1997", "%Y"),
        "description": "Some description",
        "book_id": "book_4",
        "eTag": "book_4",
    },
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
        "genres": ["Fiction", "Thriller"],
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


@pytest.mark.get_all_books
def test_get_all_books_in_db(backend):
    mongo.BACKEND = backend(books=all_books)
    response = client.get("/books")
    assert response.status_code == 200
    total_results = response.json()["total_results"]
    assert total_results == 4
    books_in_first_page = response.json()["books"]
    assert len(books_in_first_page) == 3
    assert "next_page" in response.json()
    assert "page=2" in response.json()["next_page"]


@pytest.mark.get_all_books
def test_get_all_books_in_db_second_page(backend):
    mongo.BACKEND = backend(books=all_books)
    response = client.get("/books?page=2")
    assert response.status_code == 200
    total_results = response.json()["total_results"]
    assert total_results == 4
    books_in_first_page = response.json()["books"]
    assert len(books_in_first_page) == 1
    assert "next_page" not in response.json()
    assert "prev_page" in response.json()
    assert "page=1" in response.json()["prev_page"]


@pytest.mark.add_a_book
def test_that_a_book_with_missing_fields_fails_to_add(backend):
    mongo.BACKEND = backend(books=all_books)
    book_to_add = {
        "name": "Test book",
        "author": "Test author",
        "genres": ["Fiction", "Thriller"],
        "published_year": "2000"
    }
    response = client.post("/books", json=book_to_add)
    assert response.status_code == 422


@pytest.mark.add_a_book
def test_that_book_which_exists_cannot_be_added(backend):
    mongo.BACKEND = backend(books=all_books)
    book_to_add = {
        "name": "Tell me your dreams",
        "author": "Sidney Sheldon",
        "genres": ["Fiction", "Thriller"],
        "published_year": "1997",
        "description": "Some description"
    }
    response = client.post("/books", json=book_to_add)
    assert response.status_code == 400
    assert response.json() == {"message": "Book Tell me your dreams already exists!!"}


@pytest.mark.add_a_book
def test_adding_a_book(backend):
    mongo.BACKEND = backend(books=all_books)
    book_to_add = {
        "name": "Test book",
        "author": "Test author",
        "genres": ["Fiction", "Thriller"],
        "description": "some description",
        "published_year": "2000"
    }
    response = client.post("/books", json=book_to_add)
    assert response.status_code == 201
    book_returned = response.json()
    for key in book_to_add:
        if key == "author":
            assert book_returned[key] == string.capwords(book_to_add[key])
        else:
            assert book_returned[key] == book_to_add[key]

    assert "link" in book_returned


