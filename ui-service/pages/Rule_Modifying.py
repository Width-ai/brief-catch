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
st.code(rules[rule_to_modify])
specific_actions = st.text_area("Specific Actions:")
if st.button("Modify"):
    with st.spinner("Calling rule rewriting..."):
        response = requests.post(f"{API_URL}/rule-rewriting",
                                 json={"selected_modification": selected_modification,
                                       "specific_actions": [specific_actions],
                                       "original_rule_text": rules[rule_to_modify]})
        json_response = response.json()
        st.write("Modified Rule:")
        st.code(json_response["response"], language="xml-doc")
        st.markdown(f"Input token count: {json_response['usage']['input_tokens']}")
        st.markdown(f"Output token count: {json_response['usage']['output_tokens']}")
        st.markdown(f"Cost: ${json_response['usage']['cost']}")
