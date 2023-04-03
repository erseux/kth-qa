import json
import logging

logger = logging.getLogger()
logging.basicConfig(encoding='utf-8', level=logging.INFO)

from fastapi import FastAPI, File, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


class Question(BaseModel):
    question: str


import uvicorn

from kth_qa.config import Config

config = Config()
app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5000",
    "http://localhost:5001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return RedirectResponse(url="/home")

@app.get("/home", response_class=HTMLResponse)
def home():
    # html page with search box, sending a post request to /api/ask
    # and displaying the answer
    # open index.html and return the content
    with open("kth_qa/index.html", "r") as f:
        html = f.read()
    return HTMLResponse(content=html, status_code=200)

@app.post("/api/ask/")
async def ask(question: Question):
    answer = config.index.query(question.question)
    if not answer:
        return JSONResponse(status_code=404, content={"message": "No answer found"})
    return {"answer": answer}

if __name__ == "__main__":
    uvicorn.run("kth_qa:app", host="localhost", port=5001, reload=True, reload_excludes=['files/', 'logs/'])

