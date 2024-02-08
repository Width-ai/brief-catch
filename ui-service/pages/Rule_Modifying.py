import os
import re
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

primaryColor = toml.load(".streamlit/config.toml")["theme"]["primaryColor"]
s = f"""
<style>
div.stButton > button:first-child {{ background-color: {primaryColor}; border-radius: 5px; color: #fff;}}
</style>
"""
st.markdown(s, unsafe_allow_html=True)

if "rule_to_modify" not in st.session_state:
    st.session_state["rule_to_modify"] = None

actions = ["Create", "Modify", "Disable", "Split"]
disable_scopes = ["Whole Rule", "Element"]
parent_element_scopes = [
    "Antipattern",
    "Pattern",
    "Message",
    "Suggestion",
    "Short",
    "Example",
]
element_actions = ["Add", "Delete", "Change"]
child_element_scopes = ["---", "Token", "Marker"]
name_regex_pattern = r'name="([^"]*)"'
st.markdown("## Rule Modifying")
st.divider()


def create_pr(rule_name: str, modified_rule: str):
    with st.spinner("Opening Pull Request..."):
        pr_response = requests.post(
            f"{API_URL}/update-rule",
            json={
                "rules_to_update": [
                    {"modified_rule_name": rule_name, "modified_rule": modified_rule}
                ]
            },
        )
        pr_json = pr_response.json()

        if pr_response.ok:
            st.write(f"Created pull request: {pr_json.get('pull_request_link')}")
            st.session_state["modified"] = False
            st.session_state.pop("modified_rule", None)
            st.session_state.pop("usage", None)
        else:
            st.error(f"Error creating PR: {pr_json.get('error')}")


def comment_out_element(
    xml_string: str,
    parent_type: str,
    parent_index: int,
    child_type: str = None,
    child_index: int = 0,
) -> str:
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
        root = etree.fromstring(wrapped_xml_content.encode("utf-8"), parser=parser)
        parents = root.findall(".//{}".format(parent_type))

        if parent_index < 0 or parent_index >= len(parents):
            raise IndexError("Parent index is out of range.")

        parent = parents[parent_index]

        if child_type == "---":
            parent_string = etree.tostring(parent, encoding="unicode")
            comment = etree.Comment(parent_string)
            parent.getparent().replace(parent, comment)
        else:
            children = parent.findall(child_type)
            if child_index < 0 or child_index >= len(children):
                raise IndexError("Element index is out of range.")
            element_to_comment = children[child_index]
            element_string = etree.tostring(element_to_comment, encoding="unicode")
            comment = etree.Comment(element_string)
            parent.replace(element_to_comment, comment)

        modified_rule = root.findall(".//rule")[0]
        return etree.tostring(modified_rule, pretty_print=True, encoding="unicode")
    except etree.XMLSyntaxError as e:
        st.error(f"XML Syntax Error: {e}")
        return None
    except IndexError as e:
        st.error(f"Index error: {e}")
        return None


def add_modification_section():
    """
    Adds modifications to the session state
    """
    st.session_state.modifications.append(
        {"target_element": "", "element_action": "", "specific_actions": ""}
    )


def remove_modification_section(index: int):
    """
    Removes a modification section from the list
    """
    st.session_state.modifications.pop(index)


def save_rule_change(key: str):
    st.session_state["new_rule"] = st.session_state[key]


