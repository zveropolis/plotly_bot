from datetime import datetime

from fastui.components.display import DisplayLookup
from fastui.events import GoToEvent
from pydantic import BaseModel, Field, model_validator


class YoomoneyOperation(BaseModel):
    __tablename__ = "yoomoney"

    operation_id: str
    status: str
    datetime: datetime
    title: str
    pattern_id: str | None = None
    direction: str
    amount: float
    label: str
    type: str

    site_datetime: str = Field(init=False, title="Datetime", default="00:00")

    @model_validator(mode="after")
    def set_date(cls, values: BaseModel):
        if hasattr(values, "datetime"):
            values.site_datetime = values.datetime.astimezone().ctime()
        return values


class YoomoneyOperationDetails(BaseModel):
    operation_id: str
    status: str
    pattern_id: str | None = None
    direction: str
    amount: float
    amount_due: str | None = None
    fee: float | None = None
    answer_datetime: datetime | None = None
    datetime: datetime
    title: str
    sender: str | None = None
    recipient: str | None = None
    recipient_type: str | None = None
    message: str | None = None
    comment: str | None = None
    codepro: bool | None = None
    protection_code: str | None = None
    expires: str | None = None
    label: str
    details: str | None = None
    type: str
    digital_goods: str | None = None

    @model_validator(mode="before")
    def convert_ints_to_str(cls, values):
        return {
            k: str(v) if isinstance(v, int) else v for k, v in values.__dict__.items()
        }

    site_datetime: str = Field(init=False, title="Datetime", default="00:00")

    @model_validator(mode="after")
    def set_date(cls, values: BaseModel):
        if hasattr(values, "datetime"):
            values.site_datetime = values.datetime.astimezone().ctime()
        return values


yoomoney_site_display: list = [
    DisplayLookup(
        field="operation_id",
        on_click=GoToEvent(url="/bot/tables/yoomoney/?operation_id={operation_id}"),
    ),
    DisplayLookup(field="status"),
    DisplayLookup(field="site_datetime"),
    DisplayLookup(field="title"),
    DisplayLookup(field="amount"),
    DisplayLookup(field="label"),
]
