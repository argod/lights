from fastapi import FastAPI, HTTPException
from lights.controller import Controller
import logging
import os
import yaml
from threading import Thread

from pydantic import BaseModel
from typing import List

logger = logging.getLogger(__name__)
app = FastAPI()
app.controller = None
app.controller_thread = None


@app.get("/start")
def start():
    if not app.controller:
        if 'LIGHTS_CONFIG' not in os.environ:
            raise HTTPException(status_code=500, detail="Configuration file not found")
        config_location = os.environ['LIGHTS_CONFIG']
        with open(config_location, 'r') as f:
            app_config = yaml.safe_load(f.read())
        app.controller = Controller(app_config)
    if app.controller_thread:
        app.controller.stop()
        app.controller_thread.join()
    app.controller_thread = Thread(target=app.controller.start, args=())
    app.controller_thread.start()


@app.get("/stop")
def stop():
    if not app.controller:
        raise HTTPException(status_code=500, detail="Controller object not loaded")
    app.controller.stop()
    app.controller_thread.join()


@app.get("/calendar-updates/{status}")
def calendar_updates(status: bool):
    if not app.controller:
        raise HTTPException(status_code=500, detail="Controller object not loaded")
    app.controller.set_calendar_updates(status)


@app.get("/pomodoro/{status}")
def calendar_updates(status: str):
    try:
        if not app.controller:
            raise HTTPException(status_code=500, detail="Controller object not loaded")
        if status == 'start':
            app.controller.set_pomodoro(True)
        elif status == 'stop':
            app.controller.set_pomodoro(False)
        else:
            raise HTTPException(status_code=500, detail=f"Status ({status}) not recognized possible values[start, stop].")
    except Exception:
        logger.exception(f"Error changing state of pomodoro to {status}")


class GoogleToken(BaseModel):
    token: str
    refresh_token: str
    token_uri: str
    client_id: str
    client_secret: str
    scopes: List[str]
    expiry: str


@app.post("/update-calendar-token")
def update_calendar_updates(token: GoogleToken):
    if not app.controller:
        raise HTTPException(status_code=500, detail="Controller object not loaded")
    app.controller.update_calendar_token(token.dict())
