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

st.set_page_config(page_title="BriefCatch Bulk ngram Analysis", page_icon="📝")
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

st.header("Bulk NGRAM Analysis")


def display_csv(uploaded_file) -> pd.DataFrame:
    # Read the CSV file into a Pandas DataFrame
    df = pd.read_csv(uploaded_file)
    # Display the DataFrame as a table in Streamlit
    st.write(df)
    return df


uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    df = display_csv(uploaded_file)
    if st.button('Perform Analysis'):
        st.session_state['have_result'] = False
        st.session_state['ngram_analysis'] = [{}]
        with st.spinner('Performing bulk ngram analysis...'):
            try:
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False)
                csv_buffer.seek(0)
                files = {'csv_file': (uploaded_file.name, csv_buffer, 'text/csv')}
                response = requests.post(
                    f"{API_URL}/bulk-ngram-analysis",
                    files=files
                )
                result = response.json()
                
                # Check if the request was successful
                if response.status_code == 200:
                    st.success('Successfully performed bulk ngram analysis')
                    st.session_state['ngram_analysis'] = result["results"]
                    st.session_state['have_result'] = True
                else:
                    st.error(f'Error calling API endpoint. Status code: {response.status_code}. Text: {result.get("errors")}')
            except Exception as e:
                st.error(f'An error occurred: {e}')


if st.session_state.get("have_result", False):
    st.json(st.session_state.get("ngram_analysis"))

    # Button to download the Excel file
    if st.button('Create Excel File'):
        with st.spinner('Generating Excel File...'):
            try:
                # Send the JSON data to the FastAPI endpoint
                response = requests.post(
                    f"{API_URL}/generate-excel",
                    json=st.session_state.get("ngram_analysis")
                )
                
                # Check if the request was successful
                if response.status_code == 200:
                    # Write the received Excel file to a temporary file
                    with open("analysis.xlsx", "wb") as f:
                        f.write(response.content)
                    
                    # Provide a download button for the Excel file
                    with open("analysis.xlsx", "rb") as f:
                        st.download_button(
                            label="Download Excel file",
                            data=f,
                            file_name="ngram_analysis.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                else:
                    st.error(f'Error generating Excel file. Status code: {response.status_code}')
            except Exception as e:
                st.error(f'An error occurred: {e}')