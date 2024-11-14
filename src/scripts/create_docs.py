import os
import sys
from pathlib import Path

import pdoc
from pdoc.render import configure

# Добавляем путь к директории проекта в системный путь
sys.path.insert(1, os.path.dirname(sys.path[0]))
from core.path import PATH


def create_docs():
    """Создает документацию для проекта с использованием pdoc.

    Эта функция настраивает параметры генерации документации и вызывает
    pdoc для создания документации из исходного кода проекта.

    Настройки документации включают формат документации, логотип, ссылку на логотип
    и URL для редактирования исходного кода на GitHub.

    Returns:
        None
    """
    path = Path(PATH)
    configure(
        docformat="google",
        logo="/static/Logo2_no_back_2.png",
        logo_link="/vpn",
        edit_url_map={
            "src": "https://github.com/daniil-mazurov/vpn_dan_bot/blob/DEV/src/"
        },
    )
    pdoc.pdoc(path / "src", output_directory=path / "docs")


if __name__ == "__main__":
    create_docs()
