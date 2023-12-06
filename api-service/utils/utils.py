import json
import backoff
import math
import openai
import os
import re
import tiktoken
from lxml import etree
from collections import defaultdict
from github import Github, Repository
from typing import List, Tuple, Dict
from domain.prompts import (
    SENTENCE_RANKING_SYSTEM_PROMPT,
    PARENTHESES_REWRITING_PROMPT,
    CREATE_RULE_FROM_ADHOC_SYSTEM_PROMPT
)
from domain.modifier_prompts import RULE_USER_TEXT_TEMPLATE
from domain.modifier_prompts.common_instructions import STANDARD_PROMPT
from utils.logger import setup_logger

pricing = json.load(open("pricing.json"))
utils_logger = setup_logger(__name__)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
FILENAME = os.getenv("RULE_FILENAME", "grammar.xml")




def compute_cost(usage: Dict[str, int], model: str) -> float:
    prices = pricing[model]
    return prices["prompt"] * usage["input_tokens"] / 1000 + prices["completion"] * usage["output_tokens"] / 1000


def generate_simple_message(system_prompt: str, user_prompt: str) -> List[dict]:
    return [
        {
            'role': 'system',
            'content': system_prompt
        },
        {
            'role': 'user',
            'content': user_prompt
        }
    ]


@backoff.on_exception(backoff.expo, openai.error.OpenAIError, logger=utils_logger)
def call_gpt_with_backoff(messages: List, model: str = "gpt-4", temperature: float = 0.7, max_length: int = 256) -> Tuple[str, Dict]:
    """
    Generic function to call GPT4 with specified messages
    """
    return call_gpt(model=model, messages=messages, temperature=temperature, max_length=max_length)


def call_gpt(model: str, messages: List, temperature: float = 0.7, max_length: int = 256) -> Tuple[str, Dict]:
    """
    Generic function to call GPT4 with specified messages
    """
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_length,
        frequency_penalty=0.0,
        top_p=1
    )
    usage = {
        "input_tokens": response["usage"]["prompt_tokens"],
        "output_tokens": response["usage"]["completion_tokens"]
    }
    usage["cost"] = compute_cost(usage, model)
    return response['choices'][0]['message']['content'], usage


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


def call_gpt3(input_sentence: str, model="text-davinci-003", temperature: float = 0.7, n: int = 1) -> Tuple[
    List[dict], Dict]:
    """
    Call GPT3 to generate text
    """
    prompt = f"Generate the most likely word to complete this sentence:\n\n{input_sentence}"
    response = openai.Completion.create(
        model=model,
        prompt=prompt,
        temperature=temperature,
        max_tokens=2,
        top_p=1,
        n=n,
        stop=["###"],
        logprobs=5
    )
    usage = {
        "input_tokens": response["usage"]["prompt_tokens"],
        "output_tokens": response["usage"]["completion_tokens"]
    }
    responses = []
    if len(response.get('choices')) > 0:
        top_probs = response['choices'][0]['logprobs']['top_logprobs']
        for top_prob in top_probs:
            responses.append(convert_log_probs_to_percentage(top_prob))
    usage["cost"] = compute_cost(usage, model)
    return responses, usage


def rank_sentence(sentence_number: str, rule_number: str, text: str, corrected_text: str) -> dict:
    try:
        sentence_data = '\t'.join([sentence_number, text, corrected_text])
        messages = generate_simple_message(
            system_prompt=SENTENCE_RANKING_SYSTEM_PROMPT,
            user_prompt=sentence_data
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
            "usage": usage
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
        system_prompt=PARENTHESES_REWRITING_PROMPT, user_prompt=input_text)
    result, usage = call_gpt_with_backoff(messages=messages, temperature=0, max_length=2048)
    return result.split("\n"), usage


