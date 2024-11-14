from ipaddress import IPv4Address, IPv4Interface

from fastui.components.display import DisplayLookup, DisplayMode
from fastui.events import GoToEvent
from pydantic import BaseModel, ConfigDict, Field
from random_word import RandomWords
from sqlalchemy import BigInteger, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import CIDR, INET
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.config import Base, settings
from db.models import FreezeSteps

name_gen = RandomWords()


class WgConfig(Base):
    __tablename__ = "wg_config"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "userdata.telegram_id",
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

    conf_connect: Mapped["UserData"] = relationship(  # noqa: F821 # type: ignore
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
