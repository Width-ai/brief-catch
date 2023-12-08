import os
import requests
import streamlit as st
import toml
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_SERVICE_URL", "http://localhost:8000")

st.set_page_config(page_title="Brief Catch Test UI", page_icon="📝")
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



st.markdown("# ContentCatch")
st.divider()

# Endpoint 1
st.markdown("## ParagraphCatch")
topic_sentence_text = st.text_input("Share a Paragraph!")
if st.button("Call ParagraphCatch"):
    with st.spinner("Calling ParagraphCatch..."):
        response = requests.post(f"{API_URL}/topic-sentence", 
                                 json={"input_text": topic_sentence_text})
        paragraph_catch_response = response.json()
        st.write("ParagraphCaught!")
        st.markdown(f"### New Paragraph Opener:\n{paragraph_catch_response['revised_topic_sentence']}")
        st.markdown(f"### BriefCaught Thoughts:\n{paragraph_catch_response['analysis']}")
        st.markdown(f"Input token count: {paragraph_catch_response['usage']['input_tokens']}")
        st.markdown(f"Output token count: {paragraph_catch_response['usage']['output_tokens']}")
        st.markdown(f"Cost: ${paragraph_catch_response['usage']['cost']}")
st.divider()

# Endpoint 2
st.markdown("## QuotationCatch")
quotations_text = st.text_input("Share a Quotation!")
if st.button("Call QuotationCatch"):
    with st.spinner("Calling QuotationCatch..."):
        response = requests.post(f"{API_URL}/quotations",
                                 json={"input_text": quotations_text})
        quotation_catch_response = response.json()
        st.write("QuotationCaught!")
        st.markdown(f"### New Quotation Lead-In:\n{quotation_catch_response['response']}")
        st.markdown(f"Input token count: {quotation_catch_response['usage']['input_tokens']}")
        st.markdown(f"Output token count: {quotation_catch_response['usage']['output_tokens']}")
        st.markdown(f"Cost: ${quotation_catch_response['usage']['cost']}")

st.divider()

# Endpoint 3
st.markdown("## ParentheticalCatch")
parentheses_text = st.text_input("Share a Parenthetical!")
if st.button("Call ParentheticalCatch"):
    with st.spinner("Calling ParentheticalCatch..."):
        response = requests.post(f"{API_URL}/parentheses-rewriting",
                                 json={"input_texts": parentheses_text.split(",")})
        parenthetical_catch_response = response.json()
        st.markdown(f"### New Parenthetical(s):")
        for pair in parenthetical_catch_response["response"]:
            st.write(f"**Parenthetical Caught:** {pair['input_text']}")
            st.write(f"**New Parenthetical:** {pair['output_text']}")
        st.markdown(f"Input token count: {parenthetical_catch_response['usage']['input_tokens']}")
        st.markdown(f"Output token count: {parenthetical_catch_response['usage']['output_tokens']}")
        st.markdown(f"Cost: ${parenthetical_catch_response['usage']['cost']}")