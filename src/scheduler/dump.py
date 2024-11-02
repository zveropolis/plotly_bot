import logging
from datetime import datetime
from pathlib import Path

from core.config import settings
from core.exceptions import DumpError
from core.path import PATH
from db.utils import dump

logger = logging.getLogger("apscheduler")
logging.getLogger("apscheduler.executors.default").setLevel(logging.WARNING)


async def regular_dump():
    try:
        await dump(regular=True)

        folder_path = Path(PATH) / "src" / "db" / "dumps"

        dumps = [
            file
            for file in folder_path.iterdir()
            if file.is_file() and "regular" in file.name
        ]

        if len(dumps) > settings.max_dumps:
            dumps = sorted(
                dumps,
                key=lambda file: datetime.strptime(
                    file.name.split("dump")[-1].strip("_.sql"), "%d_%m_%Y-%H_%M"
                ),
            )
            for _dump in dumps[: len(dumps) - settings.max_dumps]:
                _dump.unlink()

    except DumpError:
        logger.exception("Ошибка создания регулярного дампа")
