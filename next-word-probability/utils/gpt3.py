import math
import openai

from typing import List

from utils.logger import setup_logger

logger = setup_logger()


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
    Call GPT3 to generate text.
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