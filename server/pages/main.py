import asyncio
import logging
import os
from typing import Annotated

from fastapi import APIRouter, Depends
from fastui import AnyComponent, FastUI
from fastui import components as c
from fastui.events import GoToEvent, PageEvent

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
                            width=300,
                            height=300,
                        ),
                        c.Div(
                            components=[
                                c.Heading(text="DanVPN"),
                                c.Markdown(text="""# **ПРОСТО** *БЫСТРО* `АНОНИМНО`"""),
                            ],
                            class_name="ml-3",  # Отступ слева от изображения
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
        c.Div(
            components=[
                c.Image(
                    src="/static/qr.png",
                    alt="DanVPN QR",
                    width=200,
                    height=240,
                )
            ],
            class_name="mt-3 pt-1",
        ),
        *get_news(),
        user=user,
    )


def get_news():
    return (
        c.Heading(text="Новости", level=1, class_name="mt-4 pt-1"),
        c.Div(
            components=[
                c.Heading(text="News title", level=4),
                c.Markdown(text=("Изменения, новые пользователи")),
                c.Button(
                    text="Подробнее",
                    on_click=PageEvent(name="extra-news"),
                    named_style="secondary",
                ),
                c.Modal(
                    title="Extra News",
                    body=[c.ServerLoad(path="/bot/extra-content")],
                    footer=[
                        c.Button(
                            text="Close",
                            on_click=PageEvent(name="extra-news", clear=True),
                        ),
                    ],
                    open_trigger=PageEvent(name="extra-news"),
                ),
            ],
            class_name="border-top mt-3 pt-1",
        ),
    )


@router.get("/extra-content", response_model=FastUI, response_model_exclude_none=True)
async def modal_view() -> list[AnyComponent]:
    await asyncio.sleep(0.5)
    return [c.Paragraph(text="Изменения, новые пользователи. Подробно")]


@router.get("/{path:path}", status_code=404)
async def api_404():
    # so we don't fall through to the index page
    return {"message": "Not Found"}
