import json
import backoff
import math
import openai
import os
import pandas as pd
import pinecone
import re
import tiktoken
from collections import defaultdict
from github import Github, Repository, GithubException
from lxml import etree
from typing import List, Tuple, Dict
from uuid import uuid4
from word_embeddings_sdk import WordEmbeddingsSession
from domain.prompts import (
    SENTENCE_RANKING_SYSTEM_PROMPT,
    PARENTHESES_REWRITING_PROMPT,
    NEW_CREATE_RULE_FROM_ADHOC_SYSTEM_PROMPT,
    DYNAMIC_RULE_CHECKING_PROMPT
)
from domain.models import RuleToUpdate
from domain.modifier_prompts import RULE_USER_TEXT_TEMPLATE
from domain.modifier_prompts.common_instructions import (
    STANDARD_PROMPT,
    OPTIMIZED_STANDARD_PROMPT,
)
from utils.logger import setup_logger
from utils.regexp_validation import post_process_xml
from utils.rule_rewrite_prompt import get_dynamic_standard_prompt

pricing = json.load(open("pricing.json"))
utils_logger = setup_logger(__name__)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
FILENAME = os.getenv("RULE_FILENAME", "grammar.xml")
session = WordEmbeddingsSession(
    customer_id=os.getenv("EMBEDDINGS_SAAS_ID"),
    api_key=os.getenv("EMBEDDINGS_SAAS_API_KEY"),
)
pinecone_indexes = {}


def compute_cost(usage: Dict[str, int], model: str) -> float:
    prices = pricing[model]
    return (
        prices["prompt"] * usage["input_tokens"] / 1000
        + prices["completion"] * usage["output_tokens"] / 1000
    )


def generate_simple_message(system_prompt: str, user_prompt: str) -> List[dict]:
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


@backoff.on_exception(backoff.expo, openai.error.OpenAIError, logger=utils_logger)
def call_gpt_with_backoff(
    messages: List,
    model: str = "gpt-4",
    temperature: float = 0.7,
    max_length: int = 256,
) -> Tuple[str, Dict]:
    """
    Generic function to call GPT4 with specified messages
    """
    return call_gpt(
        model=model, messages=messages, temperature=temperature, max_length=max_length
    )


def call_gpt(
    model: str,
    messages: List,
    temperature: float = 0.7,
    max_length: int = 256,
    response_format="text",
) -> Tuple[str, Dict]:
    """
    Generic function to call GPT4 with specified messages
    """
    response = openai.ChatCompletion.create(
        response_format={"type": response_format},
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_length,
        frequency_penalty=0.0,
        top_p=1,
    )
    usage = {
        "input_tokens": response["usage"]["prompt_tokens"],
        "output_tokens": response["usage"]["completion_tokens"],
    }
    usage["cost"] = compute_cost(usage, model)
    return response["choices"][0]["message"]["content"], usage


def combine_all_usages(all_usages: List[Dict]) -> Dict:
    """
    Use dictionary comprehension to sum the values of identical keys
    """
    return {
        key: sum(d.get(key, 0) for d in all_usages) for key in set().union(*all_usages)
    }


def convert_log_probs_to_percentage(log_probs: dict) -> dict:
    """
    Calculate the exponent of each value to get probabilities
    Add them all up to use as the denominator
    Convert to percent
    """
    probs = {k: math.exp(v) for k, v in log_probs.items()}
    total_prob = sum(probs.values())
    percentages = {k: (v / total_prob) * 100 for k, v in probs.items()}
    return percentages


def call_gpt3(
    prompt: str, temperature: float = 0.7, max_tokens: int = 2
) -> Tuple[List[dict], Dict]:
    """
    Call GPT3 to generate text
    """
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=1,
        n=1,
        stop=["###"],
        logprobs=5,
    )
    usage = {
        "input_tokens": response["usage"]["prompt_tokens"],
        "output_tokens": response["usage"]["completion_tokens"],
    }
    responses = []
    if len(response.get("choices")) > 0:
        top_probs = response["choices"][0]["logprobs"]["top_logprobs"]
        for top_prob in top_probs:
            responses.append(convert_log_probs_to_percentage(top_prob))
    usage["cost"] = compute_cost(usage, "text-davinci-003")
    return responses, usage


