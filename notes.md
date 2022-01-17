1. Get the Google API


https://python.land/virtual-environments/virtualenv
python -m venv ./.venv
source ./.venv/Scripts/activate
pip install wheel
pip install --upgrade pip
pip install -r requirements.txt



https://developers.google.com/books/docs/v1/getting_started
https://developers.google.com/books/docs/v1/using#auth
https://developers.google.com/docs/api/quickstart/python

Had to grab credentials.json which was the client secret downloaded from the oauth 2.0 scope



How to use the Python library
https://developers.google.com/books/docs/v1/reference/bookshelves

service.mylibrary().bookshelves().volumes().list(shelf=shelf['id'], maxResults=500)
corresponds to https://developers.google.com/books/docs/v1/reference/mylibrary/bookshelves/volumes/list

To re-run, delete token.json
was unable to activate the bash in cygwin, changed line endings from CRLF to LF

2. Amazon scraping

https://www.datacamp.com/community/tutorials/amazon-web-scraping-using-beautifulsoup


3. Overdrive scraping

Had to render the page because otherwise it didn't show up
Need to make sure to close the connection, otherwise things got crazy
Important to nail down the "search not found" early on