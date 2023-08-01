import backoff
import openai

from typing import List

import logging


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