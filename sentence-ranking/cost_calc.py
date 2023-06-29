import tiktoken
from prompts import SENTENCE_RANKING_SYSTEM_PROMPT, USER_TEXT_EXAMPLES

INPUT_PRICING = {
    "gpt-4": 0.03/1000,
    "gpt-4-32k": 0.06/1000,
    "gpt-3.5-turbo": 0.0015/1000,
    "gpt-3.5-turbo-16k": 0.003/1000,
}

OUTPUT_PRICING = {
    "gpt-4": 0.06/1000,
    "gpt-4-32k": 0.12/1000,
    "gpt-3.5-turbo": 0.002/1000,
    "gpt-3.5-turbo-16k": 0.004/1000,
}

# calculated using the outputs in the example sheet, rough estimate 60 characters
# this is example text to calc the tokens, a worse case scenario cost
AVG_OUTPUT = "5 - The revised sentence replaces on at least 24 occasions"


def num_tokens_from_string(string: str, model_name: str = "gpt-4") -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(model_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def calc_cost(string: str, model_name: str = "gpt-4", system_prompt: str = SENTENCE_RANKING_SYSTEM_PROMPT) -> float:
    """Gets the number of tokens then looks up the cost per token for the model"""
    input_tokens = num_tokens_from_string(string=system_prompt + string)
    input_cost = INPUT_PRICING[model_name] * input_tokens
    output_tokens = num_tokens_from_string(string=AVG_OUTPUT)
    output_cost = OUTPUT_PRICING[model_name] * output_tokens
    return input_cost + output_cost


if __name__ == '__main__':
    cost = 0.0
    for example in USER_TEXT_EXAMPLES:
        cost += calc_cost(string=example)
    print(f"${cost}")