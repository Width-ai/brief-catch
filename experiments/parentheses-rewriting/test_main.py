import backoff
import logging
import openai
import os
from dotenv import load_dotenv
from io import TextIOWrapper
from typing import List
from cost_calc import num_tokens_from_string, calc_cost

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

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

logger = setup_logger(__name__)


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


@backoff.on_exception(backoff.expo, openai.error.OpenAIError, logger=logger)
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


SYSTEM_PROMPT = """Your task is to reproduce the phrases in this document, maintaining their current order while ensuring that words or phrases enclosed in parentheses in the INPUT TEXT are followed by a ~ symbol directly before the closing parenthesis. For each series of words and phrases separated by slashes, please enclose the entire series in parentheses and replace each slash with a space. Finally, if the first word is an infinitive, put it inside parentheses with no spaces and add "CT" at the beginning. Example: "come to realize" becomes "CT(come) to realize"

Examples for your guidance:
input: come to realize
output: CT(come) to realize

input: (a) matter of
output: ( a ~ ) matter of

input: per
output: per

input: (a/the) ... point
output: ( a the ~ ) ... point

input: (a/the) point of
output: ( a the ~ ) point of

input: on the decline
output: on the decline

input: on the decrease
output: on the decrease

input: along that/this line
output: along ( that this ) line

input: about/concerning it
output: ( about concerning ) it

input: in (the) ... case (of) in connection with in point of
output: in ( the ~ ) ... case ( of ~ ) in connection with in point of

input: intellectual ability/capacity
output: intellectual ( ability capacity )

input: mental ability/capacity
output: mental ( ability capacity )

input: about/concerning/in/on/regarding the matter/subject of
output: ( about concerning in on regarding ) the ( matter subject ) of

input: as/so far as SKIP3 (goes/is concerned)
output: ( as so ) far as SKIP ( goes is ) concerned

input: insofar as SKIP3 (goes/is concerned)
output: insofar as SKIP3 ( goes is ) ( concerned )

input: apply to as
output: CT(apply) to as

input: take advantage of
output: CT(take) advantage of


Please provide a response that accurately reproduces the phrases following the given guidelines.

Note: You should maintain the original order of the phrases and apply the necessary modifications as described above. Your response should be flexible enough to allow for variations in the content and length of the phrases."""



def openai_call(input_text: str) -> str:
    messages = generate_simple_message(system_prompt=SYSTEM_PROMPT, user_prompt=input_text)
    return call_gpt_with_backoff(messages=messages, temperature=0, max_length=2048)


def check_cost(filenames: List[str]) -> bool:
    total_cost = 0
    total_tokens = 0
    for filename in filenames:
        with open(filename, "r") as file:
            cost, tokens = calc_cost(string=file.read(), system_prompt=SYSTEM_PROMPT)
            total_cost += cost
            total_tokens += tokens
    proceed = input(f"Total cost to run will be {total_cost} ({total_tokens} tokens), proceed? Y/n: ")
    if proceed == "Y":
        return True
    return False


def process_file(filename: str, output_file: TextIOWrapper):
    SYS_NUM_TOKENS = num_tokens_from_string(SYSTEM_PROMPT)
    REMAINING_TOKENS = 2000 - SYS_NUM_TOKENS
    max_input_size = REMAINING_TOKENS / (1 + 1.1)  # Adjust this to keep input and output under 2048 tokens.
    input_text = ""
    with open(filename, 'r') as file:
        for line in file:
            line = line.replace(",,", "")
            line = line.strip()
            if not line:  # Skip empty lines
                continue
            line_token_count = num_tokens_from_string(line)
            if line_token_count > max_input_size:
                raise ValueError("Single line exceeds max token count.")
            if num_tokens_from_string(input_text + line) <= max_input_size:
                input_text += line + '\n'  # add newline character at end of each line.
            else:
                # The line would make the input text too large, so call the openai with the current input text
                logger.info(f"calling openai with: {input_text}")
                result = openai_call(input_text)
                logger.info(f"response from openai: {result}")
                output_file.write(result)
                # Start a new input text with the current line
                input_text = line + '\n'  # add newline character at end of each line.

        if input_text.strip():  # If there is some text in input_text.
            # Process remaining text if any.
            result = openai_call(input_text)
            output_file.write(result)


def process_files(filenames: List[str]):
    if check_cost(filenames=filenames):
        with open('output_file_v2s.txt', 'w') as output_file:
            for filename in filenames:
                process_file(filename=filename, output_file=output_file)


if __name__ == '__main__':
    process_files(filenames=['Stems through 7117.csv', 'the rest of stems.csv'])