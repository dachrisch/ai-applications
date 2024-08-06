import streamlit as st

from ai.conversation import Conversation
from ai.validate import is_valid_openai_key
from web.fetch import fetch_url_content

st.subheader('Job Offer')
st.session_state.site = st.text_input("Enter site with job offer", placeholder='Enter url with job description',
                                      value=st.session_state.get('site'))

if not is_valid_openai_key(st.session_state.api_key):
    st.error('You need an OpenAI key to proceed')
elif st.button("Analyze"):
    if st.session_state.site:
        with st.spinner('Analyzing'):
            page_content = fetch_url_content(st.session_state.site)

            c = Conversation(openai_api_key=st.session_state.api_key)
            system_prompt = ('Analyze the content of this webpage and find the job description. '
                             'if no job description is found, return empty json'
                             'if a job description is found, respond with'
                             '{'
                             '"job":{'
                             '"title": <job title>,'
                             '"about": <all infos about the company and general job description>,'
                             '"company_name": <name of the company>,'
                             '"requirements": <all infos about required skills>,'
                             '"responsibilities": <all infos about the tasks and responsibilities of this role>,'
                             '"offers": <what the company is offering in this position>,'
                             '"additional": <all additional infos not covered before>'
                             '}'
                             '}')
            user_prompt = f'The web page content is: {page_content}'
            with st.expander('Prompt'):
                st.write(system_prompt)
                st.write(user_prompt)
            st.session_state.job_description_json = c.as_system(system_prompt).as_user(user_prompt).complete()
    else:
        st.error("Please enter site.")

if 'job_description_json' in st.session_state:
    with st.expander('Model Answer'):
        st.write(st.session_state.job_description_json)
    if not st.session_state.job_description_json:
        st.error("Couldn't find job description")
    else:
        st.markdown(f'''
    ### Title: {st.session_state.job_description_json['job']['title']}
#### {st.session_state.job_description_json['job']['company_name']}
### About
{st.session_state.job_description_json['job']['about']}
### Requirements
{st.session_state.job_description_json['job']['requirements']}
### Responsibilities
{st.session_state.job_description_json['job']['responsibilities']}
### Offers
{st.session_state.job_description_json['job']['offers']}
### Extra
{st.session_state.job_description_json['job']['additional']}
    ''')