def rewrite_parentheses_helper(input_data: List[str]) -> Tuple[List[dict], Dict]:
    """
    Rewrite sentences based on criteria
    """
    # calculate max size per chunk for processing
    SYS_NUM_TOKENS = num_tokens_from_string(PARENTHESES_REWRITING_PROMPT)
    REMAINING_TOKENS = 2000 - SYS_NUM_TOKENS
    max_input_size = REMAINING_TOKENS / (1 + 1.1)  # Adjust this to keep input and output under 2048 tokens.

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
            input_text += line + '\n'  # add newline character at end of each line.
        else:
            result_list, usage = call_gpt_for_parentheses(input_text=input_text)
            output_data.extend([{'input_text': input, 'output_text': output} for input, output in
                                zip(curr_chunk_input_data, result_list)])
            # Start a new input text with the current line
            input_text = line + '\n'  # add newline character at end of each line.
            curr_chunk_input_data = [line]
            usages.append(usage)

    # if we didnt hit token limit
    if input_text:
        result_list, usage = call_gpt_for_parentheses(input_text=input_text)
        output_data.extend(
            [{'input_text': input, 'output_text': output} for input, output in zip(curr_chunk_input_data, result_list)])
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
    root = etree.fromstring(wrapped_xml_content.encode('utf-8'), parser=parser)

    rules_dict = {}

    for rule in root.xpath('.//rule'):
        rule_name = rule.get('name')
        rule_str = etree.tostring(rule, encoding='unicode', pretty_print=True)
        rules_dict[rule_name] = rule_str.rstrip()

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
        xml_content = file_content.decoded_content.decode('utf-8')
        rules_dict = parse_rules_from_xml(xml_content)
        return rules_dict
    except Exception as e:
        utils_logger.error(f"An error occurred: {e}")
        utils_logger.exception(e)
        return None


def rewrite_rule_helper(original_rule: str, target_element: str, element_action: str, specific_actions: List[str] = []) -> Tuple[str, Dict]:
    """
    Calls GPT with the corresponding system prompt and the user text formatted
    """
    # get correct system prompt
    action_system_prompt = STANDARD_PROMPT

    # format user text
    user_text = RULE_USER_TEXT_TEMPLATE.replace("{{origininal_rule_text}}", original_rule)
    user_text = user_text.replace("{{target_element}}", target_element)
    user_text = user_text.replace("{{element_action}}", element_action)
    user_text = user_text.replace("{{list of specific modifications}}", "\n".join(specific_actions))
    
    messages = generate_simple_message(system_prompt=action_system_prompt, user_prompt=user_text)

    return call_gpt_with_backoff(messages=messages, model="gpt-4-1106-preview", temperature=0, max_length=1200)


def create_new_branch(repo: Repository, branch_name: str):
    """
    Tries to create a branch, if it already exists logs a warning
    """
    try:
        main_branch_ref = repo.get_git_ref('heads/main')
        repo.create_git_ref(ref='refs/heads/' + branch_name, sha=main_branch_ref.object.sha)
    except Exception as e:
        utils_logger.warning("Branch with same name likely exists...")
        utils_logger.exception(e)



def update_rule_helper(modified_rule_name: str, modified_rule: str) -> str:
    """
    Updates a rule in the grammar.xml file and creates a pull request
    """
    g = Github(GITHUB_TOKEN)

    try:
        repo = g.get_repo(GITHUB_REPO)
        file_content = repo.get_contents(FILENAME)
        xml_content = file_content.decoded_content.decode('utf-8')
        rules_dict = parse_rules_from_xml(xml_content)
        
        # update the rule
        rules_dict[modified_rule_name] = modified_rule
        new_rule_file = "\n".join(rules_dict.values())

        BRANCH_NAME = f"update_rule/{modified_rule_name}"
        create_new_branch(repo=repo, branch_name=BRANCH_NAME)
        update_file = repo.update_file(
            path=FILENAME, 
            message=f"Update {modified_rule_name}",
            content=new_rule_file,
            sha=file_content.sha, 
            branch=BRANCH_NAME
        )

        pr_title = f"Update {modified_rule_name}"
        pr_body = f"This is an automatically generated PR to update {modified_rule_name}"
        pr_base = "main"
        pull_request = repo.create_pull(title=pr_title, body=pr_body, head=BRANCH_NAME, base=pr_base)

        return pull_request.html_url
    except Exception as e:
        utils_logger.error(f"An error occurred: {e}")
        utils_logger.exception(e)
        return None


def remove_thought_tags(input_text: str) -> str:
    """
    Removes any text between the thought tags. removes the tags too
    """
    thought_pattern = r'<THOUGHT>.*?</THOUGHT>'
    # Use re.sub to replace the pattern with an empty string
    cleaned_text = re.sub(thought_pattern, '', input_text, flags=re.DOTALL)
    return cleaned_text



def create_rule_helper(
        ad_hoc_syntax: str,
        rule_number: str,
        correction: str,
        category: str,
        explanation: str,
        test_sentence: str,
        test_sentence_correction: str) -> Tuple[str, Dict]:
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
    messages = generate_simple_message(system_prompt=CREATE_RULE_FROM_ADHOC_SYSTEM_PROMPT, user_prompt=user_text)

    response, usage = call_gpt_with_backoff(messages=messages, model="gpt-4-1106-preview", temperature=0, max_length=1480)
    cleaned_response = remove_thought_tags(response)
    return cleaned_response.strip(), usage