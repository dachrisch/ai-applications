import os
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']


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
