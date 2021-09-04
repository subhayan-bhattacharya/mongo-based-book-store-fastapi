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


def validate_book_response(response, inserted_book):
    response_data = response.json()
    replaced_inserted_data = inserted_book.replace("\'", "\"")
    inserted_data = json.loads(replaced_inserted_data)
    for key in inserted_data:
        if key == "author":
            assert response_data.get("author") == string.capwords(inserted_data.get("author"))
        else:
            assert response_data.get(key) == inserted_data.get(key)
    assert "link" in response_data
