from collections.abc import Iterable
from datetime import datetime
from uuid import UUID

from fastui.components.display import DisplayLookup, DisplayMode
from fastui.events import GoToEvent
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from core.config import Base


class Transactions(Base):
    __tablename__ = "transactions"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "userdata.telegram_id",
            ondelete="CASCADE",
        ),
        type_=BigInteger,
    )
    date: Mapped[datetime] = mapped_column(type_=DateTime(timezone=True))
    amount: Mapped[float]
    label: Mapped[UUID]

    # PAYED
    transaction_id: Mapped[str | None]
    sha1_hash: Mapped[str | None]
    sender: Mapped[str | None]
    withdraw_amount: Mapped[float | None]

    # additionally
    transaction_reference: Mapped[str]

    class ValidationSchema(BaseModel):
        id: int | None = Field(default=None, title="ID")
        user_id: int | None = Field(default=None, title="Telegram ID")  # FROM YOOMONEY
        date: datetime = Field(title="Transaction date")
        amount: float = Field(title="Amount")
        label: UUID = Field(title="Label")

        transaction_id: str | None = Field(default=None, title="Transaction ID")
        sha1_hash: str | None = Field(default=None, title="Hash")
        sender: str | None = Field(default=None, title="Sender")
        withdraw_amount: float | None = Field(default=None, title="Withdraw_amount")

        transaction_reference: str | None = Field(
            default=None, title="Transaction Reference"
        )

        site_date: str = Field(init=False, title="Transaction date", default="00:00")

        @model_validator(mode="before")
        def convert_str_to_none(cls, values):
            if isinstance(values, Iterable):
                return {k: None if v == "None" else v for k, v in dict(values).items()}
            return values

        @model_validator(mode="after")
        def set_site_date(cls, values: BaseModel):
            if hasattr(values, "date"):
                values.site_date = values.date.astimezone().ctime()
            return values

        model_config = ConfigDict(extra="ignore")

    # INTERFACE (fastui)
    site_display = [
        DisplayLookup(field="id"),
        DisplayLookup(
            field="user_id",
            mode=DisplayMode.plain,
            on_click=GoToEvent(url="/bot/tables/userdata/?telegram_id={user_id}"),
        ),
        DisplayLookup(field="site_date"),
        DisplayLookup(field="amount"),
        DisplayLookup(
            field="label",
            on_click=GoToEvent(url="/bot/tables/transactions/?label={label}"),
        ),
    ]

    site_display_all = site_display + [
        DisplayLookup(field="sender"),
        DisplayLookup(field="transaction_id", mode=DisplayMode.plain),
        DisplayLookup(field="sha1_hash", mode=DisplayMode.inline_code),
        DisplayLookup(field="withdraw_amount"),
    ]

    def __init__(self, **kwargs):
        if kwargs:
            validated_data = self.ValidationSchema(**kwargs).model_dump(
                exclude={"site_date"}
            )

            super().__init__(**(validated_data))
        else:
            super().__init__(**(kwargs))
