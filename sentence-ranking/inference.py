import os
import openai
from dotenv import load_dotenv

from prompts import SENTENCE_RANKING_SYSTEM_PROMPT, USER_TEXT_EXAMPLES
from utils import setup_logger, call_gpt4_with_backoff, generate_simple_message

# load env vars from .env file
load_dotenv()

# setup logger
logger = setup_logger()

# set openai key
openai.api_key = os.getenv('OPENAI_API_KEY')


for example in USER_TEXT_EXAMPLES:
    messages = generate_simple_message(
        system_prompt=SENTENCE_RANKING_SYSTEM_PROMPT,
        user_prompt=example
    )
    response = call_gpt4_with_backoff(messages=messages, temperature=0)
    logger.info(response)