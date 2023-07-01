import openai
import os

from dotenv import load_dotenv
from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
from utils.gpt3 import call_gpt3
from utils.logger import setup_logger

logger = setup_logger()

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()


@app.post("/generate-next-word")
def generate_next_word(input_sentence: str = Form(example="Hello, nice to meet you!"),
             temperature: float = Form(0),
             model: str = Form("text-davinci-003")):
    """
    Generate the next possible words with the log probabilities.
    """
    try:
        response = call_gpt3(input_sentence, model=model, temperature=temperature)
        return JSONResponse(content={"likely_words": response})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
