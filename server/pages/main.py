import logging
import os
from typing import Annotated

from fastapi import APIRouter, Depends
from fastui import AnyComponent, FastUI
from fastui import components as c
from fastui.events import GoToEvent

from core.path import PATH
from server.pages.shared import bot_page
from server.utils.auth_user import User

router = APIRouter()
logger = logging.getLogger()

with open(os.path.join(PATH, "server", "bot.md"), encoding="utf-8") as file:
    MAIN_TEXT = file.read()


@router.get("/", response_model=FastUI, response_model_exclude_none=True)
def api_index(
    user: Annotated[User | None, Depends(User.from_request_opt)],
) -> list[AnyComponent]:
    return bot_page(
        c.Div(
            components=[
                c.Div(
                    components=[
                        c.Image(
                            src="/static/Logo_no_back.png",
                            alt="DanVPN Logo",
                            width=200,
                            height=200,
                        ),
                        c.Div(
                            components=[
                                c.Heading(text="DanVPN"),
                                c.Markdown(text="""# **ПРОСТО** *БЫСТРО* `АНОНИМНО`"""),
                            ],
                            class_name="ml-1",  # Отступ слева от изображения
                        ),
                    ],
                    class_name="d-flex align-items-center",  # Используем Flexbox для горизонтального выравнивания
                )
            ],
            class_name="container mt-3",  # Обертка с отступами
        ),
        c.Div(
            components=[c.Markdown(text=MAIN_TEXT)],
            class_name="border-top mt-3 pt-1",
        ),
        c.Button(
            text="➣ Подключить",
            on_click=GoToEvent(url="https://t.me/vpn_dan_bot"),
        ),
        c.Button(
            text="Связаться с нами",
            on_click=GoToEvent(url="/bot/bug/create"),
            named_style="secondary",
            class_name="+ ms-2",
        ),
        user=user,
    )


@router.get("/{path:path}", status_code=404)
async def api_404():
    # so we don't fall through to the index page
    return {"message": "Not Found"}
