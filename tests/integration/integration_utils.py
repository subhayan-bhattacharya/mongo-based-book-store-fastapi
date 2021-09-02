import string
import json


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
