import os
import requests
import streamlit as st
import toml
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_SERVICE_URL", "http://localhost:8000")

rules = requests.get(f"{API_URL}/list-rules").json().get("rules")

st.set_page_config(page_title="BriefCatch Rule Modifying", page_icon="📝")
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

modifications = ['Antipattern',
                   'Add exception to token',
                   'Change final token so it requires one of these words',
                   'Add token at end requiring one of these words',
                   'Change second token',
                   'Add tokens before and after',
                   'Exclude from initial token',
                   'Exclude from first token',
                   'Antipatterns',
                   'Add required tokens both before and after the string',
                   'Exclude from final token',
                   'Exclude from second token']

st.markdown("## Rule Modifying")
st.divider()

selected_modification = st.selectbox("Modification:", modifications)
rule_to_modify = st.selectbox("Select rule to modify:", rules.keys())
with st.expander("Original rule"):
    st.code(rules[rule_to_modify])
specific_actions = st.text_area("Specific Actions:")


if st.button("Modify") and not st.session_state.get('modified', False):
    with st.spinner("Rewriting Rule..."):
        response = requests.post(f"{API_URL}/rule-rewriting",
                                 json={"selected_modification": selected_modification,
                                       "specific_actions": [specific_actions],
                                       "original_rule_text": rules[rule_to_modify]})
        
        if response.status_code == 200:
            json_response = response.json()
            st.session_state['modified'] = True
            st.session_state['modified_rule'] = json_response["response"]
            st.session_state['usage'] = json_response['usage']
            st.write("Modified Rule:")
            st.code(st.session_state['modified_rule'], language="xml-doc")
            st.markdown(f"Input token count: {st.session_state['usage']['input_tokens']}")
            st.markdown(f"Output token count: {st.session_state['usage']['output_tokens']}")
            st.markdown(f"Cost: {st.session_state['usage']['cost']}")
        else:
            st.error("Failed to rewrite rule. Please check your inputs and try again.")


if 'modified' in st.session_state and st.session_state['modified']:
    if st.button("Update Repo"):
        with st.spinner("Opening Pull Request..."):
            pr_response = requests.post(f"{API_URL}/update-rule",
                                        json={
                                            "modified_rule_name": rule_to_modify,
                                            "modified_rule": st.session_state['modified_rule']
                                        })
            pr_json = pr_response.json()

            if pr_response.ok:
                st.write(f"Created pull request: {pr_json.get('pull_request_link')}")
                # Reset or clear the session state after the pull request is created, if necessary.
                st.session_state['modified'] = False
                st.session_state.pop('modified_rule', None)
                st.session_state.pop('usage', None)
            else:
                st.error(f"Error creating PR: {pr_json.get('error')}")