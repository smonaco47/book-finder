1. Get the Google API


https://python.land/virtual-environments/virtualenv
python -m venv ./.venv
source ./.venv/Scripts/activate
pip install -r requirements.txt


https://developers.google.com/books/docs/v1/getting_started
https://developers.google.com/books/docs/v1/using#auth
https://developers.google.com/docs/api/quickstart/python

Had to grab credentials.json which was the client secret downloaded from the oauth 2.0 scope



How to use the Python library
https://developers.google.com/books/docs/v1/reference/bookshelves

service.mylibrary().bookshelves().volumes().list(shelf=shelf['id'], maxResults=500)
corresponds to https://developers.google.com/books/docs/v1/reference/mylibrary/bookshelves/volumes/list