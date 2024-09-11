import uvicorn
from fastapi import FastAPI
from util.state import exec_dir, settings, platform, Platform, logger
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()
app.mount(
    "/", StaticFiles(directory=os.path.join(exec_dir, "dist"), html=True), name="static"
)


def start():
    port = 80
    if platform != Platform.IRIS:
        port = settings.dev_server_port
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
