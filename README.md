# Book Finder

1. Fetch book lists from Google API

You'll need to set up your local environment to have a Google API token.
* https://developers.google.com/workspace/guides/create-credentials
* https://developers.google.com/workspace/guides/create-project

Set up the key to have access to the Google Books API. 

Run the get_books.py script to fetch the books in your personal workspace. It should save a JSON of the collected information to books.json.

If you wish to skip this step, you could also just rename example_books.json to books.json to see the example execution.

2. Run the jupyter notebooks

```
python -m venv ./.venv

.venv\Scripts\activate
or 
source ./.venv/Scripts/activate

```

Then install the dependencies
```
pip install wheel
pip install --upgrade pip
pip install -r requirements.txt
jupyter notebook
```

Run the (Transform google books)[Transform google books.ipynb] notebook to collect all of the scraped information. Scraped Amazon & overdrive data is cached to files locally, so you can re-run and it will not re-run the commands.

Then, run the (Book Analysis)[Book Analysis.ipynb] notebook to analyze the data that was collected.
