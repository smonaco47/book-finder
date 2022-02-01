# Modified from https://developers.google.com/docs/api/quickstart/python

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/books']

def get_books_service():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('books', 'v1', credentials=creds)

def main():
    service = get_books_service()

    try:
        shelves = service.mylibrary().bookshelves().list().execute()
        
        volumes = {}
        for shelf in shelves['items']:
            if shelf['title'] in ('My Books', 'Books for you'):
                continue
            
            try:
                volumes_on_shelf = service.mylibrary().bookshelves().volumes().list(shelf=shelf['id'], maxResults=1000).execute()
                if volumes_on_shelf['totalItems'] > 0:
                    volumes[shelf['title']] = volumes_on_shelf['items']
            except HttpError as err:
                print(err)

    except HttpError as err:
        print(err)

    for volume in volumes:
        print(volume, len(volumes[volume]))
    
    with open('books.json', 'w') as out:
        out.write(json.dumps(volumes, indent=2))

if __name__ == '__main__':
    main()