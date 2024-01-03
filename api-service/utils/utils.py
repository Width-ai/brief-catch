import json
import backoff
import math
import openai
import os
import pandas as pd
import pinecone
import re
import tiktoken
from lxml import etree
from collections import defaultdict
from github import Github, Repository, GithubException
from typing import List, Tuple, Dict
from uuid import uuid4
from word_embeddings_sdk import WordEmbeddingsSession
from domain.prompts import (
    SENTENCE_RANKING_SYSTEM_PROMPT,
    PARENTHESES_REWRITING_PROMPT,
    CREATE_RULE_FROM_ADHOC_SYSTEM_PROMPT
)
from domain.models import RuleToUpdate
from domain.modifier_prompts import RULE_USER_TEXT_TEMPLATE
from domain.modifier_prompts.common_instructions import STANDARD_PROMPT
from domain.ngram_prompts.prompts import (
    SEGMENT_CREATION_SYSTEM_PROMPT,
    IDENTIFY_PATTERNS_SYSTEM_PROMPT,
    CONDENSE_CLUSTERS_SYSTEM_PROMPT,
    CONDENSE_CLUSTERS_USER_TEMPLATE
)
from utils.adhoc_rule_search import create_correction_regex, search_for_adhoc
from utils.logger import setup_logger

pricing = json.load(open("pricing.json"))
utils_logger = setup_logger(__name__)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
FILENAME = os.getenv("RULE_FILENAME", "grammar.xml")
session = WordEmbeddingsSession(
    customer_id=os.getenv("EMBEDDINGS_SAAS_ID"),
    api_key=os.getenv("EMBEDDINGS_SAAS_API_KEY"))
pinecone_indexes = {}



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


def call_gpt3(prompt: str, temperature: float=0.7, max_tokens: int = 2) -> Tuple[List[dict], Dict]:
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
    usage["cost"] = compute_cost(usage, "text-davinci-003")
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


def fetch_rule_by_id(rule_id: str) -> Tuple[str, str]:
    """
    Search for rule by given ID, this is not the long form ID in the rule, but the short id in the name
    """
    rule_dict = pull_xml_from_github()
    for rule_name in rule_dict.keys():
        if rule_name.endswith(f"_{rule_id}"):
            return rule_dict.get(rule_name), rule_name
    return None, ""


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
        xml_content = file_content.decoded_content.decode('utf-8')
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
            rules_dict[rule.modified_rule_name] = rule.modified_rule

        new_rule_file = "\n".join(rules_dict.values())

        BRANCH_NAME = create_unique_branch(repo, BRANCH_NAME)
        update_file = repo.update_file(
            path=FILENAME, 
            message=pr_message,
            content=new_rule_file,
            sha=file_content.sha, 
            branch=BRANCH_NAME
        )

        pr_base = "main"
        pull_request = repo.create_pull(title=pr_message, body=pr_body, head=BRANCH_NAME, base=pr_base)

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


def extract_suggestion_words(input_string: str) -> List[str]:
    """
    Extract suggestion words separated by the @ signs
    """
    lines = input_string.split('\n')
    for line in lines:
        if '@' in line:
            words = [word.strip() for word in line.split('@')]
            return words
    return []


def extract_json_tags(input_text: str) -> str:
    """
    Extracts the text between the JSON tags
    """
    json_pattern = r'<JSON>.*?</JSON>'
    extracted_text = re.findall(json_pattern, input_text, flags=re.DOTALL)[0]
    extracted_text = extracted_text.replace("<JSON>", "")
    extracted_text = extracted_text.replace("</JSON>", "")
    return extracted_text.strip()


def clean_json_output(raw_output: str) -> Dict:
    """
    Clean JSON output from GPT and load as dictionary
    """
    return json.loads(
        remove_thought_tags(raw_output).replace(
            "```json", ""
        ).replace("```", "").strip()
    )


def rank_records_by_score(data: Dict) -> Dict:
    # Check if 'reranking' is in the dictionary and is a list
    for i, group in enumerate(data['reranking']):
        data['reranking'][i] = sorted(group, key=lambda x: float(x['score']), reverse=True)
    return data


def truncate_ngram_dataset(dataset: List[Dict], top_n=50) -> Dict:
    """
    Takes in ngram dataset and only keeps the top_n records based on score
    """
    # make the list of dictionary a single dictionary
    dataset = {list(item.keys())[0]: item[list(item.keys())[0]] for item in dataset}
    # flatten the dataset
    flattened = []
    for word_key, ngrams in dataset.items():
        for ngram in ngrams:
            try:
                score = float(ngram['score'])
                flattened.append((word_key, ngram['ngram'], score))
            except ValueError:
                utils_logger.error(f"Error converting score to float for '{ngram['ngram']}': {ngram['score']}")
    
    # sort by score in descending order
    sorted_flattened = sorted(flattened, key=lambda x: x[2], reverse=True)
    
    # take the top_n records, or all records if there are less than top_n
    top_records = sorted_flattened[:min(top_n, len(sorted_flattened))]
    
    # recreate the dataset with only the top records
    top_dataset = {}
    for word, ngram, score in top_records:
        if word not in top_dataset:
            top_dataset[word] = []
        top_dataset[word].append({'ngram': ngram, 'score': str(score)})
    
    return top_dataset


