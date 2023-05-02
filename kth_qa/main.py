import json
import logging

from magic.conversational import question_handler
from schema import Answer

logger = logging.getLogger()
logging.basicConfig(encoding='utf-8', level=logging.INFO)

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.routing import WebSocketRoute
import uvicorn

from schema import Question
from config import State
import arel

# --- Setup ---

# hot reload
async def reload_data():
    print("Reloading server data...")

BASE_PATH = Path(__file__).resolve().parent
static_path = str(BASE_PATH / "static")
template_path = str(BASE_PATH / "templates")

hotreload = arel.HotReload(
    paths=[
        arel.Path(static_path),
        arel.Path(template_path),
    ],
)

state = State()

app = FastAPI(
    routes=[WebSocketRoute("/hot-reload", hotreload, name="hot-reload")],
    on_startup=[hotreload.startup],
    on_shutdown=[hotreload.shutdown],
)

# templates
app.mount("/static", StaticFiles(directory="static"), name="static")
BASE_PATH = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=template_path)
# templates.env.globals["DEBUG"] = config.debug
templates.env.globals["DEBUG"] = True
templates.env.globals["hotreload"] = hotreload

# CORS
origins = [
    "http://localhost",
    "http://localhost:5001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# test questions
with open("test_response.json", "r") as f:
    test_questions = json.load(f)

# --- Routes ---

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.post("/api/ask", response_class=JSONResponse)
async def ask(question: Question):
    question_str = question.question
    if question_str in test_questions:
        return test_questions[question_str]
        
    answer = None
    try:
        answer: Answer = await question_handler(question, state)
    except Exception as e:
        logger.exception(e)
    if not answer:
        return JSONResponse(status_code=404, content={"answer": "Something went wrong."})
    return answer.dict(include={"answer", "urls"})


if __name__ == "__main__":
    uvicorn.run("kth_qa:app", host="localhost", port=5001, reload=True, reload_excludes=['files/', 'logs/'], reload_dirs=['/templates', '/static'])