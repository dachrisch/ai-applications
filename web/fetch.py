import requests
import streamlit as st


def fetch_url_content(site_url: str):
    response = requests.get(site_url)
    with st.expander(f'Fetch {site_url}'):
        st.write(response.text)
    response.raise_for_status()
    return response.text
