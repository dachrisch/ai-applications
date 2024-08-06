import streamlit as st

from ai.validate import is_valid_openai_key

with st.sidebar:
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

    st.title('CV data')
    cv_file = st.file_uploader('Text file with cv data', type="txt",accept_multiple_files=False)
    if cv_file:
        st.session_state.cv_data = cv_file.getvalue().decode('utf8')
    else:
        st.error('Please upload cv data')

st.title("Application Helper")

offer_page = st.Page('pages/offer.py', title='Analyze Job Offer')
application_page = st.Page('pages/application.py', title='Create Application')

pages = [offer_page, application_page]
if 'step' not in st.session_state:
    st.session_state.step = 0

progress = st.progress(int((st.session_state.step ) / (len(pages) - 1) * 100))
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


progress.progress(int((st.session_state.step) / (len(pages) - 1) * 100), text=pages[st.session_state.step].title)
