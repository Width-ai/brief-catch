import backoff
import logging
import math
import openai
import tiktoken
from typing import List
from domain.prompts import SENTENCE_RANKING_SYSTEM_PROMPT, PARENTHESES_REWRITING_PROMPT


def setup_logger(name):
    # Create a logger instance
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Create a formatter for the log messages
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

    # Create a console handler for the log messages
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    # logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


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


@backoff.on_exception(backoff.expo, openai.error.OpenAIError, logger=setup_logger(__name__))
def call_gpt_with_backoff(messages: List, model: str = "gpt-4", temperature: float = 0.7, max_length: int = 256) -> str:
    """
    Generic function to call GPT4 with specified messages
    """
    return call_gpt(model=model, messages=messages, temperature=temperature, max_length=max_length)


def call_gpt(model: str, messages: List, temperature: float = 0.7, max_length: int = 256) -> str:
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
    return response['choices'][0]['message']['content']


def convert_log_probs_to_percentage(log_probs: dict) -> dict:
    """
    Calculate the exponent of each value to get probabilities
    Add them all up to use as the denominator
    Convert to percent
    """
    probs = {k: math.exp(v) for k, v in log_probs.items()}
    total_prob = sum(probs.values())
    percentages = {k: (v/total_prob)*100 for k, v in probs.items()}
    return percentages


def call_gpt3(input_sentence: str, model="text-davinci-003", temperature: float = 0.7, n: int = 1) -> List[dict]:
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

    responses = []
    if len(response.get('choices')) > 0:
        top_probs = response['choices'][0]['logprobs']['top_logprobs']
        for top_prob in top_probs:
            responses.append(convert_log_probs_to_percentage(top_prob))
    return responses


def rank_sentence(sentence_number: str, rule_number: str, text: str, corrected_text: str) -> dict:
    try:
        sentence_data = '\t'.join([sentence_number, text, corrected_text])
        messages = generate_simple_message(
            system_prompt=SENTENCE_RANKING_SYSTEM_PROMPT,
            user_prompt=sentence_data
        )

        # if length of messages is more than token limit
        response = call_gpt_with_backoff(messages=messages, temperature=0)

        # split the response on the first comma
        response_parts = response.split(",", 1)

        return {
            "sentence_number": sentence_number,
            "rule_number": rule_number,
            "text": text,
            "corrected_text": corrected_text,
            "ranking": response_parts[1].strip()
        }
    except Exception as e:
        setup_logger(__name__).error(f"Error ranking sentence: {e}")
        setup_logger(__name__).exception(e)



def num_tokens_from_string(string: str, model_name: str = "gpt-4") -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(model_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def call_gpt_for_parentheses(input_text: str) -> List[str]:
    """
    Call gpt with params for parentheses editing
    """
    messages = generate_simple_message(
        system_prompt=PARENTHESES_REWRITING_PROMPT, user_prompt=input_text)
    result = call_gpt_with_backoff(messages=messages, temperature=0, max_length=2048)
    return result.split("\n")


def rewrite_parentheses_helper(input_data: List[str]) -> List[dict]:
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
            result_list = call_gpt_for_parentheses(input_text=input_text)
            output_data.extend([{'input_text': input, 'output_text': output} for input, output in zip(curr_chunk_input_data, result_list)])
            # Start a new input text with the current line
            input_text = line + '\n'  # add newline character at end of each line.
            curr_chunk_input_data = [line]
    
    # if we didnt hit token limit
    if input_text:
        result_list = call_gpt_for_parentheses(input_text=input_text)
        output_data.extend([{'input_text': input, 'output_text': output} for input, output in zip(curr_chunk_input_data, result_list)])

    return output_data