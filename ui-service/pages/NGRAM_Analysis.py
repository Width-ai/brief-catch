import json
import os
import requests
import streamlit as st
import toml
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_SERVICE_URL", "http://localhost:8000")

st.set_page_config(page_title="BriefCatch ngram Analysis", page_icon="📝")
hide_default_format = """
<style>
.stDeployButton {visibility: hidden;}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_default_format, unsafe_allow_html=True)

primaryColor = toml.load(".streamlit/config.toml")['theme']['primaryColor']
s = f"""
<style>
div.stButton > button:first-child {{ background-color: {primaryColor}; border-radius: 5px; color: #fff;}}
<style>
"""
st.markdown(s, unsafe_allow_html=True)


with st.form(key='ngram_form'):
    text_input = st.text_area("Enter rule for ngram analysis:", height=200)
    submit_button = st.form_submit_button(label='Analyze')

if submit_button:
    with st.spinner('Analyzing...'):
        try:
            ngram_analysis = requests.post(
                f"{API_URL}/ngram-analysis",
                json={"rule_text": text_input}
            )
            ngram_analysis.raise_for_status()
            response_data = ngram_analysis.json()
            st.code(json.dumps(response_data, indent=4), language="json")
        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred: {e}")