import re
from typing import *
import openai
import math


def convert_to_bytes(token: str) -> bytes:
    if token.startswith("bytes:"):
        token = token[6:].encode()
        for hex_token in re.findall(b"\\\\x.{2}", token):
            token = token.replace(hex_token, bytes.fromhex(hex_token[2:].decode()))
        return token
    else:
        return token.encode()


def call_gpt3(prompt: str, model="text-davinci-003", temperature: float = 0.7, n: int = 1) -> Tuple[str, List]:
    """
    Call GPT3 to generate text.
    """
    response = openai.Completion.create(
        model=model,
        prompt=prompt,
        temperature=temperature,
        max_tokens=1000,
        top_p=1,
        n=n,
        stop=["###"],
        logprobs=1
    )

    for choice in response["choices"]:
        text = choice["text"]
        tokens = choice["logprobs"]["tokens"]
        if len(tokens) == 0:
            return "", []
        token_logprobs = choice["logprobs"]["token_logprobs"]
        token_with_logprobs = [{"token": convert_to_bytes(token),
                                "logprobas": proba} for token, proba in zip(tokens, token_logprobs)]
        # Mapping tokens to words.
        first_token = token_with_logprobs[0]
        word = {
            "token": first_token["token"],
            "logprobas": [first_token["logprobas"]]
        }
        words = [word]
        for token in token_with_logprobs[1:]:
            if (token["token"].startswith(b" ")
                    or token["token"].startswith(b"\n")
                    or words[-1]["token"].endswith(b" ")
                    or words[-1]["token"].endswith(b"\n")):
                words.append({
                    "token": token["token"],
                    "logprobas": [token["logprobas"]]
                })
            else:
                words[-1]["token"] += token["token"]
                words[-1]["logprobas"].append(token["logprobas"])
        # Calculate average log probabilities of tokens as probability of word.
        words = [
            {
                "word": word["token"].decode().strip(" "),
                "proba": math.exp(sum(word["logprobas"]) / (len(word["logprobas"]) + 1e-9))
            } for word in words
        ]
        return text, words
    return "", []