def rank_sentence(
    sentence_number: str, rule_number: str, text: str, corrected_text: str
) -> dict:
    try:
        sentence_data = "\t".join([sentence_number, text, corrected_text])
        messages = generate_simple_message(
            system_prompt=SENTENCE_RANKING_SYSTEM_PROMPT, user_prompt=sentence_data
        )

        # if length of messages is more than token limit
        response, usage = call_gpt_with_backoff(messages=messages, temperature=0)

        # split the response on the first comma
        response_parts = response.split(",", 1)

        return {
            "sentence_number": sentence_number,
            "rule_number": rule_number,
            "text": text,
            "corrected_text": corrected_text,
            "ranking": response_parts[1].strip(),
            "usage": usage,
        }
    except Exception as e:
        utils_logger.error(f"Error ranking sentence: {e}")
        utils_logger.exception(e)


def num_tokens_from_string(string: str, model_name: str = "gpt-4") -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(model_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def call_gpt_for_parentheses(input_text: str) -> Tuple[List[str], Dict]:
    """
    Call gpt with params for parentheses editing
    """
    messages = generate_simple_message(
        system_prompt=PARENTHESES_REWRITING_PROMPT, user_prompt=input_text
    )
    result, usage = call_gpt_with_backoff(
        messages=messages, temperature=0, max_length=2048
    )
    return result.split("\n"), usage


def rewrite_parentheses_helper(input_data: List[str]) -> Tuple[List[dict], Dict]:
    """
    Rewrite sentences based on criteria
    """
    # calculate max size per chunk for processing
    SYS_NUM_TOKENS = num_tokens_from_string(PARENTHESES_REWRITING_PROMPT)
    REMAINING_TOKENS = 2000 - SYS_NUM_TOKENS
    max_input_size = REMAINING_TOKENS / (
        1 + 1.1
    )  # Adjust this to keep input and output under 2048 tokens.

    input_text = ""
    output_data = []
    curr_chunk_input_data = []
    usages = []
    for line in input_data:
        line = line.replace(",,", "")
        line = line.strip()
        if not line:  # Skip empty lines
            continue
        line_token_count = num_tokens_from_string(line)
        if line_token_count > max_input_size:
            raise ValueError("Single line exceeds max token count.")

        curr_chunk_input_data.append(line)
        if num_tokens_from_string(input_text + line) <= max_input_size:
            input_text += line + "\n"  # add newline character at end of each line.
        else:
            result_list, usage = call_gpt_for_parentheses(input_text=input_text)
            output_data.extend(
                [
                    {"input_text": input, "output_text": output}
                    for input, output in zip(curr_chunk_input_data, result_list)
                ]
            )
            # Start a new input text with the current line
            input_text = line + "\n"  # add newline character at end of each line.
            curr_chunk_input_data = [line]
            usages.append(usage)

    # if we didnt hit token limit
    if input_text:
        result_list, usage = call_gpt_for_parentheses(input_text=input_text)
        output_data.extend(
            [
                {"input_text": input, "output_text": output}
                for input, output in zip(curr_chunk_input_data, result_list)
            ]
        )
        usages.append(usage)
    total_usage = defaultdict(float)
    for usage in usages:
        for key, value in usage.items():
            total_usage[key] += value
    return output_data, total_usage


def parse_rules_from_xml(xml_content: str) -> Dict:
    """
    Parse rules from XML content and store them in a dictionary.
    :param xml_content: str - The content of the XML file
    :return: dict - A dictionary with rule names as keys and full rules as values
    """
    # Parse the XML content
    # TODO: the source file needs to include these
    dtd = """
    <!DOCTYPE root [
    <!ENTITY months "January|February|March|April|May|June|July|August|September|October|November|December">
    <!ENTITY abbrevMonths "Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec">
    ]>
    """
    wrapped_xml_content = f"{dtd}<root>{xml_content}</root>"

    parser = etree.XMLParser(resolve_entities=True)
    root = etree.fromstring(wrapped_xml_content.encode("utf-8"), parser=parser)

    rules_dict = {}

    for rule in root.xpath(".//rule"):
        rule_name = rule.get("name")
        rule_str = etree.tostring(rule, encoding="unicode", pretty_print=True)
        # NOTE: we want to remove alias whenever a rule gets passed to gpt. @abeukers: I did some manual combing through the codebase and calling it once here seems to provide full coverage of examples I detected; anytime a rule is pulled frmo the from grammar.xml its done through `pull_xml_from_github` which calls this.
        rules_dict[rule_name] = resolve_alias_in_suggestion(rule_str.rstrip())

    return rules_dict


def pull_xml_from_github() -> Dict:
    """
    Pull a specified file from a private GitHub repository.
    :param token: str - Your personal GitHub access token
    :param repo_name: str - Full name of the repository (e.g., "username/repo")
    :param file_path: str - Path to the XML file within the repository (e.g., "path/to/grammar.xml")
    :return: dict - The rules with the name as the key and the rule as the value
    """
    g = Github(GITHUB_TOKEN)

    try:
        repo = g.get_repo(GITHUB_REPO)
        file_content = repo.get_contents(FILENAME)
        xml_content = file_content.decoded_content.decode("utf-8")
        rules_dict = parse_rules_from_xml(xml_content)
        return rules_dict
    except Exception as e:
        utils_logger.error(f"An error occurred: {e}")
        utils_logger.exception(e)
        return None


def fetch_rule_by_id(rule_id: str) -> Tuple[str, str]:
    """
    Search for rule by given ID, this is not the long form ID in the rule, but the short id in the name
    """
    rule_dict = pull_xml_from_github()
    for rule_name in rule_dict.keys():
        if rule_name.endswith(f"_{rule_id}"):
            return rule_dict.get(rule_name), rule_name
    return None, ""


def rewrite_rule_helper(
    original_rule: str,
    target_element: str,
    element_action: str,
    specific_actions: List[str] = [],
    use_dynamic_prompt: bool = True,
) -> Tuple[str, Dict]:
    """
    Calls GPT with the corresponding system prompt and the user text formatted
    """
    # get correct system prompt
    if use_dynamic_prompt:
        action_system_prompt = get_dynamic_standard_prompt(
            original_rule,
            target_element,
            element_action,
            specific_actions,
        )
    else:
        action_system_prompt = OPTIMIZED_STANDARD_PROMPT

    # format user text
    user_text = RULE_USER_TEXT_TEMPLATE.replace(
        "{{origininal_rule_text}}", original_rule
    )
    user_text = user_text.replace("{{target_element}}", target_element)
    user_text = user_text.replace("{{element_action}}", element_action)
    user_text = user_text.replace(
        "{{list of specific modifications}}", "\n".join(specific_actions)
    )

    messages = generate_simple_message(
        system_prompt=action_system_prompt, user_prompt=user_text
    )

    return call_gpt_with_backoff(
        messages=messages, model="gpt-4-1106-preview", temperature=0, max_length=1500
    )


def resolve_alias_in_suggestion(rule_xml):
    suggestion_tag_pattern = r"<suggestion>.*?</suggestion>"
    suggest_tags = re.findall(suggestion_tag_pattern, rule_xml)
    for old_suggest in suggest_tags:
        pattern = r"\\\b([1-9][0-9]?|100)\b"
        # print(1, old_suggest)
        new_suggest = re.sub(
            pattern, lambda x: f"""<match no="{x[0][1:]}"/>""", old_suggest
        )
        rule_xml = rule_xml.replace(old_suggest, new_suggest)
        # print(2, new_suggest)
    return rule_xml


def create_new_branch(repo: Repository, branch_name: str):
    """
    Tries to create a branch, if it already exists logs a warning
    """
    try:
        main_branch_ref = repo.get_git_ref("heads/main")
        repo.create_git_ref(
            ref="refs/heads/" + branch_name, sha=main_branch_ref.object.sha
        )
    except Exception as e:
        utils_logger.warning("Branch with same name likely exists...")
        utils_logger.exception(e)


def create_unique_branch(repo: Repository, base_branch_name: str) -> str:
    """
    Creates a new branch with a unique name by appending a number if needed.
    """
    branch_name = base_branch_name
    counter = 1
    while True:
        try:
            repo.get_branch(branch_name)
            # If the branch exists, append/increment the counter and try again
            branch_name = f"{base_branch_name}_{counter}"
            counter += 1
        except GithubException:
            # If the branch does not exist, we can use this name
            break
    create_new_branch(repo=repo, branch_name=branch_name)
    return branch_name


def update_rule_helper(rules_to_update: List[RuleToUpdate]) -> str:
    """
    Updates a rule in the grammar.xml file and creates a pull request
    """
    g = Github(GITHUB_TOKEN)

    try:
        repo = g.get_repo(GITHUB_REPO)
        file_content = repo.get_contents(FILENAME)
        xml_content = file_content.decoded_content.decode("utf-8")
        rules_dict = parse_rules_from_xml(xml_content)

        # update the rule
        if len(rules_to_update) == 1:
            if rules_to_update[0].modified_rule_name in rules_dict.keys():
                BRANCH_NAME = f"update_rule/{rules_to_update[0].modified_rule_name}"
                pr_message = f"Update {rules_to_update[0].modified_rule_name}"
                pr_body = f"This is an automatically generated PR to update {rules_to_update[0].modified_rule_name}"
            else:
                BRANCH_NAME = f"create_rule/{rules_to_update[0].modified_rule_name}"
                pr_message = f"Create {rules_to_update[0].modified_rule_name}"
                pr_body = f"This is an automatically generated PR to create {rules_to_update[0].modified_rule_name}"
        else:
            BRANCH_NAME = "batch_update"
            pr_message = f"Update {len(rules_to_update)} rules"
            pr_body = f"This is an automatically generated PR to update {len(rules_to_update)} rules"

        for rule in rules_to_update:
            if rule.modified_rule_name not in rules_dict.keys():
                if "." in rule.modified_rule_name:
                    original_rule_name = re.sub(r"\.\d+", "", rule.modified_rule_name)
                    if original_rule_name in rules_dict.keys():
                        utils_logger.info(
                            f"Removing rule {original_rule_name} from dictionary..."
                        )
                        rules_dict.pop(original_rule_name)
            rules_dict[rule.modified_rule_name] = rule.modified_rule

        new_rule_file = "\n".join(rules_dict.values())

        BRANCH_NAME = create_unique_branch(repo, BRANCH_NAME)
        update_file = repo.update_file(
            path=FILENAME,
            message=pr_message,
            content=new_rule_file,
            sha=file_content.sha,
            branch=BRANCH_NAME,
        )

        pr_base = "main"
        pull_request = repo.create_pull(
            title=pr_message, body=pr_body, head=BRANCH_NAME, base=pr_base
        )

        return pull_request.html_url
    except Exception as e:
        utils_logger.error(f"An error occurred: {e}")
        utils_logger.exception(e)
        return None


def remove_thought_tags(text: str) -> str:
    """
    Remove the thought tags from a string
    """
    # This pattern handles tags that span multiple lines and ignores case
    thought_pattern = re.compile(r"<thought>.*?</thought>", re.DOTALL | re.IGNORECASE)

    # Substitute occurrences of the pattern with an empty string to remove them
    cleaned_text = re.sub(thought_pattern, "", text)

    return cleaned_text


def message_html_to_markdown(xml_rule: str) -> str:
    """
    Function to make sure the <message> tag does not contain any HTML.
    """
    # bold tags
    xml_rule = xml_rule.replace("<b>", "**")
    xml_rule = xml_rule.replace("</b>", "**")
    # italics tag
    xml_rule = xml_rule.replace("<i>", "*")
    xml_rule = xml_rule.replace("</i>", "*")
    # linebreak tag
    xml_rule = xml_rule.replace("<linebreak/><linebreak/><linebreak/>", "|")
    xml_rule = xml_rule.replace("<linebreak/><linebreak/>", "|")
    xml_rule = xml_rule.replace("<linebreak/>", "|")

    return xml_rule


def check_rule_modification(rule_xml: str) -> Tuple[str, List[Dict]]:
    response, usage = call_gpt_with_backoff(
        model="gpt-4-1106-preview",
        messages=[
            {"role": "system", "content": DYNAMIC_RULE_CHECKING_PROMPT},
            {"role": "user", "content": rule_xml},
        ],
        temperature=0,
        max_length=1500,
    )
    response = response.replace("```xml", "")
    response = response.replace("```", "")
    response = response.replace("N.*?", "N.*")
    response = remove_thought_tags(response)
    new_rule_xml = re.findall(r"<rule.*?</rule>", response, re.DOTALL)
    if new_rule_xml:
        rule_xml = new_rule_xml[0]
    return rule_xml, [usage]


def create_rule_helper(
    ad_hoc_syntax: str,
    rule_number: str,
    correction: str,
    category: str,
    explanation: str,
    test_sentence: str,
    test_sentence_correction: str,
) -> Tuple[str, Dict]:
    """
    Creates a new rule based on the provided input
    """
    user_text = f"""Ad Hoc:
{ad_hoc_syntax}
Rule Number:
{rule_number}
Correction:
{correction}
Category:
{category}
Explanation:
{explanation}
Test Sentence:
{test_sentence}
Corrected Test Sentence:
{test_sentence_correction}

XML Rule:"""
    messages = generate_simple_message(
        system_prompt=NEW_CREATE_RULE_FROM_ADHOC_SYSTEM_PROMPT, user_prompt=user_text
    )
    usages = []

    response, usage = call_gpt_with_backoff(
        messages=messages, model="gpt-4-1106-preview", temperature=0, max_length=1480
    )
    usages.append(usage)

    # post processing
    cleaned_response = remove_thought_tags(response)
    cleaned_response = cleaned_response.replace("```xml", "").replace("```", "")
    cleaned_response = post_process_xml(cleaned_response)
    cleaned_response = message_html_to_markdown(cleaned_response)
    # rule validation
    cleaned_response, _usages = check_rule_modification(cleaned_response)
    usages.extend(_usages)
    return cleaned_response.strip(), combine_all_usages(usages)


def extract_suggestion_words(input_string: str) -> List[str]:
    """
    Extract suggestion words separated by the @ signs
    """
    lines = input_string.split("\n")
    for line in lines:
        if "@" in line:
            words = [word.strip() for word in line.split("@")]
            return words
    return []


def extract_json_tags(input_text: str) -> str:
    """
    Extracts the text between the JSON tags
    """
    json_pattern = r"<JSON>.*?</JSON>"
    extracted_text = re.findall(json_pattern, input_text, flags=re.DOTALL)
    if extracted_text:
        extracted_text = extracted_text[0].replace("<JSON>", "")
        extracted_text = extracted_text.replace("</JSON>", "")
        return extracted_text.strip()

    utils_logger.warning(f"no JSON tag pattern detected, doing fallback. {input_text=}")
    pattern = ".*?<JSON>"
    new_str = re.sub(pattern, "", input_text, count=1)
    new_str = new_str.replace("</JSON>", "")
    return new_str


def clean_json_output(raw_output: str) -> Dict:
    """
    Clean JSON output from GPT and load as dictionary
    """
    return json.loads(
        remove_thought_tags(raw_output)
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )


def get_pinecone_index(index_name: str) -> pinecone.Index:
    """
    Function to get pinecone index from cache or create new one
    """
    if index_name not in pinecone_indexes:
        pinecone.init(
            api_key=str(os.getenv("PINECONE_API_KEY")),
            environment=str(os.getenv("PINECONE_ENV")),
        )
        pinecone_indexes[index_name] = pinecone.Index(index_name)
    return pinecone_indexes[index_name]


def get_embeddings(sentences: List[str], keep_alive: bool = False) -> List:
    """
    Call embeddings service, returns embeddings if successful or raises error
    """
    if keep_alive:
        session.keep_alive(
            model_id=os.getenv("EMBEDDINGS_SAAS_MODEL_ID"),
            model_version_id=os.getenv("EMBEDDINGS_SAAS_MODEL_VERSION_ID"),
        )
    return session.inference(
        model_id=os.getenv("EMBEDDINGS_SAAS_MODEL_ID"),
        model_version_id=os.getenv("EMBEDDINGS_SAAS_MODEL_VERSION_ID"),
        input_texts=sentences,
    )


def insert_into_pinecone(
    index_name: str,
    namespace: str,
    records: List[dict],
    keep_alive: bool = False,
):
    """
    Insert records into pinecone with a schema of
    {"id": "", "embedded_value": "", "full_input": "", "expected_output": ""}
    """
    index = get_pinecone_index(index_name=index_name)
    for record in records:
        if not record.get("embedded_value", ""):
            utils_logger.warning("No value found for embeddings, passing empty string")
        index.upsert(
            vectors=[
                (
                    record.get("id", str(uuid4())),
                    get_embeddings([record.get("embedded_value", "")], keep_alive)[0],
                    {
                        "full_input": record.get("full_input", ""),
                        "expected_output": record.get("expected_output"),
                    },
                )
            ],
            namespace=namespace,
        )


def search_pinecone_index(
    index_name: str,
    namespace: str,
    search_param: str,
    num_results: int,
    threshold: float,
    keep_embeddings_alive: bool = False,
) -> List[dict]:
    """
    Function to search correct pinecone index
    """
    # load index
    index = get_pinecone_index(index_name=index_name)

    # get total number of vectors from pinecone to fix out of bounds error
    TOTAL_NUM_VECTORS = index.describe_index_stats()["total_vector_count"]
    if num_results > TOTAL_NUM_VECTORS:
        num_results = TOTAL_NUM_VECTORS

    query_em = get_embeddings([search_param], keep_embeddings_alive)[0]

    try:
        result = index.query(
            query_em, namespace=namespace, top_k=num_results, includeMetadata=True
        )

        # iterate through and only return the results that are within the set threshold
        return [
            match["metadata"]
            for match in result["matches"]
            if match["score"] >= threshold
        ]
    except Exception as e:
        setup_logger(__name__).error(f"Error querying pinecone: {e}")
        return []


def create_df_from_analysis_data(data: List, data_type: str) -> pd.DataFrame:
    if data_type == "clusters":
        # Assuming 'clusters' contains a list of dicts with 'pattern' and 'values'
        flattened_data = []
        for cluster in data:
            for value in cluster["values"]:
                flattened_data.append({"pattern": cluster["pattern"], **value})
        return pd.DataFrame(flattened_data)
    elif data_type == "usages":
        return pd.DataFrame(data)
    else:  # flags or other types
        return pd.DataFrame(data, columns=["flags"])
