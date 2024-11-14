from datetime import datetime

from fastui.components.display import DisplayLookup, DisplayMode
from fastui.events import GoToEvent
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import BigInteger, DateTime, Enum, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.config import Base
from db.models import UserActivity
from db.models.wg_config import WgConfig


class UserData(Base):
    __tablename__ = "userdata"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(type_=BigInteger, unique=True)
    telegram_name: Mapped[str]
    admin: Mapped[bool] = mapped_column(default=False)
    active: Mapped[UserActivity] = mapped_column(
        Enum(UserActivity, values_callable=lambda obj: [e.value for e in obj]),
        default=UserActivity.inactive,
    )
    stage: Mapped[float] = mapped_column(default=0)
    balance: Mapped[float] = mapped_column(type_=Numeric(scale=2), default=0)
    free: Mapped[bool] = mapped_column(default=True)
    mute: Mapped[bool] = mapped_column(server_default="0")
    updated: Mapped[datetime] = mapped_column(
        type_=DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.current_timestamp(),
    )

    configs: Mapped[list["WgConfig"]] = relationship(
        back_populates="conf_connect", lazy="subquery"
    )

    # @hybrid_property
    def fbalance(self):
        return round(float(self.balance), 2)

    class ValidationSchema(BaseModel):
        id: int | None = Field(default=None, title="ID")
        telegram_id: int = Field(title="Telegram ID")
        telegram_name: str = Field(title="Name")
        admin: bool = Field(title="Admin", default=False)
        active: UserActivity = Field(title="Active", default=UserActivity.inactive)
        stage: float = Field(title="Stage", default=0)
        balance: float = Field(title="Balance", default=0)
        free: bool = Field(title="Free", default=True)
        mute: bool = Field(title="Mute", default=False)
        updated: datetime = Field(title="Last update")

        configs: list["WgConfig.ValidationSchema"] = Field(
            default=[], title="User Configurations"
        )

        site_updated: str = Field(init=False, title="Last update", default="00:00")

        @model_validator(mode="after")
        def set_site_date(cls, values: BaseModel):
            if hasattr(values, "updated"):
                values.site_updated = values.updated.astimezone().ctime()
            return values

        model_config = ConfigDict(extra="ignore")

    # INTERFACE (fastui)
    site_display = [
        DisplayLookup(field="id"),
        DisplayLookup(
            field="telegram_id",
            mode=DisplayMode.plain,
            on_click=GoToEvent(url="/bot/tables/userdata/?telegram_id={telegram_id}"),
        ),
        DisplayLookup(field="telegram_name", mode=DisplayMode.as_title),
        DisplayLookup(field="admin"),
        DisplayLookup(field="active", mode=DisplayMode.markdown),
        DisplayLookup(field="stage"),
        DisplayLookup(field="balance"),
        DisplayLookup(field="free"),
        DisplayLookup(field="mute"),
        DisplayLookup(field="site_updated"),
    ]

    def __init__(self, **kwargs):
        if kwargs:
            validated_data = self.ValidationSchema(**kwargs).model_dump(
                exclude={"site_updated"}
            )

            super().__init__(**(validated_data))
        else:
            super().__init__(**(kwargs))
