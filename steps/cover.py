from datetime import datetime
from typing import Any, Dict

import streamlit as st
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build

from api.credentials_helper import GoogleCredentialsHandler

TEMPLATE_ID = "1CVawnjkR2eMJ6pqHlu8su3zvmrIdesfR78DNAUhKubE"

creds = GoogleCredentialsHandler.from_token()


def login_to_google(credentials_handler: GoogleCredentialsHandler):
    if not credentials_handler.is_logged_in():
        if credentials_handler.need_refresh():
            try:
                credentials_handler.refresh()
            except RefreshError:
                credentials_handler.run_flow(st.session_state.google_credentials_json)
        else:
            credentials_handler.run_flow(st.session_state.google_credentials_json)

        credentials_handler.save_token()


def copy_replace_doc(template_id: str, job_description_json: Dict[str, Any], application_text: str):
    docs_service = build("docs", "v1", credentials=creds.credentials)
    drive_service = build("drive", "v3", credentials=creds.credentials)
    cover_letter_file = drive_service.files().copy(fileId=template_id, body={
        'name': f'Anschreiben - {job_description_json['job']['company_name']}'}).execute()

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
                'replaceText': job_description_json['job']['company_name'],
            }
        },
        {
            'replaceAllText': {
                'containsText': {
                    'text': '{{role_title}}',
                    'matchCase': 'true'
                },
                'replaceText': job_description_json['job']['title'],
            }
        },
        {
            'replaceAllText': {
                'containsText': {
                    'text': '{{cover_body}}',
                    'matchCase': 'true'
                },
                'replaceText': application_text,
            }
        }

    ]

    response = docs_service.documents().batchUpdate(
        documentId=cover_letter_file.get('id'), body={'requests': requests}).execute()
    return cover_letter_file


def get_template_file():
    docs_service = build("docs", "v1", credentials=creds.credentials)
    return docs_service.documents().get(documentId=TEMPLATE_ID).execute()


st.subheader('Create Cover Letter')

if 'job_description_json' not in st.session_state or 'application' not in st.session_state:
    st.error('Job application not analyzed')
else:
    with st.container(border=True):
        if creds.is_logged_in():
            st.markdown('##### :heavy_check_mark: Google Drive Connection')
            if st.button('Logout', type='secondary'):
                creds.logout()
                st.rerun()
            document = get_template_file()
            st.write(
                f"Template in use is: [{document.get('title')}](https://docs.google.com/document/d/{document.get('documentId')})")
        else:
            st.markdown('##### :x: Google Drive Connection')
            if st.button('Login'):
                login_to_google(creds)
                st.rerun()

    if creds.is_logged_in():
        with st.expander('Cover body'):
            st.write(st.session_state.application)
        if st.button('Create Cover letter'):
            with st.spinner('Creating Cover Letter'):
                cover_letter = copy_replace_doc(TEMPLATE_ID,
                                                st.session_state.job_description_json,
                                                st.session_state.application)

                st.success(
                    f"Created [{cover_letter.get('name')}](https://docs.google.com/document/d/{cover_letter.get('id')})")
