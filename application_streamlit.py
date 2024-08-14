import json
from datetime import datetime

import streamlit as st
from openai import APIStatusError

from ai.conversation import Conversation
from ai.validate import is_valid_openai_key
from steps.pages import pages

with st.sidebar:
    st.title('Application')
    if st.button('Start Over'):
        for state in ['job_description_json', 'step', 'site', 'site_content', 'application']:
            if state in st.session_state:
                st.session_state.pop(state)
        st.query_params.from_dict({'step': 0})

    st.title("Configuration")
    api_key = st.text_input("Enter OpenAI API key:", type="password",
                            help='Get your key [here](https://platform.openai.com/organization/api-keys)')
    try:
        if not api_key:
            st.error('Please enter your OpenAI API Key.')
        elif api_key != st.session_state.get('api_key'):
            if is_valid_openai_key(api_key):
                st.session_state.api_key = api_key
                st.success('API Key valid.')
            else:
                st.error('Invalid API key. Enter correct API key.')
                del st.session_state.api_key
        elif st.session_state.get('api_key') and is_valid_openai_key(st.session_state.api_key):
            with st.expander('Token Usage'):
                c = Conversation(st.session_state.api_key)
                usage = c.usage(datetime.now())
                st.write(f'Context  : {usage.context_tokens} ({usage.context_costs:.2f} €)')
                st.write(f'Generated: {usage.generated_tokens} ({usage.generated_costs:.2f} €)')

    except APIStatusError as e:
        st.error(f'API Error: {e}\nsee [status.openai.com](https://status.openai.com/)')

    cv_file = st.file_uploader('Text file with cv data', type="txt", accept_multiple_files=False)
    if cv_file:
        if cv_file.file_id != st.session_state.get('cv_file_id'):
            st.session_state.cv_file_id = cv_file.file_id
            st.session_state.cv_data = cv_file.getvalue().decode('utf8')
    else:
        if 'cv_file_id' in st.session_state: del st.session_state.cv_file_id
        st.error('Please upload cv data')

    google_credentials_file = st.file_uploader('Google Credentials JSON', type="json", accept_multiple_files=False)
    if google_credentials_file:
        st.session_state.google_credentials_json = json.loads(google_credentials_file.getvalue())
    else:
        st.error('Please upload google credentials file')

st.title("Application Helper")

if 'step' not in st.query_params:
    st.query_params.from_dict({'step': 0})

step = int(st.query_params.step)

progress = st.progress(int(step / (len(pages) - 1) * 100),
                       text=f'[{step + 1}/{len(pages)}] {pages[step].title}')
columns = st.columns((1, 5, 1))
with columns[0]:
    if step > 0:
        if st.button('Back', type='primary'):
            st.query_params.step = int((step - 1) % len(pages))
            st.rerun()
with columns[2]:
    if (step + 1) < len(pages):
        if st.button('Next', type='primary'):
            st.query_params.step = int((step + 1) % len(pages))
            st.rerun()

pg = st.navigation([pages[step]], position='hidden')
pg.run()
st.query_params.from_dict({'step': step})