def ngram_helper_suggestion(rule_pattern: str, suggestion_pattern: str) -> Dict:
    """
    Helper function to perform the ngram analysis on suggestion patterns
    """
    try:
        suggestion_patterns = suggestion_pattern.split("@")
        search_patterns = create_correction_regex(rule_pattern, suggestion_pattern)
        # load the csv with ngram data
        df = pd.read_csv("data/Ngram Over 1 score.csv")
        df.drop(columns=["Unnamed: 2", "Unnamed: 3", "Unnamed: 4"], inplace=True)
        df.dropna(inplace=True)
        
        # search the ngram data for the different patterns
        ngram_data = []
        flags = []
        clusters = []
        usages = []
        for index, search_pattern in enumerate(search_patterns):
            if search_pattern:
                records = df[df['ngram'].str.contains(search_pattern)].to_dict(orient='records')
                if records:
                    ngram_data.append({suggestion_patterns[index].strip(): records})
                else:
                    flags.append(suggestion_patterns[index].strip())
        
        # drop any record not in the top n (default is 50)
        ngram_data = truncate_ngram_dataset(ngram_data)
        
        if ngram_data:
            # segment the results into groups with similar patterns
            segment_messages = generate_simple_message(
                system_prompt=SEGMENT_CREATION_SYSTEM_PROMPT,
                user_prompt=json.dumps(ngram_data))
            segment_output, segment_usage = call_gpt_with_backoff(
                messages=segment_messages,
                model="gpt-4-1106-preview",
                temperature=0,
                max_length=1279)
            usages.append(segment_usage)
            
            cleaned_output = clean_json_output(segment_output)
            
            # remove any segement with just one record
            cleaned_output['reranking'] = [item for item in cleaned_output['reranking'] if len(item) > 1]
            
            # sort the records in each group to be in order by score
            ranked_groups = rank_records_by_score(cleaned_output)
            pattern_messages = generate_simple_message(
                system_prompt=IDENTIFY_PATTERNS_SYSTEM_PROMPT,
                user_prompt=json.dumps(ranked_groups.get("reranking", [])))
            pattern_output, pattern_usage = call_gpt_with_backoff(
                messages=pattern_messages,
                model="gpt-3.5-turbo",
                temperature=0,
                max_length=1983)
            usages.append(pattern_usage)

            cleaned_pattern_output = clean_json_output(pattern_output)
            
            # condense the clusters where patterns are alike
            condensed_messages = generate_simple_message(
                system_prompt=CONDENSE_CLUSTERS_SYSTEM_PROMPT,
                user_prompt=CONDENSE_CLUSTERS_USER_TEMPLATE.replace(
                    "{{cluster_dictionary}}", json.dumps(cleaned_pattern_output, indent=4)
                )
            )
            condensed_output, condense_usage = call_gpt_with_backoff(
                messages=condensed_messages,
                model="gpt-4-1106-preview",
                temperature=0,
                max_length=1599)
            usages.append(condense_usage)
            extracted_condensed_clusters = extract_json_tags(condensed_output)
            clusters = clean_json_output(extracted_condensed_clusters)
        return {
            "clusters": clusters,
            "flags": flags,
            "usages": usages
        }
    except Exception as e:
        utils_logger.error(f"Error clustering ngram data: {e}")
        utils_logger.exception(e)
        raise e


