import requests
import streamlit as st


def fetch_url_content(site_url: str):
    try:
        response = requests.get(site_url)
        with st.expander(f'Fetch {site_url}'):
            st.write(response.text)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return None
