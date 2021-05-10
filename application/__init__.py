"""Main module for the fastapi app."""
import os
import pathlib

from dotenv import load_dotenv
from fastapi import FastAPI

import application.routers as routers
import application.mongo as mongo

# load the environment from the file app.env in the project directory
basedir = pathlib.Path(__file__).parent.parent
load_dotenv(basedir / "app.env")

app = FastAPI()

app.include_router(routers.router)
app.add_event_handler("startup", mongo.backend)
