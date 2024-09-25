import logging
import os
from datetime import datetime

from pandas import DataFrame, ExcelWriter
from sqlalchemy import select

from core.exceptions import DumpError
from core.path import PATH
from db.database import execute_query
from db.models import Transactions, UserData, WgConfig

logger = logging.getLogger()


async def async_dump():
    filename = os.path.join(
        PATH,
        "src",
        "db",
        "dumps",
        f"dump_{datetime.today().strftime('%d_%m_%Y-%H_%M')}.xlsx",
    )
    with ExcelWriter(filename, engine="openpyxl", mode="w") as writer:
        try:
            for model in (UserData, WgConfig, Transactions):
                query = select(model)
                res = await execute_query(query)
                DataFrame(
                    data=[line.__udict__ for line in res.scalars().all()]
                ).to_excel(writer, sheet_name=model.__tablename__, index=False)
        except Exception:
            raise DumpError
        else:
            return filename
