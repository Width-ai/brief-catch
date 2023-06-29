import os
import openai
import pandas as pd
import time
import timeit
from dotenv import load_dotenv
from multiprocessing import Pool
from typing import List

from cost_calc import calc_cost
from prompts import SENTENCE_RANKING_SYSTEM_PROMPT, CONDENSED_SENTENCE_RANKING_SYSTEM_PROMPT
from utils import setup_logger, call_gpt4_with_backoff, generate_simple_message

# load env vars from .env file
load_dotenv()

# setup logger
logger = setup_logger()

# set openai key
openai.api_key = os.getenv('OPENAI_API_KEY')


def rank_sentences(input_data_tuple: tuple) -> str:
    index, row, sleep_time = input_data_tuple
    try:
        time.sleep(sleep_time)  # Wait for a certain period to avoid hitting rate limit
        sentence_data = '\t'.join(row.astype(str))
        messages = generate_simple_message(
            system_prompt=SENTENCE_RANKING_SYSTEM_PROMPT,
            user_prompt=sentence_data
        )
        response = call_gpt4_with_backoff(messages=messages, temperature=0)
        # logger.info(response)
        return response
    except Exception as e:
        logger.error(f"Error ranking sentence {index}: {e}")
        logger.exception(e)


def parallelize_rank_sentences(df: pd.DataFrame, processes: int, sleep_time: int) -> List[str]:
    pool = Pool(processes=processes)
    data_tuples = [(index, row, sleep_time) for index, row in df.iterrows()]
    result = pool.map(rank_sentences, data_tuples)
    pool.close()
    pool.join()
    return result


def calc_run_cost(input_data: pd.DataFrame) -> float:
    cost = 0.0
    for _, row in input_data.iterrows():
        sentence_data = '\t'.join(row.astype(str))
        cost += calc_cost(string=sentence_data, system_prompt=CONDENSED_SENTENCE_RANKING_SYSTEM_PROMPT)
    return cost


def main():
    # read in data
    df = pd.read_csv('data/sentence_ranking_clean_input_data.csv')

    NUM_RECORDS = 100
    NUM_PROCESSES = 10
    SLEEP_TIME = 0

    # run a cost analysis and check for approval
    cost_estimate = calc_run_cost(input_data=df.tail(NUM_RECORDS))
    approval = input(f"Estimated cost: ${cost_estimate}\nContinue? [Y/n]:")
    
    if approval == 'Y':
        # rank the sentences
        start_time = timeit.default_timer()
        results = parallelize_rank_sentences(df=df.tail(NUM_RECORDS), processes=NUM_PROCESSES, sleep_time=SLEEP_TIME)
        end_time = timeit.default_timer()
        logger.info(f"Run time: {end_time - start_time}")

        # write results to output file
        with open('data/output_parallel.txt', 'w') as f:
            f.write("\n".join(results))


if __name__ == '__main__':
    main()