import json
import openai
import os
from collections import defaultdict
from dotenv import load_dotenv
from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import JSONResponse
from domain.prompts import TOPIC_SENTENCE_SYSTEM_PROMPT, QUOTATION_SYSTEM_PROMPT
from domain.models import InputData, SentenceRankingInput, InputDataList
from utils.utils import generate_simple_message, call_gpt_with_backoff, setup_logger, rank_sentence, call_gpt3, \
    rewrite_parentheses_helper

logger = setup_logger(__name__)

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()


@app.post("/topic-sentence")
def topic_sentence(input_data: InputData):
    """
    Evaluate if the topic sentence needs to be revised, return the revised version if needed
    """
    try:
        messages = generate_simple_message(
            system_prompt=TOPIC_SENTENCE_SYSTEM_PROMPT,
            user_prompt=input_data.input_text
        )
        response, usage = call_gpt_with_backoff(messages=messages, model="gpt-4", temperature=0)
        logger.info(f"response from topic sentence analysis: {response}")
        json_response = json.loads(response)
        if json_response["revised_topic_sentence"].lower().replace(".", "") == "no changes":
            logger.info("original sentence didn't need changes, replacing value in output...")
            json_response["revised_topic_sentence"] = input_data.input_text
        json_response["usage"] = usage
        return JSONResponse(content=json_response)
    except Exception as e:
        logger.error(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/quotations")
def quotations(input_data: InputData):
    """
    Evaluate if the passage has quotations introduced with fluffy lean-ins and replace them with substantive ones
    """
    try:
        messages = generate_simple_message(
            system_prompt=QUOTATION_SYSTEM_PROMPT,
            user_prompt=input_data.input_text
        )
        response, usage = call_gpt_with_backoff(messages=messages, temperature=1)
        return JSONResponse(content={"response": response, "usage": usage})
    except Exception as e:
        logger.error(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/sentence-ranking")
def sentence_ranking(input_data: SentenceRankingInput):
    """
    Rank the sentence corrections
    """
    try:
        responses = [
            rank_sentence(
                sentence_number=record.sentence_number,
                rule_number=record.rule_number,
                text=record.text,
                corrected_text=record.corrected_text
            )
            for record in input_data.input_data
        ]
        usages = [response.pop("usage") for response in responses]
        total_usage = defaultdict(float)
        for usage in usages:
            for key, value in usage.items():
                total_usage[key] += value
        return JSONResponse(content={"response": responses, "usage": total_usage})
    except Exception as e:
        logger.error(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/parentheses-rewriting")
def parentheses_rewriting(input_data: InputDataList):
    """
    Rewrite text that has parentheses in it based on criteria
    """
    try:
        response, usage = rewrite_parentheses_helper(input_data=input_data.input_texts)
        return JSONResponse(content={
            "response": response,
            "usage": usage
        })
    except Exception as e:
        logger.error(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/generate-next-word")
def generate_next_word(input_sentence: InputData) -> JSONResponse:
    """
    Generate the next possible words with the log probabilities.
    """
    try:
        prompt = f"Generate the most likely word to complete this sentence:\n\n{input_sentence.input_text.strip()}"
        response, usage = call_gpt3(prompt=prompt, temperature=0)
        return JSONResponse(content={"likely_words": response, "usage": usage})
    except Exception as e:
        logger.error(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/bulk-generate-next-word")
async def bulk_generate_next_word(file: UploadFile = File(...)) -> JSONResponse:
    """
    Generates the next possible words with the log probabilities for a bulk dataset
    """
    try:
        contents = await file.read()
        # Split the file contents into lines and then into tuples
        lines = [line for line in contents.decode('utf-8').split('\n') if line.strip()]
        response_data = []
        for line in lines:
            response, usage = call_gpt3(prompt=line.strip(), temperature=0)
            response_data.append({
                "input": line,
                "likely_words": response,
                "usage": usage
            })
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/generate-prev-word")
def generate_prev_word(input_data: InputData) -> JSONResponse:
    """
    Generate the most likely previous word with the log probabilities
    """
    try:
        prompt = f"Fill in the blank in the sentence below:\n\n____ {input_data.input_text.strip()}\n\n"
        response, usage = call_gpt3(prompt=prompt, temperature=0, max_tokens=10)
        return JSONResponse(content={"likely_words": response, "usage": usage})
    except Exception as e:
        logger.error(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/bulk-generate-prev-word")
async def bulk_generate_prev_word(file: UploadFile = File(...)) -> JSONResponse:
    """
    Generates the previous possible words with the log probabilities for a bulk dataset
    """
    try:
        contents = await file.read()
        # Split the file contents into lines and then into tuples
        lines = [line for line in contents.decode('utf-8').split('\n') if line.strip()]
        response_data = []
        for line in lines:
            prompt = f"Fill in the blank in the sentence below:\n\n____ {line.strip()}\n\n"
            response, usage = call_gpt3(prompt=prompt, temperature=0, max_tokens=10)
            response_data.append({
                "input": line,
                "likely_words": response,
                "usage": usage
            })
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)