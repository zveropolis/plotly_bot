import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastui import AnyComponent, FastUI
from fastui import components as c
from fastui.events import BackEvent, GoToEvent, PageEvent
from pydantic import BaseModel, Field
from sqlalchemy import and_, select, update

from core.err import DatabaseError
# from db.utils import get_all_users
from db import models as mod
from db.database import execute_query
from server.fast_pages.shared import bot_page, patched_fastui_form, tabs
from server.utils.auth_user import User

router = APIRouter()
queue = logging.getLogger("queue")


class ReportStatus(BaseModel):
    id: int = Field(title="ID")
    user_id: int = Field(title="Telegram ID")
    status: mod.ReportStatus = Field(title="New Status")


@router.get("/", response_model=FastUI, response_model_exclude_none=True)
async def report_profile(
    user: Annotated[User, Depends(User.from_request)],
    report_id: int,
    telegram_id: int,
) -> list[AnyComponent]:
    try:
        _table = mod.Reports

        query = (
            select(_table)
            .where(
                and_(
                    _table.id == report_id,
                    _table.user_id == telegram_id,
                )
            )
            .order_by(_table.id)
        )
        raw_report: mod.Reports = (await execute_query(query)).scalar_one_or_none()
        if raw_report:
            report = _table.ValidationSchema.model_validate(
                raw_report, from_attributes=True
            )
        else:
            return bot_page(c.Paragraph(text="Report not found"), user=user)

    except DatabaseError:
        raise HTTPException(status_code=500, detail="Database Error")
    else:
        return bot_page(
            *tabs(),
            c.Div(
                components=[
                    c.Button(
                        text="Back", named_style="secondary", on_click=BackEvent()
                    ),
                    c.Button(
                        text="Change Status", on_click=PageEvent(name="change-status")
                    ),
                    c.Modal(
                        title="Change Status",
                        body=[
                            c.Paragraph(text="Choose new status for this report"),
                            c.ModelForm(
                                model=ReportStatus,
                                submit_url="/api/bot/tables/reports/report/send_status",
                                initial=dict(id=report.id, user_id=report.user_id),
                                footer=[],
                                submit_trigger=PageEvent(name="change-status-submit"),
                            ),
                        ],
                        footer=[
                            c.Button(
                                text="Cancel",
                                named_style="secondary",
                                on_click=PageEvent(name="change-status", clear=True),
                            ),
                            c.Button(
                                text="Submit",
                                on_click=PageEvent(name="change-status-submit"),
                            ),
                        ],
                        open_trigger=PageEvent(name="change-status"),
                    ),
                ],
                class_name="mt-3 pt-1",
            ),
            c.Details(data=report, fields=_table.site_display_all),
            *[
                c.Image(
                    src=f"/bugs/{folder}/{image}",
                    width=360,
                    height=640,
                    on_click=GoToEvent(
                        url=f"/bot/tables/reports/report/image/?id={report.id}&folder={folder}&image={image}"
                    ),
                    class_name="border rounded mt-3 pt-1",
                )
                for image, folder in report.pictures.items()
            ]
            if report.pictures
            else [],
            user=user,
            title=f'Report from user "{report.user_id}"',
        )


@router.post(
    "/report/send_status",
    response_model=FastUI,
    response_model_exclude_none=True,
)
async def change_report_status(
    form: Annotated[ReportStatus, patched_fastui_form(ReportStatus)],
):
    try:
        query = (
            update(mod.Reports)
            .values(status=form.status)
            .where(and_(mod.Reports.id == form.id, mod.Reports.user_id == form.user_id))
        )
        await execute_query(query)
    except Exception as e:
        return [
            c.FireEvent(event=PageEvent(name="status-not-changed")),
            c.Toast(
                title="Toast",
                body=[
                    c.Paragraph(text=f"Error: {e.args[0] if e.args else 500}"),
                ],
                open_trigger=PageEvent(name="status-not-changed"),
                position="bottom-end",
            ),
        ]
    else:
        queue.info(
            "Изменен статус обращения",
            extra={
                "type": "REPORT",
                "user_id": form.user_id,
                "label": form.id,
                "amount": form.status,
            },
        )

        return [
            c.FireEvent(
                event=GoToEvent(
                    url="/bot/tables/reports"  # report_id={form.id}&telegram_id={form.user_id}"
                )
            )
        ]


@router.get(
    "/report/image/",
    response_model=FastUI,
    response_model_exclude_none=True,
)
async def report_image(
    user: Annotated[User, Depends(User.from_request)],
    id: int,
    folder: str,
    image: str,
):
    return bot_page(
        c.Button(
            text="Назад",
            on_click=BackEvent(),
            named_style="secondary",
            class_name="+ ms-2",
        ),
        c.Div(
            components=[
                c.Image(
                    src=f"/bugs/{folder}/{image}",
                    class_name="border rounded mt-3 pt-1",
                )
            ],
            class_name="mt-3 pt-1",
        ),
        user=user,
        title=f"Report {id}",
    )
