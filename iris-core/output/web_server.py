import uvicorn
from fastapi import FastAPI
from util.state import exec_dir
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()
app.mount(
    "/", StaticFiles(directory=os.path.join(exec_dir, "dist"), html=True), name="static"
)


def start():
    uvicorn.run(app, host="0.0.0.0", port=5800, log_level="info")
