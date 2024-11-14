from datetime import date as date_cls
from datetime import datetime

from fastui.components.display import DisplayLookup, DisplayMode
from fastui.events import GoToEvent
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import BigInteger, Date, DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from core.config import Base
from db.models import ReportStatus


class Reports(Base):
    __tablename__ = "reports"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            'userdata.telegram_id',
            ondelete="CASCADE",
        ),
        type_=BigInteger,
    )
    user_name: Mapped[str | None] = mapped_column(default=None)
    info: Mapped[str]
    pictures: Mapped[dict | None] = mapped_column(type_=JSONB, default=None)
    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus, values_callable=lambda obj: [e.value for e in obj]),
        default=ReportStatus.created,
    )
    create_date: Mapped[date_cls] = mapped_column(type_=Date, server_default=func.now())
    updated: Mapped[datetime] = mapped_column(
        type_=DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.current_timestamp(),
    )

    class ValidationSchema(BaseModel):
        id: int | None = Field(default=None, title="ID")
        user_id: int = Field(title="Telegram ID")
        user_name: str | None = Field(default=None, title="Name")
        info: str = Field(title="Info")
        pictures: dict | None = Field(default={}, title="Pictures")
        status: ReportStatus = Field(default=ReportStatus.created, title="Status")
        create_date: date_cls = Field(title="Create date")
        updated: datetime | None = Field(
            default=None, title="Last update"
        )  # None def big_form_post

        site_updated: str = Field(init=False, title="Last update", default="00:00")

        @model_validator(mode="after")
        def set_updated(cls, values: BaseModel):
            if hasattr(values, "updated") and hasattr(values.updated, "ctime"):
                values.site_updated = values.updated.astimezone().ctime()
            return values

        model_config = ConfigDict(extra="ignore")

    # INTERFACE (fastui)
    site_display = [
        DisplayLookup(
            field="id",
            on_click=GoToEvent(
                url="/bot/tables/reports/?report_id={id}&telegram_id={user_id}"
            ),
        ),
        DisplayLookup(
            field="user_id",
            mode=DisplayMode.plain,
            on_click=GoToEvent(url="/bot/tables/userdata/?telegram_id={user_id}"),
        ),
        DisplayLookup(field="user_name", mode=DisplayMode.as_title),
        DisplayLookup(field="status"),
        DisplayLookup(field="create_date", mode=DisplayMode.date),
    ]
    site_display_all = site_display + [
        DisplayLookup(field="site_updated"),
        DisplayLookup(field="info"),
    ]

    def __init__(self, **kwargs):
        if kwargs:
            validated_data = self.ValidationSchema(**kwargs).model_dump(
                exclude={"site_updated"}
            )

            super().__init__(**(validated_data))
        else:
            super().__init__(**(kwargs))
