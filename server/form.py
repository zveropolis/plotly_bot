from datetime import date
import logging
import os
from typing import Annotated

import aiofiles
from fastapi import APIRouter, UploadFile
from fastui import FastUI
from fastui import components as c
from fastui.events import GoToEvent, PageEvent
from fastui.forms import FormFile, Textarea  # , fastui_form
from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError

from shared import bot_page, patched_fastui_form
from core.path import PATH

router = APIRouter()
logger = logging.getLogger()

UPLOAD_DIRECTORY = os.path.join(PATH, "bugs")  # Папка для загрузки файлов
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)


class BugModel(BaseModel):
    user_name: str | None = Field(
        None,
        title="Name",
        description="Представьтесь, чтобы мы знали как к вам обращаться",
    )

    telegram_id: int = Field(
        title="ID",
        description="Ваш ID в Telegram",
    )

    bug_info: Annotated[str, Textarea(rows=5)] = Field(
        title="Info",
        description="Описание вашей проблемы",
    )

    pics: (
        Annotated[list[UploadFile], FormFile(accept="image/*", max_size=3_100_000)]
        | None
    ) = Field(
        None,
        title="Pictures",
        description="Скриншоты проблемы. "
        "Если у вас проблемы с оплатой обязательно приложите скриншот совершенной транзакции (чек).",
    )

    date_of: date = Field(
        title="Date",
        description="Когда вы наблюдали проблему?",
    )

    human: bool = Field(
        title="Is human",
        description="Are you human?",
        json_schema_extra={"mode": "switch"},
    )

    @field_validator("human")
    def human_validator(cls, v: bool) -> bool:
        if v is False:
            raise PydanticCustomError(
                "Human", "Необходимо подтверждение того, что вы человек"
            )
        return v


@router.get("/create", response_model=FastUI, response_model_exclude_none=True)
def form_content(name: str | None = None, telegram_id: int | None = None):
    return bot_page(
        c.Heading(text="Опишите вашу проблему", level=2),
        c.ModelForm(
            model=BugModel,
            display_mode="page",
            submit_url="/api/bot/bug/send",
            initial=dict(user_name=name, telegram_id=telegram_id, date_of=date.today()),
            loading=[c.Spinner(text="Хорошо, отправляю ваш отчет...")],
        ),
        title="Отправить отчет о проблеме",
    )


@router.post("/send", response_model=FastUI, response_model_exclude_none=True)
async def big_form_post(form: Annotated[BugModel, patched_fastui_form(BugModel)]):
    try:
        logger.info("Принято сообщение о проблеме", extra=dict(form))

        for in_file in form.pics:
            content = await in_file.read()
            if content:
                file_location = os.path.join(UPLOAD_DIRECTORY, in_file.filename)

                async with aiofiles.open(file_location, "wb") as out_file:
                    await out_file.write(content)

    except Exception:
        logger.exception("Ошибка регистрации формы обращения в техподдержку")
        return [
            c.FireEvent(event=PageEvent(name="bug-sended")),
            c.Modal(
                title="Ошибка!",
                body=[
                    c.Paragraph(
                        text="Сожалеем, однако при отправке формы произошла ошибка. Пожалуйста попробуйте позже."
                    )
                ],
                footer=[
                    c.Button(text="Принято", on_click=GoToEvent(url="/bot/bug/create")),
                ],
                open_trigger=PageEvent(name="bug-sended"),
            ),
        ]
    else:
        return [
            c.FireEvent(event=PageEvent(name="bug-sended")),
            c.Modal(
                title="Успешно!",
                body=[
                    c.Paragraph(
                        text="Ваш отчет об ошибке успешно отправлен и будет обработан в ближайшее время"
                    )
                ],
                footer=[
                    c.Button(text="Принято", on_click=GoToEvent(url="/bot")),
                ],
                open_trigger=PageEvent(name="bug-sended"),
            ),
        ]


@router.get("/{path:path}", status_code=404)
async def api_404():
    # so we don't fall through to the index page
    return {"message": "Not Found"}
