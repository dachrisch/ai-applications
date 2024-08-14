import streamlit as st

offer_page = st.Page('steps/offer.py', title='Analyze Job Offer')
application_page = st.Page('steps/application.py', title='Create Application')
cover_letter_page = st.Page('steps/cover.py', title='Create Cover Letter')

pages = [offer_page, application_page, cover_letter_page]
