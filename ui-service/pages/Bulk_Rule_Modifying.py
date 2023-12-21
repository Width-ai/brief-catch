import os
import requests
import streamlit as st
import toml
from dotenv import load_dotenv
from typing import Dict, List

load_dotenv()
API_URL = os.getenv("API_SERVICE_URL", "http://localhost:8000")

st.set_page_config(page_title="BriefCatch Bulk Rule Modifying", page_icon="📝")
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


def create_pr(rules_to_update: List[Dict]):
    with st.spinner("Opening Pull Request..."):
        payload = {
            "rules_to_update": [
                {
                    "modified_rule_name": rule["original_rule_name"],
                    "modified_rule": rule["response"]
                } for rule in rules_to_update
            ]
        }
        pr_response = requests.post(
            f"{API_URL}/update-rule",
            json=payload)
        pr_json = pr_response.json()

        if pr_response.ok:
            st.write(f"Created pull request: {pr_json.get('pull_request_link')}")
        else:
            st.error(f"Error creating PR: {pr_json.get('error')}")



uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    if st.button('Send to API'):
        st.session_state['have_result'] = False
        st.session_state['bulk_rules'] = [{}]
        with st.spinner('Performing bulk modifications...'):
            try:
                files = {'csv_file': (uploaded_file.name, uploaded_file, 'text/csv')}
                response = requests.post(
                    f"{API_URL}/bulk-rule-rewriting",
                    files=files
                )
                
                # Check if the request was successful
                if response.status_code == 200:
                    st.success('Successfully performed batch modification')
                    result = response.json()
                    st.session_state['bulk_rules'] = result["results"]
                    st.session_state['have_result'] = True
                else:
                    st.error(f'Error calling API endpoint. Status code: {response.status_code}. Text: {response.text}')
            except Exception as e:
                st.error(f'An error occurred: {e}')


if st.session_state.get("have_result", False):
    st.json(st.session_state.get("bulk_rules"))

    if st.button("Open PR"):
        create_pr(st.session_state.get("bulk_rules"))