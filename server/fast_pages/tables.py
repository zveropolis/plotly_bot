from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastui import AnyComponent, FastUI
from fastui import components as c
from fastui.events import BackEvent
from pydantic import BaseModel
from sqlalchemy import select
from yoomoney import Client
from yoomoney.exceptions import YooMoneyError

from core.config import settings
from core.err import DatabaseError
from db import models as mod
from db.database import execute_query
from server.fast_pages.shared import bot_page, tabs
from server.utils.auth_user import User

router = APIRouter()


@router.get("/yoomoney", response_model=FastUI, response_model_exclude_none=True)
async def yoomoney_view(
    user: Annotated[User, Depends(User.from_request)],
    page: int = 1,
) -> list[AnyComponent]:
    try:
        _table = mod.YoomoneyOperation
        client = Client(settings.YOO_TOKEN.get_secret_value())

        history = client.operation_history()
        size = user.page_size

        data = [
            _table.model_validate(operation, from_attributes=True)
            for operation in history.operations
        ]

    except YooMoneyError:
        raise HTTPException(status_code=500, detail="Yoomoney Connection Error")
    else:
        return bot_page(
            *tabs(),
            c.Table(
                data=data[(page - 1) * size : page * size],
                columns=mod.yoomoney_site_display,
            )
            if data
            else c.Paragraph(text="Empty table"),
            c.Pagination(page=page, page_size=size, total=len(data)),
            user=user,
            title=_table.__tablename__.capitalize(),
        )


@router.get("/yoomoney/", response_model=FastUI, response_model_exclude_none=True)
async def yoomoney_operation_profile(
    user: Annotated[User, Depends(User.from_request)],
    operation_id: str,
) -> list[AnyComponent]:
    try:
        client = Client(settings.YOO_TOKEN.get_secret_value())
        details = client.operation_details(operation_id)
        data = mod.YoomoneyOperationDetails.model_validate(
            details, from_attributes=True
        )

    except YooMoneyError:
        return bot_page(c.Paragraph(text="Operation not found"), user=user)
        raise HTTPException(status_code=500, detail="Yoomoney Connection Error")
    else:
        return bot_page(
            *tabs(),
            c.Div(
                components=[
                    c.Button(
                        text="Back", named_style="secondary", on_click=BackEvent()
                    ),
                ],
                class_name="mt-3 pt-1",
            ),
            c.Details(data=data),
            user=user,
            title=f'Operation "{details.operation_id}"',
        )


@router.get("/{table}", response_model=FastUI, response_model_exclude_none=True)
async def tables_view(
    user: Annotated[User, Depends(User.from_request)],
    table: str,
    page: int = 1,
) -> list[AnyComponent]:
    try:
        _table = mod.TABLES_SCHEMA.get(table)
        assert _table
        schema: BaseModel = _table.ValidationSchema
        size = user.page_size

        query = select(_table).order_by(_table.id)
        raw: list = (await execute_query(query)).scalars().all()
        data = [schema.model_validate(row, from_attributes=True) for row in raw]

        # TABLE = c.Table(data=,columns=[DisplayLookup() for column in tables[table].columns])

    except AssertionError:
        raise HTTPException(status_code=404, detail="Item not found")
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Database Error")
    else:
        return bot_page(
            *tabs(),
            c.Table(
                data=data[(page - 1) * size : page * size], columns=_table.site_display
            )
            if data
            else c.Paragraph(text="Empty table"),
            c.Pagination(page=page, page_size=size, total=len(data)),
            user=user,
            title=table.capitalize(),
        )


@router.get("/userdata/", response_model=FastUI, response_model_exclude_none=True)
async def user_profile(
    user: Annotated[User, Depends(User.from_request)],
    telegram_id: int,
) -> list[AnyComponent]:
    try:
        _table = mod.UserData

        query = select(_table).where(_table.telegram_id == telegram_id)
        raw_tg_user: mod.UserData = (await execute_query(query)).scalar_one_or_none()
        if raw_tg_user:
            tg_user = _table.ValidationSchema.model_validate(
                raw_tg_user, from_attributes=True
            )

            query = (
                select(mod.Transactions)
                .where(mod.Transactions.user_id == tg_user.telegram_id)
                .order_by(mod.Transactions.id)
            )
            raw: list = (await execute_query(query)).scalars().all()
            transactions = [
                mod.Transactions.ValidationSchema.model_validate(
                    row, from_attributes=True
                )
                for row in raw
            ]

        else:
            return bot_page(c.Paragraph(text="User not found"), user=user)

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
                ],
                class_name="mt-3 pt-1",
            ),
            c.Details(data=tg_user, fields=_table.site_display),
            c.Heading(text="User configurations", level=3),
            c.Table(
                data=tg_user.configs,
                columns=mod.WgConfig.site_display,
            )
            if tg_user.configs
            else c.Paragraph(text="No configs"),
            c.Heading(text="User tranasactions", level=3),
            c.Table(
                data=transactions,
                columns=mod.Transactions.site_display,
            )
            if transactions
            else c.Paragraph(text="No transactions"),
            user=user,
            title=tg_user.telegram_name,
        )


@router.get("/wg_config/", response_model=FastUI, response_model_exclude_none=True)
async def config_profile(
    user: Annotated[User, Depends(User.from_request)],
    name: str,
) -> list[AnyComponent]:
    try:
        _table = mod.WgConfig

        query = select(_table).where(_table.name == name)
        raw_config: mod.WgConfig = (await execute_query(query)).scalar_one_or_none()
        if raw_config:
            config = _table.ValidationSchema.model_validate(
                raw_config, from_attributes=True
            )

        else:
            return bot_page(c.Paragraph(text="Config not found"), user=user)

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
                ],
                class_name="mt-3 pt-1",
            ),
            c.Details(data=config, fields=_table.site_display_all),
            user=user,
            title=f'Configuration "{config.name}"',
        )


@router.get("/transactions/", response_model=FastUI, response_model_exclude_none=True)
async def transaction_profile(
    user: Annotated[User, Depends(User.from_request)],
    label: str,
) -> list[AnyComponent]:
    try:
        _table = mod.Transactions

        query = select(_table).where(_table.label == label).order_by(_table.id)
        raw_transactions: list[mod.Transactions] = (
            (await execute_query(query)).scalars().all()
        )
        if raw_transactions:
            transactions = [
                _table.ValidationSchema.model_validate(row, from_attributes=True)
                for row in raw_transactions
            ]
            try:
                client = Client(settings.YOO_TOKEN.get_secret_value())
                history = client.operation_history()

                yoomoney_data = [
                    mod.YoomoneyOperation.model_validate(
                        operation, from_attributes=True
                    )
                    for operation in history.operations
                    if operation.operation_id
                    in [transaction.transaction_id for transaction in transactions]
                ]
            except YooMoneyError:
                yoomoney_data = []

        else:
            return bot_page(c.Paragraph(text="Config not found"), user=user)

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
                ],
                class_name="mt-3 pt-1",
            ),
            *[
                c.Details(data=transaction, fields=_table.site_display_all)
                for transaction in transactions
            ],
            c.Table(
                data=yoomoney_data,
                columns=mod.yoomoney_site_display,
            )
            if yoomoney_data
            else c.Paragraph(text="Yoomoney no matches found"),
            user=user,
            title=f'Transactions from user "{transactions[0].user_id}"',
        )
