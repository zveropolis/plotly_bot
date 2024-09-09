#!./.venv/bin/python


import asyncio
import logging
import logging.config
import os
import sys
from fastapi import FastAPI
import uvicorn


sys.path.insert(1, os.path.join(sys.path[0], "src"))


logging.config.fileConfig("log.ini", disable_existing_loggers=True)
logger = logging.getLogger()

app = FastAPI()


@app.get("/test")
def get_all_students_course(name: str | None = None):
    return {"message": f"Hello {name}"}


if __name__ == "__main__":
    uvicorn.run(app, port=5000)
