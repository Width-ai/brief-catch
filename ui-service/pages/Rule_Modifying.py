import os
import requests
import streamlit as st
import toml
from dotenv import load_dotenv
from lxml import etree

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

if 'rule_to_modify' not in st.session_state:
    st.session_state['rule_to_modify'] = None

actions = ['Create', 'Modify', 'Disable']
disable_scopes = ['Whole Rule', 'Element']
parent_element_scopes = ['Antipattern', 'Pattern', 'Suggestion', 'Example']
child_element_scopes = ['---', 'Token', 'Marker']

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


def create_pr(rule_name: str, modified_rule: str):
    with st.spinner("Opening Pull Request..."):
        pr_response = requests.post(
            f"{API_URL}/update-rule",
            json={
                "modified_rule_name": rule_name,
                "modified_rule": modified_rule
            })
        pr_json = pr_response.json()

        if pr_response.ok:
            st.write(f"Created pull request: {pr_json.get('pull_request_link')}")
            st.session_state['modified'] = False
            st.session_state.pop('modified_rule', None)
            st.session_state.pop('usage', None)
        else:
            st.error(f"Error creating PR: {pr_json.get('error')}")


def comment_out_element(xml_string: str, parent_type: str, parent_index: int, child_type: str = None, child_index: int = 0) -> str:
    """
    Function to comment out a specified element in an XML rule using the lxml library

    Returns the modified rule as a string
    """
    try:
        dtd = """
        <!DOCTYPE root [
        <!ENTITY months "January|February|March|April|May|June|July|August|September|October|November|December">
        <!ENTITY abbrevMonths "Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec">
        ]>
        """
        wrapped_xml_content = f"{dtd}<root>{xml_string}</root>"
        parser = etree.XMLParser(resolve_entities=False)
        root = etree.fromstring(wrapped_xml_content.encode('utf-8'), parser=parser)
        parents = root.findall('.//{}'.format(parent_type))

        if parent_index < 0 or parent_index >= len(parents):
            raise IndexError("Parent index is out of range.")

        parent = parents[parent_index]
        
        if child_type == '---':
            parent_string = etree.tostring(parent, encoding='unicode')
            comment = etree.Comment(parent_string)
            parent.getparent().replace(parent, comment)
        else:
            children = parent.findall(child_type)
            if child_index < 0 or child_index >= len(children):
                raise IndexError("Element index is out of range.")
            element_to_comment = children[child_index]
            element_string = etree.tostring(element_to_comment, encoding='unicode')
            comment = etree.Comment(element_string)
            parent.replace(element_to_comment, comment)
        
        modified_rule = root.findall(".//rule")[0]
        return etree.tostring(modified_rule, pretty_print=True, encoding='unicode')
    except etree.XMLSyntaxError as e:
        st.error(f"XML Syntax Error: {e}")
        return None
    except IndexError as e:
        st.error(f"Index error: {e}")
        return None


modification_action = st.selectbox("Action to take:", actions)
if modification_action == "Create":
    st.session_state['modified'] = False
    st.session_state['modified_rule'] = None
    st.write("Create form")
elif modification_action == "Disable":
    # Initialize session state variables if they don't already exist
    if 'rule_to_modify' not in st.session_state:
        st.session_state['rule_to_modify'] = None
    if 'modified_rule' not in st.session_state:
        st.session_state['modified_rule'] = None
    if 'modified' not in st.session_state:
        st.session_state['modified'] = False
    if 'disable_scope' not in st.session_state:
        st.session_state['disable_scope'] = None

    # If 'modified' is True, the modification has already been done, so reset the applicable states
    if st.session_state['modified']:
        st.session_state['rule_to_modify'] = None
        st.session_state['disable_scope'] = None
        st.session_state['modified_rule'] = None
        st.session_state['modified'] = False

    st.session_state['rule_to_modify'] = st.selectbox("Select rule to disable:", list(rules.keys()), index=0 if st.session_state['rule_to_modify'] is None else list(rules.keys()).index(st.session_state['rule_to_modify']))

    with st.expander("Original rule"):
        st.code(rules[st.session_state['rule_to_modify']])

    st.session_state['disable_scope'] = st.selectbox("What do you want to disable?", disable_scopes, index=0 if st.session_state['disable_scope'] is None else disable_scopes.index(st.session_state['disable_scope']))

    if st.session_state['disable_scope'] == "Element":
        element_disable_scope = st.selectbox("Which element type do you want to disable?", parent_element_scopes)
        parent_element_index = st.text_input("Enter the index of the parent element you wish to disable:")
        child_element_type = st.selectbox("[Optional] Enter the type of the child element:", child_element_scopes)
        child_element_index = st.text_input("[Optional] Enter the index of the child element:")

        if st.button("Disable Element"):
            commented_rule = comment_out_element(
                xml_string=rules[st.session_state['rule_to_modify']],
                parent_type=element_disable_scope.lower(),
                parent_index=int(parent_element_index),
                child_type=child_element_type.lower(),
                child_index=int(child_element_index) if child_element_index else None)
            st.session_state['modified'] = True
            st.session_state['modified_rule'] = commented_rule
            st.divider()
            st.write("Disabled Rule:")
            st.code(commented_rule)
    else:
        commented_rule = "<!--" + rules[st.session_state['rule_to_modify']] + "-->"
        st.session_state['modified'] = True
        st.session_state['modified_rule'] = commented_rule
        st.divider()
        st.write("Disabled Rule:")
        st.code(commented_rule)

    if st.session_state['modified']:
        if st.button("Update Repo"):
            create_pr(rule_name=st.session_state['rule_to_modify'], modified_rule=st.session_state['modified_rule'])
else:
    st.session_state['modified'] = False
    st.session_state['modified_rule'] = None
    rule_to_modify = st.selectbox("Select rule to modify:", rules.keys())
    with st.expander("Original rule"):
        st.code(rules[rule_to_modify])

    selected_modification = st.selectbox("Modification:", modifications)
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
                create_pr(rule_name=rule_to_modify, modified_rule=st.session_state['modified_rule'])