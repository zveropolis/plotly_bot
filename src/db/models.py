import enum
from datetime import datetime
from ipaddress import IPv4Address, IPv4Interface
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import BigInteger, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import INET, CIDR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.config import Base


class UserActivity(enum.Enum):
    active = "active"
    inactive = "inactive"
    deleted = "deleted"

    def __str__(self) -> str:
        return self.value


class UserData(Base):
    class ValidationSchema(BaseModel):
        telegram_id: int
        telegram_name: str | None
        admin: bool
        active: UserActivity
        stage: int
        month: int

    def __init__(self, **kw):
        validated_data = self.ValidationSchema(**kw).__dict__

        super().__init__(**(kw | validated_data))

    __tablename__ = "userdata"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(type_=BigInteger, unique=True)
    telegram_name: Mapped[str | None]
    admin: Mapped[bool]
    active: Mapped[UserActivity] = mapped_column(
        Enum(UserActivity, values_callable=lambda obj: [e.value for e in obj])
    )
    stage: Mapped[int]
    month: Mapped[int]

    configs: Mapped[list["WgConfig"]] = relationship(back_populates="conf_connect")


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
    transaction_reference: Mapped[str | None]
    transaction_label: Mapped[UUID]
    transaction_date: Mapped[datetime]
    transaction_sum: Mapped[int]
    transaction_stage: Mapped[int]
    transaction_month: Mapped[int]


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
    name: Mapped[str | None]
    user_private_key: Mapped[str] = mapped_column(String(44))
    address: Mapped[IPv4Interface] = mapped_column(type_=CIDR)
    dns: Mapped[IPv4Address] = mapped_column(type_=INET)
    server_public_key: Mapped[str] = mapped_column(String(44))
    allowed_ips: Mapped[IPv4Interface] = mapped_column(type_=CIDR)
    endpoint_ip: Mapped[str] = mapped_column(type_=INET)
    endpoint_port: Mapped[int]

    conf_connect: Mapped[list["UserData"]] = relationship(back_populates="configs")
