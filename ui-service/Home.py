import json
import os
import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_SERVICE_URL", "http://localhost:8000")

st.set_page_config(page_title="Brief Catch Test UI", page_icon="📝")
hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)

st.title("Text Rewriting")
st.divider()

# Endpoint 1
st.subheader("**/topic-sentence Endpoint**")
topic_sentence_text = st.text_input("Input String for /topic-sentence endpoint")
if st.button("Call /topic-sentence Endpoint"):
    with st.spinner("Calling /topic-sentence..."):
        response = requests.post(f"{API_URL}/topic-sentence", 
                                 json={"input_text": topic_sentence_text})
        st.write("Response:", response.json())
st.divider()

# Endpoint 2
st.subheader("**/quotations Endpoint**")
quotations_text = st.text_input("Input String for /quotations endpoint")
if st.button("Call /quotations Endpoint"):
    with st.spinner("Calling /quotations..."):
        response = requests.post(f"{API_URL}/quotations",
                                 json={"input_text": quotations_text})
        st.write("Response:", response.json())
st.divider()

# Endpoint 3
st.subheader("**/parentheses-rewriting Endpoint**")
parentheses_text = st.text_input("Input List of strings for /parentheses-rewriting endpoint")
if st.button("Call /parentheses-rewriting Endpoint"):
    with st.spinner("Calling /parentheses-rewriting..."):
        response = requests.post(f"{API_URL}/parentheses-rewriting",
                                 json={"input_texts": parentheses_text.split(",")})
        st.write("Response:", response.json())