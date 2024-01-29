import io
import os
import pandas as pd
import requests
import streamlit as st
import toml
from dotenv import load_dotenv
from typing import Dict, List

load_dotenv()
API_URL = os.getenv("API_SERVICE_URL", "http://localhost:8000")

st.set_page_config(page_title="BriefCatch Bulk Rule Creation", page_icon="📝")
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
</style>
"""
st.markdown(s, unsafe_allow_html=True)

st.header("Bulk Rule Creation")

def create_pr(rules_to_update: List[Dict]):
    with st.spinner("Opening Pull Request..."):
        payload = {
            "rules_to_update": [
                {
                    "modified_rule_name": rule["rule_name"],
                    "modified_rule": rule["rule"]
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


def display_and_modify_rules(bulk_rules: List[Dict]) -> None:
    with st.form("bulk_rules_form"):
        modified_rules = []
        for i, rule in enumerate(bulk_rules):
            rule_name = st.text_input(f"Rule Name {i+1}", value=rule["rule_name"], key=f"rule_name_{i}")
            rule_response = st.text_area(f"New Rule {i+1}", value=rule["rule"], key=f"rule_response_{i}", height=175)
            modified_rules.append({
                "rule_name": rule_name,
                "rule": rule_response
            })
        submitted = st.form_submit_button("Save Modifications")
        if submitted:
            st.session_state['bulk_rules'] = modified_rules
            st.success("Modifications saved!")


def display_csv(uploaded_file) -> pd.DataFrame:
    # Read the CSV file into a Pandas DataFrame
    df = pd.read_csv(uploaded_file)
    # Display the DataFrame as a table in Streamlit
    st.write(df)
    return df


uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    df = display_csv(uploaded_file)
    if st.button('Send to API'):
        st.session_state['have_result'] = False
        st.session_state['bulk_rules'] = [{}]
        with st.spinner('Performing bulk creations...'):
            try:
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False)
                csv_buffer.seek(0)
                files = {'csv_file': (uploaded_file.name, csv_buffer, 'text/csv')}
                response = requests.post(
                    f"{API_URL}/bulk-rule-creation",
                    files=files
                )
                result = response.json()
                
                # Check if the request was successful
                if response.status_code == 200:
                    st.success('Successfully performed batch modification')
                    st.session_state['bulk_rules'] = result["results"]
                    st.session_state['have_result'] = True
                else:
                    st.error(f'Error calling API endpoint. Status code: {response.status_code}. Text: {result.get("errors")}')
            except Exception as e:
                st.error(f'An error occurred: {e}')


if st.session_state.get("have_result", False):
    display_and_modify_rules(st.session_state.get("bulk_rules"))

    if st.button("Open PR"):
        create_pr(st.session_state.get("bulk_rules"))