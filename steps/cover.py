import os
from datetime import datetime
from typing import Any

import streamlit as st
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']
DOCUMENT_ID = "1CVawnjkR2eMJ6pqHlu8su3zvmrIdesfR78DNAUhKubE"


class GoogleCredentialsHandler(object):
    def __init__(self, credentials: Credentials | None, token_file: str):
        self.token_file = token_file
        self.credentials = credentials

    @classmethod
    def from_token(cls, filename='token.json'):
        if os.path.exists(filename):
            return cls(Credentials.from_authorized_user_file(filename, SCOPES), token_file=filename)
        else:
            return cls(None, token_file=filename)

    def is_logged_in(self):
        return self.credentials is not None and self.credentials.valid

    def need_refresh(self):
        return self.credentials and self.credentials.expired and self.credentials.refresh_token

    def refresh(self):
        self.credentials.refresh(Request())

    def run_flow(self, google_credentials_json: dict[Any, Any]):
        flow = InstalledAppFlow.from_client_config(
            google_credentials_json, SCOPES
        )
        self.credentials = flow.run_local_server()

    def save_token(self):
        with open(self.token_file, "w") as token:
            token.write(self.credentials.to_json())

    def logout(self):
        os.unlink(self.token_file)
        del self.credentials


creds = GoogleCredentialsHandler.from_token()


def login_to_google(credentials_handler: GoogleCredentialsHandler):
    if not credentials_handler.is_logged_in():
        if credentials_handler.need_refresh():
            credentials_handler.refresh()
        else:
            credentials_handler.run_flow(st.session_state.google_credentials_json)

        credentials_handler.save_token()

st.subheader('Create Cover Letter')
if creds.is_logged_in():
    if st.button('Logout', type='secondary'):
        creds.logout()
        st.rerun()

    try:
        docs_service = build("docs", "v1", credentials=creds.credentials)
        drive_service = build("drive", "v3", credentials=creds.credentials)

        document = docs_service.documents().get(documentId=DOCUMENT_ID).execute()

        st.write(
            f"Template in use is: [{document.get('title')}](https://docs.google.com/document/d/{document.get('documentId')})")
        if st.button('Create Cover letter'):
            with st.spinner('Creating Cover Letter'):
                cover_letter = drive_service.files().copy(fileId=document.get('documentId'), body={
                    'name': f'Anschreiben - {st.session_state.job_description_json['job']['company_name']}'}).execute()

                requests = [
                    {
                        'replaceAllText': {
                            'containsText': {
                                'text': '{{date}}',
                                'matchCase': 'true'
                            },
                            'replaceText': str(datetime.now().strftime("%d.%m.%Y")),
                        }
                    },
                    {
                        'replaceAllText': {
                            'containsText': {
                                'text': '{{company_name}}',
                                'matchCase': 'true'
                            },
                            'replaceText': st.session_state.job_description_json['job']['company_name'],
                        }
                    },
                    {
                        'replaceAllText': {
                            'containsText': {
                                'text': '{{role_title}}',
                                'matchCase': 'true'
                            },
                            'replaceText': st.session_state.job_description_json['job']['title'],
                        }
                    },
                    {
                        'replaceAllText': {
                            'containsText': {
                                'text': '{{cover_body}}',
                                'matchCase': 'true'
                            },
                            'replaceText': st.session_state.application,
                        }
                    }

                ]

                result = docs_service.documents().batchUpdate(
                    documentId=cover_letter.get('id'), body={'requests': requests}).execute()

            st.success(
                f"Created [{cover_letter.get('name')}](https://docs.google.com/document/d/{cover_letter.get('id')})")
    except HttpError as err:
        st.error(err)
else:
    if st.button('Login'):
        login_to_google(creds)
        st.rerun()
