import openai
import os

from dotenv import load_dotenv
from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
from src.models.gpt3 import call_gpt3

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()


@app.post("/generate-next-word")
def generate_next_word(prompt: str = Form(example="Hello, nice to meet you!"),
             temperature: float = Form(0),
             model: str = Form("text-davinci-003")):
    """
    Generate the next possible words with the log probabilities.
    """
    try:
        text, words = call_gpt3(prompt, model=model, temperature=temperature)
        return {
            "text": text,
            "words": words
        }
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
