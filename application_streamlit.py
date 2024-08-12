import json

import streamlit as st

from ai.validate import is_valid_openai_key

with st.sidebar:
    st.title('Application')
    if st.button('Start Over'):
        for state in ['job_description_json', 'step', 'site', 'site_content', 'application']:
            if state in st.session_state:
                st.session_state.pop(state)

    st.title("Configuration")
    st.session_state.api_key = st.text_input("Enter OpenAI API key:", type="password",
                                             help='Get your key [here](https://platform.openai.com/organization/api-keys)')
    is_valid_key = is_valid_openai_key(st.session_state.api_key)
    if not st.session_state.api_key:
        st.error('Please enter your OpenAI API Key.')
    elif is_valid_key:
        st.success('API Key valid.')
    else:
        st.error('Invalid API key. Enter correct API key.')
        st.session_state.api_key = ''

    cv_file = st.file_uploader('Text file with cv data', type="txt", accept_multiple_files=False)
    if cv_file:
        st.session_state.cv_data = cv_file.getvalue().decode('utf8')
    else:
        st.error('Please upload cv data')

    google_credentials_file = st.file_uploader('Google Credentials JSON', type="json", accept_multiple_files=False)
    if google_credentials_file:
        st.session_state.google_credentials_json = json.loads(google_credentials_file.getvalue())
    else:
        st.error('Please upload google credentials file')

st.title("Application Helper")

offer_page = st.Page('steps/offer.py', title='Analyze Job Offer')
application_page = st.Page('steps/application.py', title='Create Application')
cover_letter_page = st.Page('steps/cover.py', title='Create Cover Letter')

pages = [offer_page, application_page, cover_letter_page]
if 'step' not in st.session_state:
    st.session_state.step = 0

progress = st.progress(int(st.session_state.step / (len(pages) - 1) * 100),
                       text=f'[{st.session_state.step + 1}/{len(pages)}] {pages[st.session_state.step].title}')
columns = st.columns((1, 5, 1))
with columns[0]:
    if st.session_state.step > 0:
        if st.button('Back', type='primary'):
            st.session_state.step = int((st.session_state.step - 1) % len(pages))
            st.rerun()
with columns[2]:
    if (st.session_state.step + 1) < len(pages):
        if st.button('Next', type='primary'):
            st.session_state.step = int((st.session_state.step + 1) % len(pages))
            st.rerun()

pg = st.navigation([pages[st.session_state.step]], position='hidden')
pg.run()
