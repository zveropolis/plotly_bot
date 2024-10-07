import enum
from datetime import datetime
from ipaddress import IPv4Address, IPv4Interface
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from random_word import RandomWords
from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import CIDR, INET
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.config import Base, settings
from db import ddl  # TRIGGERS

name_gen = RandomWords()


class UserActivity(enum.Enum):
    active = "active"
    inactive = "inactive"
    freezed = "freezed"
    deleted = "deleted"
    banned = "banned"

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
    balance: Mapped[float] = mapped_column(default=0)
    free: Mapped[bool] = mapped_column(default=True)

    configs: Mapped[list["WgConfig"]] = relationship(
        back_populates="conf_connect", lazy="subquery"
    )

    class ValidationSchema(BaseModel):
        telegram_id: int
        telegram_name: str
        admin: bool
        active: UserActivity
        stage: float
        balance: float
        free: bool

        model_config = ConfigDict(extra="ignore")

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
    transaction_id: Mapped[int | None] = mapped_column(type_=BigInteger)
    sha1_hash: Mapped[str | None]
    sender: Mapped[str | None]
    withdraw_amount: Mapped[float | None]

    # additionally
    transaction_reference: Mapped[str]

    class ValidationSchema(BaseModel):
        user_id: int | None = None
        date: datetime
        amount: float
        label: UUID

        transaction_id: int | None = None
        sha1_hash: str | None = None
        sender: str | None = None
        withdraw_amount: float | None = None

        model_config = ConfigDict(extra="ignore")

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
    name: Mapped[str] = mapped_column(default=name_gen.get_random_word)
    freeze: Mapped[bool] = mapped_column(default=False)
    user_private_key: Mapped[str] = mapped_column(String(44))
    address: Mapped[IPv4Interface] = mapped_column(type_=CIDR)
    dns: Mapped[IPv4Address] = mapped_column(type_=INET, default="9.9.9.9")
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
        user_id: int
        name: str
        freeze: bool
        user_private_key: str
        address: IPv4Interface
        dns: IPv4Address
        server_public_key: str
        allowed_ips: IPv4Interface
        endpoint_ip: IPv4Address
        endpoint_port: int

        model_config = ConfigDict(extra="ignore")

    def __init__(self, **kwargs):
        if kwargs:
            validated_data = self.ValidationSchema(**kwargs).__dict__

            super().__init__(**(validated_data))
        else:
            super().__init__(**(kwargs))
