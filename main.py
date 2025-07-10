from fastapi import FastAPI
from pydantic import BaseModel
import ollama
from ollama import Client
import requests
import json
import os
import re
from dotenv import load_dotenv
from dotenv import find_dotenv
import openai


load_dotenv(find_dotenv())


GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

dockerClient = Client(host='http://ml:11434')

dreeseClient = openai.OpenAI(
    base_url="http://18.218.87.50/v1",
    api_key="sk-test"  # Placeholder, no authentication enforced
)

app = FastAPI()

class LLMInput(BaseModel):
    text1: str
    text2: str

@app.post("/llm-test")
async def summarize(payload: LLMInput):
    prompt = (
        "Given the following two news articles write a single unbiased summary\n "
        f"Article 1:\n{payload[1].content}\n\n"
        f"Article 2:\n{payload[2].content}\n\n"
        "Neutral Summary:"
    )

    response = dockerClient.chat(model='llama3.2', messages=[{'role': 'user', 'content': prompt},])

    # print(response.message.content)

    return {"summary": response.message.content}


@app.post("/gemini-test")
async def summarize2(payload: LLMInput):

    prompt = (
        "Given the following two news articles write a single unbiased summary\n "
        f"Article 1:\n{payload.text1}\n\n"
        f"Article 2:\n{payload.text2}\n\n"
        "Neutral Summary:"
    )

    some_request = {"contents": [{"parts": [{"text": prompt }]}]}

    response = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",  json=some_request)

    return {"summary": response.json()['candidates'][0]['content']['parts']}



class LLMInput2(BaseModel):
    nArticles: str

@app.post("/rag-gemini-test")
async def summarize2(payload: LLMInput2):
    prompt = (
        "Given the following two news articles write a single unbiased summary\n "
        f"{payload.nArticles}\n"
        "Neutral Summary:"
    )

    some_request = {"contents": [{"parts": [{"text": prompt }]}]}

    response = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",  json=some_request)
    print(f"\n\n\n\n\n{response.json()}\n\n\n\n")
    return {"summary": response.json()['candidates'][0]['content']['parts']}


@app.post("/rag-ollama-test")
async def summarize2(payload: LLMInput2):
    prompt = (
        "Given the following two news articles write a single unbiased summary\n "
        f"{payload.nArticles}\n"
        "Neutral Summary:"
    )

    response = dockerClient.chat(model='llama3.2', messages=[{'role': 'user', 'content': prompt},])
    print(f"\n\n\n\n\n{response}\n\n\n\n")
    return {"summary": response.message.content}


@app.post("/rag-dreese-test")
async def summarize2(payload: LLMInput2):
    prompt = (
        "Given the following two news articles write a single unbiased summary\n "
        f"{payload.nArticles}\n"
        "Neutral Summary:"
    )
    # Send a chat request
    response = dreeseClient.chat.completions.create(
        model="llama3",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    print(f"\n\n\n\n\n{response}\n\n\n\n")
    return {"summary": response.choices[0].message.content}