def ngram_helper_rule(rule_pattern: str) -> Dict:
    """
    Helper function to perform the ngram analysis on rule patterns
    """
    try:
        search_pattern = " ".join(search_for_adhoc(rule_pattern))
        # load the csv with ngram data
        df = pd.read_csv("data/Ngram Over 1 score.csv")
        df.drop(columns=["Unnamed: 2", "Unnamed: 3", "Unnamed: 4"], inplace=True)
        df.dropna(inplace=True)
        
        # search the ngram data for the different patterns
        ngram_data = []
        flags = []
        clusters = []
        usages = []
        records = df[df['ngram'].str.contains(search_pattern)].to_dict(orient='records')
        if records:
            ngram_data.append({rule_pattern: records})
        else:
            flags.append(rule_pattern)
        
        # drop any record not in the top n (default is 50)
        ngram_data = truncate_ngram_dataset(ngram_data)
        
        if ngram_data:
            # segment the results into groups with similar patterns
            segment_messages = generate_simple_message(
                system_prompt=SEGMENT_CREATION_SYSTEM_PROMPT,
                user_prompt=json.dumps(ngram_data))
            segment_output, segment_usage = call_gpt_with_backoff(
                messages=segment_messages,
                model="gpt-4-1106-preview",
                temperature=0,
                max_length=1240)
            usages.append(segment_usage)
            
            cleaned_output = clean_json_output(segment_output)
            
            # remove any segement with just one record
            cleaned_output['reranking'] = [item for item in cleaned_output['reranking'] if len(item) > 1]
            
            # sort the records in each group to be in order by score
            ranked_groups = rank_records_by_score(cleaned_output)
            pattern_messages = generate_simple_message(
                system_prompt=IDENTIFY_PATTERNS_SYSTEM_PROMPT,
                user_prompt=json.dumps(ranked_groups.get("reranking", [])))
            pattern_output, pattern_usage = call_gpt_with_backoff(
                messages=pattern_messages,
                model="gpt-3.5-turbo",
                temperature=0,
                max_length=1983)
            usages.append(pattern_usage)

            cleaned_pattern_output = clean_json_output(pattern_output)
            
            # condense the clusters where patterns are alike
            condensed_messages = generate_simple_message(
                system_prompt=CONDENSE_CLUSTERS_SYSTEM_PROMPT,
                user_prompt=CONDENSE_CLUSTERS_USER_TEMPLATE.replace(
                    "{{cluster_dictionary}}", json.dumps(cleaned_pattern_output, indent=4)
                ))
            condensed_output, condense_usage = call_gpt_with_backoff(
                messages=condensed_messages,
                model="gpt-4-1106-preview",
                temperature=0,
                max_length=1600)
            usages.append(condense_usage)
            extracted_condensed_clusters = extract_json_tags(condensed_output)
            clusters = clean_json_output(extracted_condensed_clusters)
        return {
            "clusters": clusters,
            "flags": flags,
            "usages": usages
        }
    except Exception as e:
        utils_logger.error(f"Error clustering ngram data: {e}")
        utils_logger.exception(e)
        raise e



def get_pinecone_index(index_name: str) -> pinecone.Index:
    """
    Function to get pinecone index from cache or create new one
    """
    if index_name not in pinecone_indexes:
        pinecone.init(api_key=str(os.getenv("PINECONE_API_KEY")), environment=str(os.getenv("PINECONE_ENV")))
        pinecone_indexes[index_name] = pinecone.Index(index_name)
    return pinecone_indexes[index_name]


def get_embeddings(sentences: List[str], keep_alive: bool = False) -> List:
    """
    Call embeddings service, returns embeddings if successful or raises error
    """
    if keep_alive:
        session.keep_alive(
            model_id=os.getenv("EMBEDDINGS_SAAS_MODEL_ID"),
            model_version_id=os.getenv("EMBEDDINGS_SAAS_MODEL_VERSION_ID")
        )
    return session.inference(
        model_id=os.getenv("EMBEDDINGS_SAAS_MODEL_ID"),
        model_version_id=os.getenv("EMBEDDINGS_SAAS_MODEL_VERSION_ID"),
        input_texts=sentences
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
            vectors=[(
                record.get("id", str(uuid4())),
                get_embeddings([record.get("embedded_value", "")], keep_alive)[0],
                {
                    "full_input": record.get("full_input", ""),
                    "expected_output": record.get("expected_output")
                }
            )],
            namespace=namespace
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
    TOTAL_NUM_VECTORS = index.describe_index_stats()['total_vector_count']
    if num_results > TOTAL_NUM_VECTORS:
        num_results = TOTAL_NUM_VECTORS

    query_em = get_embeddings([search_param], keep_embeddings_alive)[0]

    try:
        result = index.query(query_em, namespace=namespace, top_k=num_results, includeMetadata=True)

        # iterate through and only return the results that are within the set threshold
        return [
            match['metadata']
            for match in result['matches']
            if match['score'] >= threshold
        ]
    except Exception as e:
        setup_logger(__name__).error(f"Error querying pinecone: {e}")
        return []


def create_df_from_analysis_data(data: List, data_type: str) -> pd.DataFrame:
    if data_type == 'clusters':
        # Assuming 'clusters' contains a list of dicts with 'pattern' and 'values'
        flattened_data = []
        for cluster in data:
            for value in cluster['values']:
                flattened_data.append({'pattern': cluster['pattern'], **value})
        return pd.DataFrame(flattened_data)
    elif data_type == 'usages':
        return pd.DataFrame(data)
    else:  # flags or other types
        return pd.DataFrame(data, columns=['flags'])