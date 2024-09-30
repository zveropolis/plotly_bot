#!./.venv/bin/python


from datetime import datetime
import logging
import logging.config
import os
from pprint import pprint
import sys
from typing import Annotated, List
from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile, Request
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
    notification_type: str = Form(default=""),
    operation_id: str = Form(default=""),
    amount: float = Form(default=0.0),
    withdraw_amount: float = Form(default=0.0),
    currency: str = Form(default=""),
    datetime: datetime = Form(default=datetime(1999, 30, 1, 0, 0, 0, 0)),
    sender: str = Form(default=""),
    codepro: bool = Form(default=False),
    label: str = Form(default=""),
    sha1_hash: str = Form(default=""),
    test_notification: bool = Form(default=True),
    unaccepted: bool = Form(default=False),
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
    return {"status": "success"}


if __name__ == "__main__":
    try:
        uvicorn.run(app, host="172.17.0.1", port=5000)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
    # uvicorn.run("_serv:app", host="127.0.0.1", port=5000, workers=2, reload=True)
