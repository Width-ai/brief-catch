import openai
from tiktoken import get_encoding
from typing import Dict, List

openai.api_key = "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"

prices = {
    "gpt-4-32k": {
        "input": 0.06,
        "output": 0.12
    },
    "gpt-4": {
        "input": 0.03,
        "output": 0.06
    },
    "gpt-3.5-turbo-16k": {
        "input": 0.003,
        "output": 0.004
    },
    "gpt-3.5-turbo": {
        "input": 0.0015,
        "output": 0.002
    }
}


def num_tokens_from_string(string: str, encoding_name: str = "cl100k_base") -> int:
    """Returns the number of tokens in a text string."""
    encoding = get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def format_simple_message_for_gpt(system_message: str, user_message: str) -> List[Dict]:
    """
    Takes in a single system message and user message and returns a 
    list of messages used for gpt chat completion
    """
    return [
        {
            "role": "system",
            "content": system_message
        },
        {
            "role": "user",
            "content": user_message
        }
    ]


def call_gpt(messages: List, model: str = "gpt-3.5-turbo-16k", temperature: float = 0.7, max_length: int = 256) -> str:
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


SYSTEM_PROMPT = "You are an expert blog exteneder. Write an extended version of a blog based on the user input"
user_input = """Title: Extraordinary Popular Delusions and The Madness of Crowds: A Fascinating Exploration of Human Behavior

Introduction:
Extraordinary Popular Delusions and The Madness of Crowds is a captivating book written by Charles Mackay in 1841. This timeless classic delves into the intriguing world of human behavior, exploring the irrationality that often takes hold of individuals when they become part of a crowd. Mackay's work remains relevant even today, shedding light on the various delusions and mass hysteria that have shaped history. In this review, we will delve into the key themes and insights offered by this remarkable book.

1. Historical Context:
Mackay's book provides a historical perspective on the power of collective behavior. He examines numerous instances throughout history where large groups of people have succumbed to irrational beliefs and behaviors. From the Dutch Tulip Mania to the South Sea Bubble, Mackay dissects these episodes, revealing the underlying psychological and social factors that contributed to their occurrence.

2. Psychological Insights:
One of the book's most significant contributions is its exploration of the psychological aspects of crowd behavior. Mackay delves into the concept of herd mentality, where individuals abandon their rationality and conform to the beliefs and actions of the group. He highlights the dangers of this phenomenon, emphasizing how it can lead to disastrous consequences, such as financial ruin or societal upheaval.

3. The Role of Delusions:
Mackay's work also focuses on the power of delusions in shaping popular opinion. He examines various delusions, including witch hunts, alchemy, and fortune-telling, illustrating how these beliefs can spread rapidly and influence the masses. By analyzing these delusions, Mackay provides valuable insights into the vulnerability of human nature and the ease with which false ideas can gain traction.

4. Lessons for Modern Society:
Although written in the 19th century, Extraordinary Popular Delusions and The Madness of Crowds offers valuable lessons for contemporary society. The book serves as a cautionary tale, reminding us of the dangers of blindly following the crowd and succumbing to irrational beliefs. It prompts readers to question their own biases and think critically, encouraging individual thought and independent decision-making.

Conclusion:
Extraordinary Popular Delusions and The Madness of Crowds is a thought-provoking book that continues to captivate readers with its exploration of human behavior. Charles Mackay's timeless insights into the power of collective delusions and the madness that can grip societies offer valuable lessons for both historical and contemporary contexts. This book serves as a reminder to remain vigilant against the dangers of herd mentality and to cultivate critical thinking in order to avoid falling prey to popular delusions."""

def spend_on_openai(cost_cap: float):
    model = "gpt-4"
    current_spend = 0.0
    while current_spend < cost_cap:
        try:
            current_spend += (num_tokens_from_string(SYSTEM_PROMPT + user_input) / 1000) * prices.get(model, {}).get("input")
            messages = format_simple_message_for_gpt(system_message=SYSTEM_PROMPT, user_message=user_input)
            response = call_gpt(messages=messages, model=model, temperature=0.3, max_length=3000)
            print(f"response: {response}")
            current_spend += (num_tokens_from_string(response) / 1000) * prices.get(model, {}).get("output")
            print(f"#########\nCurrent Spend: {current_spend}\n#########")
        except Exception as e:
            print(f"Error spending money: {e}")



if __name__ == "__main__":
    spend_on_openai(cost_cap=37.60)