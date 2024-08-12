import string

import streamlit as st

from ai.conversation import Conversation

if all(k in st.session_state for k in ('cv_data', 'job_description_json')):
    st.subheader('Application')
    with open('application.prompt', 'r') as ap:
        application_prompt_template = string.Template(ap.read())
    application_prompt = application_prompt_template.safe_substitute(
        {'JOBDESC': st.session_state.job_description_json,
         'CVDATA': st.session_state.cv_data})
    with st.expander('Application prompt'):
        st.write(application_prompt)

    st.session_state.prompt_refinements = st.text_area(label='Prompt refinements',
                                                        placeholder='Anything you want to add to the prompt',
                                                        value=st.session_state.get('prompt_refinements'))
    if st.button('Create'):
        with st.spinner('Creating Application'):
            c = Conversation(openai_api_key=st.session_state.api_key, response_format="text")
            c.as_user(application_prompt)
            if st.session_state.prompt_refinements:
                c.as_user(st.session_state.prompt_refinements)
            st.session_state.application = c.complete()
    if 'application' in st.session_state:
        st.write(st.session_state.application)
elif 'job_description_json' not in st.session_state:
    st.error('Job not analyzed')
elif 'cv_data' not in st.session_state:
    st.error('CV data not uploaded')
