import itertools
import string
import json
from box import Box


def book_data():
    return {
        'name': "Tell me your dreams",
        'author': "Sidney Sheldon",
        'genres': [
            'Fiction',
            'Thriller'
        ],
        'published_year': '1997',
        'description': 'Some description'
    }


def updated_book_data():
    book = book_data()
    book['description'] = 'Some new description'
    return book


def book_data_to_insert():
    return Box(book_data())


def updated_book_data_to_insert():
    return Box(updated_book_data())


def _validate_inserted_with_retrieved(inserted, response):
    for key in inserted:
        if key == "author":
            assert response.get("author") == string.capwords(inserted.get("author"))
        else:
            assert response.get(key) == inserted.get(key)


def validate_book_response(response, book_data_with_request=None, inserted_book_data=None):
    response_data = response.json()
    inserted_data = None
    if book_data_with_request is not None:
        replaced_inserted_data = book_data_with_request.replace("\'", "\"")
        inserted_data = json.loads(replaced_inserted_data)
    if inserted_book_data is not None:
        inserted_data = inserted_book_data
    assert inserted_data is not None
    _validate_inserted_with_retrieved(inserted=inserted_data, response=response_data)
    assert "link" in response_data


def validate_authors_response(response, all_books_inserted):
    response_data = response.json()
    assert isinstance(response_data, list)
    all_authors_inserted = list(set([book["author"] for book in all_books_inserted]))
    assert sorted(response_data) == sorted(all_authors_inserted)


def validate_genres_response(response, all_books_inserted):
    response_data = response.json()
    assert isinstance(response_data, list)
    all_authors_inserted = list(
        set(
            itertools.chain.from_iterable([book["genres"] for book in all_books_inserted])
        )
    )
    assert sorted(response_data) == sorted(all_authors_inserted)


def validate_all_books_first_page_response(response, all_books_inserted):
    response_data = response.json()
    assert 'next_page' in response_data
    assert 'total_results' in response_data
    assert response_data['total_results'] == len(all_books_inserted)


def validate_all_books_second_page_response(response, all_books_inserted, books_returned_in_prev_request):
    response_data = response.json()
    replaced_books_returned_prev_request = books_returned_in_prev_request.replace("\'", "\"")
    books_in_prev_response = json.loads(replaced_books_returned_prev_request)
    if len(all_books_inserted) - len(books_in_prev_response) < 3:
        assert "next_page" not in response_data
        assert "prev_page" in response_data
        assert len(response_data["books"]) == len(all_books_inserted) - len(books_in_prev_response)