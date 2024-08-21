import enum
from datetime import datetime
from ipaddress import IPv4Address, IPv4Interface
from uuid import UUID

from sqlalchemy import BigInteger, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column

from core.config import Base


class UserActivity(enum.Enum):
    active = "active"
    inactive = "inactive"
    deleted = "deleted"


class UserData(Base):
    __tablename__ = "userdata"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(type_=BigInteger)
    telegram_name: Mapped[str | None]
    admin: Mapped[bool]
    active: Mapped[UserActivity] = mapped_column(
        Enum(UserActivity, values_callable=lambda obj: [e.value for e in obj])
    )


class Transactions(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            UserData.id,  # "userdata.id",
            ondelete="CASCADE",
        )
    )
    transaction_reference: Mapped[str | None]
    transaction_label: Mapped[UUID]
    transaction_date: Mapped[datetime]
    transaction_sum: Mapped[int]


class WgConfig(Base):
    __tablename__ = "wg_config"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            UserData.id,  # "userdata.id",
            ondelete="CASCADE",
        )
    )
    user_private_key: Mapped[str] = mapped_column(String(44))
    address: Mapped[IPv4Interface] = mapped_column(type_=INET)
    dns: Mapped[IPv4Address] = mapped_column(type_=INET)
    server_public_key: Mapped[str] = mapped_column(String(44))
    allowed_ips: Mapped[IPv4Interface] = mapped_column(type_=INET)
    endpoint: Mapped[str] = mapped_column(type_=INET)
