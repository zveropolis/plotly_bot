#!./.venv/bin/python


import logging
import logging.config
import os
import sys
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Form

sys.path.insert(1, os.path.join(sys.path[0], "server"))
sys.path.insert(1, os.path.join(sys.path[0], "src"))

from src.app import models as mod
from src.db.utils import confirm_success_pay

server_log = "./server/log.ini"
logging.config.fileConfig(server_log, disable_existing_loggers=False)
logger = logging.getLogger()
queue = logging.getLogger("queue")
app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/test")
def test_message(name: str | None = None):
    return {"message": f"Hello {name}"}


@app.post("/bot/notice")
async def receive_pay_data(
    notification_type: str = Form(default=""),
    operation_id: str = Form(default=""),
    amount: float = Form(default=0.0),
    withdraw_amount: float = Form(default=0.0),
    currency: str = Form(default=""),
    datetime: datetime = Form(default=datetime(1999, 1, 30, 0, 0, 0, 0)),
    sender: str = Form(default=""),
    codepro: bool = Form(default=False),
    label: str = Form(default="00000000-0000-0000-0000-000000000000"),
    sha1_hash: str = Form(default=""),
    test_notification: bool = Form(default=None),
    unaccepted: bool = Form(default=None),
):
    data = {
        "notification_type": notification_type,
        "transaction_id": operation_id,
        "amount": amount,
        "withdraw_amount": withdraw_amount,
        "currency": currency,
        "date": datetime,
        "sender": sender,
        "codepro": codepro,
        "label": label,
        "sha1_hash": sha1_hash,
        "test_notification": test_notification,
        "unaccepted": unaccepted,
    }
    logger.info("Принято уведомление об оплате", extra=data)

    transaction: mod.Transactions = await confirm_success_pay(mod.Transactions(**data))

    logger.info(f"Обновлены данные по транзакции {transaction}")
    queue.info(
        "Регистрация транзакции в очереди",
        extra={
            "type": "TRANSACTION",
            "user_id": transaction.user_id,
            "label": label,
            "month": transaction.transaction_month,
            "stage": transaction.transaction_stage,
        },
    )
    return {"status": str(transaction)}


if __name__ == "__main__":
    with open("./logs/server.log", "w"), open("./logs/psql_serv.log", "w"):
        ...
    uvicorn.run(
        "_serv:app",
        # host="127.0.0.1",
        host="172.17.0.1",
        port=5000,
        workers=2,
        # reload=True,
        log_config=server_log,
        log_level="info",
        use_colors=False,
    )
