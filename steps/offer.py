import streamlit as st

from ai.conversation import Conversation
from ai.validate import is_valid_openai_key
from web.fetch import fetch_url_content

url_tab, content_tab = st.tabs(['From URL', 'From Content'])
with url_tab:
    st.subheader('Job Offer')
    st.session_state.site = st.text_input("Enter site with job offer", placeholder='Enter url with job description',
                                          value=st.session_state.get('site'))
    st.session_state.site_content=fetch_url_content(st.session_state.site)
with content_tab:
    st.subheader('Job Offer')
    st.session_state.site_content = st.text_area("Paste site content with job offer",
                                                 placeholder='Copy & Paste the site content here',
                                                 value=st.session_state.get('site_content'))

if not is_valid_openai_key(st.session_state.api_key):
    st.error('You need an OpenAI key to proceed')
elif st.button("Analyze"):
    if st.session_state.site_content:
        with st.spinner('Analyzing'):

            c = Conversation(openai_api_key=st.session_state.api_key)
            system_prompt = ('Analyze the content of this webpage and find the job description. '
                             'if no job description is found, return empty json as {}'
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
            user_prompt = f'The web page content is: {st.session_state.site_content}'
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
