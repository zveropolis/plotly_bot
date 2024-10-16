import logging
import os
from datetime import datetime, timedelta

from pandas import DataFrame, ExcelWriter
from sqlalchemy import select

from core.exceptions import BackupError
from core.path import PATH
from db.database import execute_query
from db.models import Transactions, UserData, WgConfig

logger = logging.getLogger()


async def async_backup():
    filename = os.path.join(
        PATH,
        "src",
        "db",
        "backups",
        f"backup_{datetime.today().strftime('%d_%m_%Y-%H_%M')}.xlsx",
    )
    with ExcelWriter(filename, engine="openpyxl", mode="w") as writer:
        try:
            for model in (UserData, WgConfig, Transactions):
                query = select(model).order_by(model.id)
                res = await execute_query(query)

                df = DataFrame(data=[line.__udict__ for line in res.scalars().all()])

                date_columns = df.select_dtypes(include=["datetime64[ns, UTC]"]).columns
                for date_column in date_columns:
                    df[date_column] = df[date_column].dt.tz_localize(None)
                    df[date_column] = df[date_column] + timedelta(hours=3)

                df.to_excel(writer, sheet_name=model.__tablename__, index=False)
        except Exception:
            logger.exception("Ошибка создания дампа БД")
            raise BackupError
        else:
            return filename
