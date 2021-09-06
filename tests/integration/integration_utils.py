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

