import json
import openai
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from domain.prompts import TOPIC_SENTENCE_SYSTEM_PROMPT, QUOTATION_SYSTEM_PROMPT
from domain.models import InputData
from utils.utils import generate_simple_message, call_gpt_with_backoff, setup_logger

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
        response = call_gpt_with_backoff(messages=messages, model="gpt-4", temperature=0)
        logger.info(f"response from topic sentence analysis: {response}")
        json_response = json.loads(response)
        if json_response["revised_topic_sentence"].lower().replace(".", "") == "no changes":
            logger.info("original sentence didn't need changes, replacing value in output...")
            json_response["revised_topic_sentence"] = input_data.input_text
        return JSONResponse(content=json_response)
    except Exception as e:
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
        response = call_gpt_with_backoff(messages=messages, temperature=1)
        return JSONResponse(content={"response": response})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
