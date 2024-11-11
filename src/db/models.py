import enum
from collections.abc import Iterable
from datetime import date as date_cls
from datetime import datetime
from ipaddress import IPv4Address, IPv4Interface
from uuid import UUID

from fastui.components.display import DisplayLookup, DisplayMode
from fastui.events import GoToEvent
from pydantic import BaseModel, ConfigDict, Field, model_validator
from random_word import RandomWords
from sqlalchemy import (BigInteger, Date, DateTime, Enum, ForeignKey, Numeric,
                        String, func)
from sqlalchemy.dialects.postgresql import CIDR, INET, JSONB
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.config import Base, settings
from db import ddl as _  # NOTE TRIGGERS

name_gen = RandomWords()


class UserActivity(enum.Enum):
    active = "active"
    inactive = "inactive"
    freezed = "freezed"
    deleted = "deleted"
    banned = "banned"

    def __str__(self) -> str:
        return self.value


class FreezeSteps(enum.Enum):
    yes = "yes"
    wait_yes = "wait_yes"
    no = "no"
    wait_no = "wait_no"

    def __str__(self) -> str:
        return self.value


class ReportStatus(enum.Enum):
    created = "created"
    at_work = "at_work"
    decided = "decided"
    cancelled = "cancelled"

    def __str__(self) -> str:
        return self.value


class UserData(Base):
    __tablename__ = "userdata"

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

    @hybrid_property
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
        DisplayLookup(field="Mute"),
        DisplayLookup(field="updated", mode=DisplayMode.datetime),
    ]

    def __init__(self, **kwargs):
        if kwargs:
            validated_data = self.ValidationSchema(**kwargs).__dict__

            super().__init__(**(validated_data))
        else:
            super().__init__(**(kwargs))


class Transactions(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            UserData.telegram_id,  # "userdata.id",
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

        @model_validator(mode="before")
        def convert_str_to_none(cls, values):
            if isinstance(values, Iterable):
                return {k: None if v == "None" else v for k, v in dict(values).items()}
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
        DisplayLookup(field="date", mode=DisplayMode.datetime),
        DisplayLookup(field="amount"),
        DisplayLookup(
            field="label",
            on_click=GoToEvent(url="/bot/tables/transactions/?label={label}"),
        ),
        DisplayLookup(field="sender"),
    ]

    site_display_all = site_display + [
        DisplayLookup(field="transaction_id", mode=DisplayMode.plain),
        DisplayLookup(field="sha1_hash", mode=DisplayMode.inline_code),
        DisplayLookup(field="withdraw_amount"),
    ]

    def __init__(self, **kwargs):
        if kwargs:
            validated_data = self.ValidationSchema(**kwargs).__dict__

            super().__init__(**(validated_data))
        else:
            super().__init__(**(kwargs))


