import string

import streamlit as st

from ai.conversation import Conversation

if 'job_description_json' in st.session_state:
    st.subheader('Application')
    with open('application.prompt', 'r') as ap:
        application_prompt_template = string.Template(ap.read())
    application_prompt = application_prompt_template.safe_substitute(
        {'JOBDESC': st.session_state.job_description_json,
         'CVDATA': st.session_state.cv_data})
    with st.expander('Application prompt'):
        st.write(application_prompt)

    prompt_refinements = st.text_input(label='Prompt refinements', placeholder='Anything you want to add to the prompt')
    if st.button('Create'):
        with st.spinner('Creating Application'):
            c = Conversation(openai_api_key=st.session_state.api_key, response_format="text")
            c.as_user(application_prompt)
            if prompt_refinements:
                c.as_user(prompt_refinements)
            application = c.complete()
        st.write(application)
else:
    st.error('Job not analyzed')
