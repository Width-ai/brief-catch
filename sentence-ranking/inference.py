import os
import openai
import pandas as pd
import re
import time
import timeit
from dotenv import load_dotenv
from multiprocessing import Pool, Lock
from typing import List

from cost_calc import calc_cost, num_tokens_from_string
from prompts import SENTENCE_RANKING_SYSTEM_PROMPT, CONDENSED_SENTENCE_RANKING_SYSTEM_PROMPT
from utils import setup_logger, call_gpt4_with_backoff, generate_simple_message

# load env vars from .env file
load_dotenv()

# setup logger
logger = setup_logger()

# set openai key
openai.api_key = os.getenv('OPENAI_API_KEY')

GPT_4_RATE_LIMIT = 40000
TOKEN_BUFFER_AMOUNT = 3000

write_lock = Lock()

def rank_sentences(input_data_tuple: tuple):
    index, row, sleep_time = input_data_tuple
    if index % 100 == 0:
        logger.info(f"Current index: {index}")
    try:
        time.sleep(sleep_time)  # Wait for a certain period to avoid hitting rate limit
        sentence_data = '\t'.join(row.astype(str))
        messages = generate_simple_message(
            system_prompt=SENTENCE_RANKING_SYSTEM_PROMPT,
            user_prompt=sentence_data
        )

        # if length of messages is more than token limit
        if num_tokens_from_string(string=SENTENCE_RANKING_SYSTEM_PROMPT + sentence_data) < GPT_4_RATE_LIMIT - TOKEN_BUFFER_AMOUNT:
            response = call_gpt4_with_backoff(messages=messages, temperature=0)
            
            # write results to file immediately
            with write_lock:
                with open('data/output_rest_of_data.txt', 'a') as f:
                    f.write(response + "\n")

    except Exception as e:
        logger.error(f"Error ranking sentence {index}: {e}")
        logger.exception(e)


def parallelize_rank_sentences(df: pd.DataFrame, processes: int, sleep_time: int):
    pool = Pool(processes=processes)
    data_tuples = [(index, row, sleep_time) for index, row in df.iterrows()]
    pool.map(rank_sentences, data_tuples)
    pool.close()
    pool.join()


def calc_run_cost(input_data: pd.DataFrame) -> tuple[float, int]:
    cost = 0.0
    tokens = 0
    for _, row in input_data.iterrows():
        sentence_data = '\t'.join(row.astype(str))
        sentence_cost, sentence_tokens = calc_cost(string=sentence_data, system_prompt=CONDENSED_SENTENCE_RANKING_SYSTEM_PROMPT)
        cost += sentence_cost
        tokens += sentence_tokens
    return cost, tokens


def read_numbers(file_name):
    numbers = []
    with open(file_name, 'r') as file:
        lines = file.readlines()
        for line in lines:
            match = re.search(r'(\d+)\.', line)
            if match:
                numbers.append(int(match.group(1)))
    return numbers


def main():
    # read in data
    df = pd.read_csv('data/sentence_ranking_clean_input_data.csv')
    df = df.reset_index(drop=True)

    NUM_RECORDS = -5000
    NUM_PROCESSES = 6
    SLEEP_TIME = 5

    # filter out data
    # df = df.head(NUM_RECORDS)
    df = df[~df['sentence #'].isin(read_numbers('data/output_rest_of_data.txt'))]

    # run a cost analysis and check for approval
    cost_estimate, token_estimate = calc_run_cost(input_data=df)
    approval = input(f"Estimated cost: ${cost_estimate}\nEstimated tokens: {token_estimate}\nContinue? [Y/n]:")

    if approval == 'Y':
        # rank the sentences
        start_time = timeit.default_timer()
        parallelize_rank_sentences(df=df, processes=NUM_PROCESSES, sleep_time=SLEEP_TIME)
        end_time = timeit.default_timer()
        logger.info(f"Run time: {end_time - start_time}")


if __name__ == '__main__':
    main()