class WgConfig(Base):
    __tablename__ = "wg_config"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            UserData.telegram_id,  # "userdata.id",
            ondelete="CASCADE",
        ),
        type_=BigInteger,
    )
    name: Mapped[str] = mapped_column(default=name_gen.get_random_word, unique=True)
    freeze: Mapped[FreezeSteps] = mapped_column(
        Enum(FreezeSteps, values_callable=lambda obj: [e.value for e in obj]),
        default=FreezeSteps.no,
    )
    user_private_key: Mapped[str] = mapped_column(String(44))
    address: Mapped[IPv4Interface] = mapped_column(type_=CIDR)
    dns: Mapped[str] = mapped_column(default="10.0.0.1,9.9.9.9")
    server_public_key: Mapped[str] = mapped_column(String(44))
    allowed_ips: Mapped[IPv4Interface] = mapped_column(type_=CIDR, default="0.0.0.0/0")
    endpoint_ip: Mapped[IPv4Address] = mapped_column(
        type_=INET, default=settings.WG_HOST
    )
    endpoint_port: Mapped[int] = mapped_column(default=settings.WG_PORT)

    conf_connect: Mapped[UserData] = relationship(
        back_populates="configs", lazy="subquery"
    )

    class ValidationSchema(BaseModel):
        id: int | None = Field(default=None, title="ID")
        user_id: int = Field(title="Telegram ID")
        name: str = Field(title="Title")
        freeze: FreezeSteps = Field(default=FreezeSteps.no, title="Freeze")
        user_private_key: str = Field(title="User Priv Key")
        address: IPv4Interface = Field(title="Address")
        dns: str = Field(default="10.0.0.1,9.9.9.9", title="DNS")
        server_public_key: str = Field(title="Server Pub Key")
        allowed_ips: IPv4Interface = Field(default="0.0.0.0/0", title="Allowed IPs")
        endpoint_ip: IPv4Address = Field(default=settings.WG_HOST, title="Endpoint IP")
        endpoint_port: int = Field(default=settings.WG_PORT, title="Endpoint Port")

        model_config = ConfigDict(extra="ignore")

    # INTERFACE (fastui)
    site_display = [
        DisplayLookup(field="id"),
        DisplayLookup(
            field="user_id",
            mode=DisplayMode.plain,
            on_click=GoToEvent(url="/bot/tables/userdata/?telegram_id={user_id}"),
        ),
        DisplayLookup(
            field="name",
            mode=DisplayMode.as_title,
            on_click=GoToEvent(url="/bot/tables/wg_config/?name={name}"),
        ),
        DisplayLookup(field="freeze"),
        DisplayLookup(field="address"),
    ]
    site_display_all = site_display + [
        DisplayLookup(field="user_private_key", mode=DisplayMode.inline_code),
        DisplayLookup(field="server_public_key", mode=DisplayMode.inline_code),
        DisplayLookup(field="dns"),
        DisplayLookup(field="allowed_ips"),
        DisplayLookup(field="endpoint_ip"),
        DisplayLookup(field="endpoint_port"),
    ]

    def __init__(self, **kwargs):
        if kwargs:
            validated_data = self.ValidationSchema(**kwargs).__dict__

            super().__init__(**(validated_data))
        else:
            super().__init__(**(kwargs))


class Reports(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            UserData.telegram_id,  # "userdata.id",
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
        DisplayLookup(field="updated", mode=DisplayMode.datetime),
        DisplayLookup(field="info"),
    ]

    def __init__(self, **kwargs):
        if kwargs:
            validated_data = self.ValidationSchema(**kwargs).__dict__

            super().__init__(**(validated_data))
        else:
            super().__init__(**(kwargs))


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


yoomoney_site_display: list = [
    DisplayLookup(
        field="operation_id",
        on_click=GoToEvent(url="/bot/tables/yoomoney/?operation_id={operation_id}"),
    ),
    DisplayLookup(field="status"),
    DisplayLookup(field="datetime", mode=DisplayMode.datetime),
    DisplayLookup(field="title"),
    DisplayLookup(field="amount"),
    DisplayLookup(field="label"),
]


class News(Base):
    __tablename__ = "news"

    id: Mapped[int] = mapped_column(primary_key=True)
    news_id: Mapped[str] = mapped_column(unique=True)
    date: Mapped[date_cls] = mapped_column(type_=Date, server_default=func.now())
    title: Mapped[str]
    excerpt: Mapped[str]
    content_title: Mapped[str]
    content: Mapped[str]

    class ValidationSchema(BaseModel):
        id: int | None = Field(default=None, title="ID")
        news_id: str = Field(title="News ID")
        date: date_cls = Field(title="Create date")
        title: str = Field(title="Title")
        excerpt: str = Field(title="Excerpt")
        content_title: str = Field(title="Content Title")
        content: str = Field(title="Content")

        model_config = ConfigDict(extra="ignore")

    # INTERFACE (fastui)
    site_display = [
        DisplayLookup(
            field="news_id",
            on_click=GoToEvent(url="/bot/tables/news/?news_id={news_id}"),
        ),
        DisplayLookup(field="title"),
        DisplayLookup(field="date", mode=DisplayMode.date),
    ]
    site_display_all = site_display + [
        DisplayLookup(field="excerpt"),
        DisplayLookup(field="content_title"),
        DisplayLookup(field="content"),
    ]

    def __init__(self, **kwargs):
        if kwargs:
            validated_data = self.ValidationSchema(**kwargs).__dict__

            super().__init__(**(validated_data))
        else:
            super().__init__(**(kwargs))


TABLES_SCHEMA = {
    UserData.__tablename__: UserData,
    Transactions.__tablename__: Transactions,
    WgConfig.__tablename__: WgConfig,
    Reports.__tablename__: Reports,
    YoomoneyOperation.__tablename__: YoomoneyOperation,
    News.__tablename__: News,
}
