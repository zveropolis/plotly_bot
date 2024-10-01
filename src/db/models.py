import enum
from datetime import datetime
from ipaddress import IPv4Address, IPv4Interface
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Enum, ForeignKey, String, DateTime
from sqlalchemy.dialects.postgresql import CIDR, INET
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.config import Base
from db import ddl  # TRIGGERS


class UserActivity(enum.Enum):
    active = "active"
    inactive = "inactive"
    deleted = "deleted"

    def __str__(self) -> str:
        return self.value


class UserData(Base):
    __tablename__ = "userdata"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(type_=BigInteger, unique=True)
    telegram_name: Mapped[str]
    admin: Mapped[bool]
    active: Mapped[UserActivity] = mapped_column(
        Enum(UserActivity, values_callable=lambda obj: [e.value for e in obj])
    )
    stage: Mapped[int]
    month: Mapped[int]

    configs: Mapped[list["WgConfig"]] = relationship(
        back_populates="conf_connect", lazy="subquery"
    )

    class ValidationSchema(BaseModel):
        telegram_id: int
        telegram_name: str
        admin: bool
        active: UserActivity
        stage: int
        month: int

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
    transaction_stage: Mapped[int]
    transaction_month: Mapped[int]

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
        transaction_stage: int | None = None
        transaction_month: int | None = None

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
    name: Mapped[str]
    user_private_key: Mapped[str] = mapped_column(String(44))
    address: Mapped[IPv4Interface] = mapped_column(type_=CIDR)
    dns: Mapped[IPv4Address] = mapped_column(type_=INET)
    server_public_key: Mapped[str] = mapped_column(String(44))
    allowed_ips: Mapped[IPv4Interface] = mapped_column(type_=CIDR)
    endpoint_ip: Mapped[IPv4Address] = mapped_column(type_=INET)
    endpoint_port: Mapped[int]

    conf_connect: Mapped[UserData] = relationship(
        back_populates="configs", lazy="subquery"
    )

    class ValidationSchema(BaseModel):
        user_id: int
        name: str
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