modification_action = st.selectbox("Action to take:", actions)
if modification_action == "Create":
    st.session_state["modified"] = False
    st.session_state.setdefault("new_rule", "")
    st.write("Create Form")

    # Define the form fields
    with st.form(key="create_rule_form"):
        ad_hoc_syntax = st.text_input("Ad Hoc Syntax")
        rule_number = st.text_input("Rule Number")
        correction = st.text_input("Correction")
        category = st.text_input("Category")
        explanation = st.text_area("Explanation")
        test_sentence = st.text_input("Test Sentence")
        test_sentence_correction = st.text_input("Test Sentence Correction")

        # Form submission button
        submit_button = st.form_submit_button(label="Submit Rule")

    # If the form is submitted, send the data to the API endpoint
    if submit_button:
        st.session_state["form_submitted"] = True
        # Create the JSON object with the correct fields
        json_data = {
            "ad_hoc_syntax": ad_hoc_syntax,
            "rule_number": rule_number,
            "correction": correction,
            "category": category,
            "explanation": explanation,
            "test_sentence": test_sentence,
            "test_sentence_correction": test_sentence_correction,
        }

        # Use st.spinner to indicate loading while waiting for the request to resolve
        with st.spinner("Creating rule... Please wait."):
            try:
                response = requests.post(f"{API_URL}/create-rule", json=json_data)
                if response.status_code == 200:
                    json_response = response.json()
                    st.session_state["modified"] = True
                    st.session_state["new_rule"] = json_response["response"]
                    st.session_state["usage"] = json_response["usage"]
                else:
                    st.error(
                        f"Failed to create rule. Status code: {response.status_code}"
                    )
                    st.error(f"Response body: {response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"An error occurred: {e}")

    if st.session_state.get("form_submitted", False):
        st.session_state["new_rule"] = st.text_area(
            label="New Rule:",
            value=st.session_state["new_rule"],
            key="final_rule_version",
            height=400,
            on_change=save_rule_change,  # Call save_rule_change when the text changes
            args=(
                "final_rule_version",
            ),  # Pass the key of the text area to the callback
        )
        st.markdown(f"Input token count: {st.session_state['usage']['input_tokens']}")
        st.markdown(f"Output token count: {st.session_state['usage']['output_tokens']}")
        st.markdown(f"Cost: {st.session_state['usage']['cost']}")
        if st.button("Update Repo"):
            new_rule_name_match = re.search(
                name_regex_pattern, st.session_state["new_rule"]
            )
            if new_rule_name_match:
                new_rule_name = new_rule_name_match.group(1)
            else:
                new_rule_name = f"BRIEFCATCH_{category.upper()}_{rule_number}"
            create_pr(
                rule_name=new_rule_name, modified_rule=st.session_state["new_rule"]
            )
elif modification_action == "Disable":
    # Initialize session state variables if they don't already exist
    if "rule_to_modify" not in st.session_state:
        st.session_state["rule_to_modify"] = None
    if "modified_rule" not in st.session_state:
        st.session_state["modified_rule"] = None
    if "modified" not in st.session_state:
        st.session_state["modified"] = False
    if "disable_scope" not in st.session_state:
        st.session_state["disable_scope"] = None

    # If 'modified' is True, the modification has already been done, so reset the applicable states
    if st.session_state["modified"]:
        st.session_state["rule_to_modify"] = None
        st.session_state["disable_scope"] = None
        st.session_state["modified_rule"] = None
        st.session_state["modified"] = False

    st.session_state["rule_to_modify"] = st.selectbox(
        "Select rule to disable:",
        list(rules.keys()),
        index=(
            0
            if st.session_state["rule_to_modify"] is None
            else list(rules.keys()).index(st.session_state["rule_to_modify"])
        ),
    )

    with st.expander("Original rule"):
        st.code(rules[st.session_state["rule_to_modify"]])

    st.session_state["disable_scope"] = st.selectbox(
        "What do you want to disable?",
        disable_scopes,
        index=(
            0
            if st.session_state["disable_scope"] is None
            else disable_scopes.index(st.session_state["disable_scope"])
        ),
    )

    if st.session_state["disable_scope"] == "Element":
        element_disable_scope = st.selectbox(
            "Which element type do you want to disable?", parent_element_scopes
        )
        parent_element_index = st.text_input(
            "Enter the index of the parent element you wish to disable:"
        )
        child_element_type = st.selectbox(
            "[Optional] Enter the type of the child element:", child_element_scopes
        )
        child_element_index = st.text_input(
            "[Optional] Enter the index of the child element:"
        )

        if st.button("Disable Element"):
            commented_rule = comment_out_element(
                xml_string=rules[st.session_state["rule_to_modify"]],
                parent_type=element_disable_scope.lower(),
                parent_index=int(parent_element_index),
                child_type=child_element_type.lower(),
                child_index=int(child_element_index) if child_element_index else None,
            )
            st.session_state["modified"] = True
            st.session_state["modified_rule"] = commented_rule
            st.divider()
            st.write("Disabled Rule:")
            st.code(commented_rule)
    else:
        commented_rule = "<!--" + rules[st.session_state["rule_to_modify"]] + "-->"
        st.session_state["modified"] = True
        st.session_state["modified_rule"] = commented_rule
        st.divider()
        st.write("Disabled Rule:")
        st.session_state["modified_rule"] = st.text_area(
            label="Final Modified Rule:",
            value=st.session_state["modified_rule"],
            key="final_rule_version",
            height=400,
        )

    if "modified" in st.session_state and st.session_state["modified"]:
        if st.button("Update Repo"):
            create_pr(
                rule_name=st.session_state["rule_to_modify"],
                modified_rule=st.session_state["modified_rule"],
            )
elif modification_action == "Modify":
    if "modifications" not in st.session_state:
        st.session_state.modifications = []
    st.session_state["modified_rule"] = None
    st.session_state.setdefault("new_rule", "")
    rule_to_modify = st.selectbox("Select rule to modify:", rules.keys())
    with st.expander("Original rule"):
        st.code(rules[rule_to_modify])

    if st.button("Add another modification"):
        add_modification_section()

    # Display the form sections
    for i, modification in enumerate(st.session_state.modifications):
        with st.container():
            st.markdown(f"### Modification {i+1}")
            modification["target_element"] = st.selectbox(
                f"Target Element {i+1}:",
                parent_element_scopes,
                key=f"target_element_{i}",
            )
            modification["element_action"] = st.selectbox(
                f"What do you want to do to the element {i+1}:",
                element_actions,
                key=f"element_action_{i}",
            )
            modification["specific_actions"] = st.text_area(
                f"Specific Actions {i+1}:", key=f"specific_actions_{i}"
            )
            if st.button(f"Remove Modification {i+1}", key=f"remove_modification_{i}"):
                remove_modification_section(i)
                st.experimental_rerun()
    if st.button("Modify") and not st.session_state.get("modified", False):
        st.session_state["modified_rule"] = rules[rule_to_modify]
        if "total_usage" not in st.session_state:
            st.session_state["total_usage"] = {
                "input_tokens": 0,
                "output_tokens": 0,
                "cost": 0,
            }
        for modification in st.session_state.modifications:
            with st.spinner(
                f"Processing Modification {st.session_state.modifications.index(modification)+1}..."
            ):
                response = requests.post(
                    f"{API_URL}/rule-rewriting",
                    json={
                        "target_element": modification["target_element"],
                        "element_action": modification["element_action"],
                        "specific_actions": [modification["specific_actions"]],
                        "original_rule_text": st.session_state["modified_rule"],
                    },
                )
                if response.status_code == 200:
                    json_response = response.json()
                    st.session_state["new_rule"] = json_response[
                        "response"
                    ]  # Update the rule text for the next modification
                    # Update total usage
                    st.session_state["total_usage"]["input_tokens"] += json_response[
                        "usage"
                    ]["input_tokens"]
                    st.session_state["total_usage"]["output_tokens"] += json_response[
                        "usage"
                    ]["output_tokens"]
                    st.session_state["total_usage"]["cost"] += json_response["usage"][
                        "cost"
                    ]
                else:
                    st.error(
                        f"Failed to rewrite rule in Modification {st.session_state.modifications.index(modification)+1}. Please check your inputs and try again."
                    )
                    break  # Exit the loop if there's an error
        if response.status_code == 200:
            st.session_state["modified"] = True

    if st.session_state.get("modified", False):
        st.session_state["new_rule"] = st.text_area(
            label="Final Modified Rule:",
            value=st.session_state["new_rule"],
            key="final_rule_version",
            height=400,
            on_change=save_rule_change,
            args=("final_rule_version",),
        )
        st.markdown(
            f"Input token count: {st.session_state['total_usage']['input_tokens']}"
        )
        st.markdown(
            f"Output token count: {st.session_state['total_usage']['output_tokens']}"
        )
        st.markdown(f"Cost: {st.session_state['total_usage']['cost']}")
        if st.button("Update Repo"):
            with st.spinner("Opening Pull Request..."):
                create_pr(
                    rule_name=rule_to_modify, modified_rule=st.session_state["new_rule"]
                )
elif modification_action == "Split":
    st.session_state.setdefault("new_rule", "")
    rule_to_modify = st.selectbox("Select rule to split:", rules.keys())
    st.session_state["modified_rule"] = rules[rule_to_modify]
    with st.expander("Original rule"):
        st.code(rules[rule_to_modify])

    split_strategies = [
        "Split <or> tag",
        "Rule is too broad",
    ]
    split_strategy = st.selectbox(
        "How would you like to split?",
        split_strategies,
    )
    original_rule = st.session_state["modified_rule"]
    if split_strategy == split_strategies[0]:
        # split: on or
        action = "or"
        additional_considerations = ""
    elif split_strategy == split_strategies[1]:
        # split: rule too broad
        action = "toobroad"
        additional_considerations = st.text_input("Additional Considerations")
    else:
        st.error("Invalid splitting action selected.")
    if st.button("Split"):
        response = requests.post(
            f"{API_URL}/rule-splitting",
            json={
                "target_element": "",
                "element_action": action,
                "specific_actions": [additional_considerations],
                "original_rule_text": original_rule,
            },
        )
        if response.status_code == 200:
            json_response = response.json()
            st.session_state["modified"] = True
            for ix, operand_rule in enumerate(json_response["response"]):
                st.code(operand_rule)
else:
    st.error("Invalid action selected.")
