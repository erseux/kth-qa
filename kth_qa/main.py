import logging
import os

logger = logging.getLogger()
logging.basicConfig(encoding='utf-8', level=logging.INFO)

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.routing import WebSocketRoute
import uvicorn

from schema import Question
from config import Config
import arel

# --- Setup ---
DEBUG = False # set to True to disable index creation and querying

# hot reload
async def reload_data():
    print("Reloading server data...")

hotreload = arel.HotReload(
    paths=[
        # arel.Path("./server/data", on_reload=[reload_data]),
        arel.Path("./static"),
        arel.Path("./templates"),
    ],
)

config = Config(debug=DEBUG)

app = FastAPI(
    routes=[WebSocketRoute("/hot-reload", hotreload, name="hot-reload")],
    on_startup=[hotreload.startup],
    on_shutdown=[hotreload.shutdown],
)

# templates
app.mount("/static", StaticFiles(directory="static"), name="static")
BASE_PATH = Path(__file__).resolve().parent
template_path=str(BASE_PATH / "templates")
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

# --- Routes ---

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return RedirectResponse(url="/home")

@app.get("/home", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.post("/api/ask", response_class=JSONResponse)
async def ask(question: Question):
    answer = config.index.query(question.question)
    if not answer:
        return JSONResponse(status_code=404, content={"message": "No answer found"})
    return {"answer": answer}


if __name__ == "__main__":
    uvicorn.run("kth_qa:app", host="localhost", port=5001, reload=True, reload_excludes=['files/', 'logs/'], reload_dirs=['/templates', '/static'])