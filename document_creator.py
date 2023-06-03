from __future__ import print_function
import os.path
from typing import Final
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class DocumentCreator:
    SCOPES: Final = [
        "https://www.googleapis.com/auth/documents",
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/drive.file",
    ]

    def __init__(self):
        self.creds = None

    def connect_api(self):
        creds = None

        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('google_oauth_client.json', self.SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        self.creds = creds

    def create_doc(self, filename, text):
        try:
            service = build("docs", "v1", credentials=self.creds)
            doc = service.documents().create(body={"title": filename}).execute()

            requests = [
                {
                    'insertText': {
                        'location': {
                            'index': 1,
                        },
                        'text': text
                    }
                },
            ]

            service.documents().batchUpdate(documentId=doc.get("documentId"), body={'requests': requests}).execute()

        except HttpError as err:
            print(err)


if __name__ == '__main__':
    doc_creator = DocumentCreator()
    doc_creator.connect_api()
    doc_creator.create_doc("abc", "안녕하세요\n제 이름은 이수원입니다.\n잘 부탁드립니다.")
