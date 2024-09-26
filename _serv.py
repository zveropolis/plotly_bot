#!./.venv/bin/python


from datetime import datetime
import logging
import logging.config
import os
from pprint import pprint
import sys
from typing import Annotated, List
from fastapi import FastAPI, File, Form, Query, UploadFile, Request
from pydantic import BaseModel
import uvicorn

sys.path.insert(1, os.path.join(sys.path[0], "server"))
sys.path.insert(1, os.path.join(sys.path[0], "src"))


logging.config.fileConfig("log.ini", disable_existing_loggers=True)
logger = logging.getLogger()

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/test")
def get_all_students_course(name: str | None = None):
    pass
    return {"message": f"Hello {name}"}


@app.post("/bot/notice")
def receive_data(
    notification_type: str = Form(...),
    operation_id: str = Form(...),
    amount: float = Form(...),
    withdraw_amount: float = Form(...),
    currency: str = Form(...),
    datetime: datetime = Form(...),
    sender: str = Form(...),
    codepro: bool = Form(...),
    label: str = Form(...),
    sha1_hash: str = Form(...),
    test_notification: bool = Form(...),
    unaccepted: bool = Form(...),
):
    data = {
        "notification_type": notification_type,
        "operation_id": operation_id,
        "amount": amount,
        "withdraw_amount": withdraw_amount,
        "currency": currency,
        "datetime": datetime,
        "sender": sender,
        "codepro": codepro,
        "label": label,
        "sha1_hash": sha1_hash,
        "test_notification": test_notification,
        "unaccepted": unaccepted,
    }
    pprint(data)


if __name__ == "__main__":
    uvicorn.run(app, host="172.17.0.1", port=5000)
    # uvicorn.run("_serv:app", host="127.0.0.1", port=5000, workers=2, reload=True)
