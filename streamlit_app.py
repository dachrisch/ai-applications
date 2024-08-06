import json
import re
from typing import List

import pandas as pd
import streamlit as st
from attr import define
from bs4 import BeautifulSoup
from cattrs import unstructure, structure
from openai import OpenAI

from ai.validate import is_valid_openai_key
from web.fetch import fetch_url_content


def analyze_content_for_job_offers(website_code, openai_key):
    client = OpenAI(api_key=openai_key)
    links = scan_links(website_code)
    prompt = (
        'check the list of links for any, that refer to job offers, like career or jobs: '
        f'\n\n {links}. \n\n'
        'If multiple links refer to the same page, only output the first link.'
        'Also exclude links containing social media or job aggregators like'
        'linkedin, xing, facebook or stellenanzeigen.de.'
        'Output the possible links as json list like:'
        '{"links":[{'
        '"title": <link_title>,'
        '"url": <link_url>'
        '}]}')
    with st.expander('Prompt'):
        st.write(prompt)
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
        )
        model_answer = chat_completion.choices[0].message.content
        with st.expander('Model Answer'):
            st.write(model_answer)
        job_links = structure(json.loads(model_answer)['links'], List[Link])

        if job_links:
            job_link = job_links[0]
            with st.spinner(f'Checking {job_link}'):
                st.markdown(f'### [{job_link.title}]({job_link.url})')
                job_offers = check_for_job_offers(job_link, openai_key)
            return job_offers
        else:
            return 'No jobs available'
    except Exception as e:
        st.error(f"Error analyzing content with OpenAI: {e}")
        return None


@define
class Link:
    title: str
    url: str


@define
class SearchResults:
    links: list[Link] = []


def check_for_job_offers(job_link: Link, openai_key: str):
    job_content = fetch_url_content(job_link.url)
    client = OpenAI(api_key=openai_key)
    prompt = (
        'check the website content for any job offers: '
        f'\n\n {job_content}. \n\n'
        'If no job offers are found, return "no offers found".'
        'Return found offers with the job title, job description and a link to the details')
    with st.expander(f'Prompt - {job_link}'):
        st.write(prompt)
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="gpt-4o-mini",
        )
        model_answer = chat_completion.choices[0].message.content
        with st.expander('Model Answer'):
            st.write(model_answer)

        return model_answer
    except Exception as e:
        st.error(f"Error analyzing content with OpenAI: {e}")
        return None


def map_link(link_element):
    title = ''
    if link_element.text:
        findall = re.findall(r'\S+', link_element.text)
        if len(findall) > 0:
            title = findall[0]
        else:
            title = link_element.text
    url = link_element.attrs['href']
    return Link(title=title, url=url)


def scan_links(site_content):
    try:
        soup = BeautifulSoup(site_content, 'html.parser')
        return SearchResults(
            list(filter(lambda l: l.title != '', map(map_link, soup.find_all('a', href=True, target="_blank")))))
    except Exception as e:
        st.error(f"Error performing Google search: {e}")
        return []



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

st.title("Job Offer Analyzer")

site = st.text_input("Enter a site to scan for links:")
if st.button("Scan"):
    if site:
        with st.spinner('Scanning'):
            st.session_state.page_content = unstructure(scan_links(fetch_url_content(site)))
    else:
        st.error("Please enter a search query.")

if 'search_results' in st.session_state and st.session_state.page_content:
    search_results = structure(st.session_state.page_content, SearchResults)
    st.write("Select one or more results to analyze:")
    if "df" not in st.session_state:
        st.session_state.df = pd.DataFrame(
            {
                'title': map(lambda x: x.title, search_results.links),
                'link': map(lambda x: x.url, search_results.links)
            }
        )

    event = st.dataframe(
        st.session_state.df,
        height=600,
        hide_index=True,
        column_config={
            'title': 'Title',
            'link': st.column_config.LinkColumn('Link')
        },
        on_select='rerun',
        selection_mode=['multi-row'],
    )
    st.session_state.selected_links = unstructure(
        list(map(lambda s: search_results.links[s], event.selection['rows'])))
    if st.button('Clear results'):
        del st.session_state.page_content
        st.rerun()

    if st.session_state.selected_links:
        if not is_valid_openai_key(st.session_state.api_key):
            st.error('You need an OpenAI key to proceed')
        elif st.button('Analyze'):
            with st.spinner('Analyzing results'):
                for link in structure(st.session_state.selected_links, List[Link]):
                    with st.spinner(f"Analyzing: {link.title}"):
                        content = fetch_url_content(link.url)
                        st.markdown(f'## [{link.title}]({link.url})')
                        if content:
                            result = analyze_content_for_job_offers(content, st.session_state.api_key)
                            if result:
                                st.success(f"Analysis Complete for {link}")
                                st.write(result)
                            else:
                                st.error(f"No response from the analysis for {link}.")
                        else:
                            st.error(f"Could not fetch content from {link}.")
