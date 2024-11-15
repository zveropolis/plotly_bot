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
    """Модель конфигурации WireGuard.

    Эта модель представляет собой структуру данных для хранения конфигураций
    WireGuard, связанных с пользователями.
    """

    __tablename__ = "wg_config"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    """int: Уникальный идентификатор конфигурации WireGuard."""

    user_id: Mapped[int] = mapped_column(
        ForeignKey("userdata.telegram_id", ondelete="CASCADE"),
        type_=BigInteger,
    )
    """int: Идентификатор пользователя в Telegram, связанный с конфигурацией."""

    name: Mapped[str] = mapped_column(default=name_gen.get_random_word, unique=True)
    """str: Название конфигурации (по умолчанию генерируется случайным образом)."""

    freeze: Mapped[FreezeSteps] = mapped_column(
        Enum(FreezeSteps, values_callable=lambda obj: [e.value for e in obj]),
        default=FreezeSteps.no,
    )
    """FreezeSteps: Статус заморозки конфигурации (по умолчанию 'no')."""

    user_private_key: Mapped[str] = mapped_column(String(44))
    """str: Приватный ключ пользователя для WireGuard."""

    address: Mapped[IPv4Interface] = mapped_column(type_=CIDR)
    """IPv4Interface: IP-адрес конфигурации WireGuard."""

    dns: Mapped[str] = mapped_column(default="10.0.0.1,9.9.9.9")
    """str: DNS-серверы для конфигурации (по умолчанию '10.0.0.1,9.9.9.9')."""

    server_public_key: Mapped[str] = mapped_column(String(44))
    """str: Публичный ключ сервера для WireGuard."""

    allowed_ips: Mapped[IPv4Interface] = mapped_column(type_=CIDR, default="0.0.0.0/0")
    """IPv4Interface: Разрешенные IP-адреса для конфигурации (по умолчанию '0.0.0.0/0')."""

    endpoint_ip: Mapped[IPv4Address] = mapped_column(
        type_=INET, default=settings.WG_HOST
    )
    """IPv4Address: IP-адрес конечной точки WireGuard (по умолчанию из настроек)."""

    endpoint_port: Mapped[int] = mapped_column(default=settings.WG_PORT)
    """int: Порт конечной точки WireGuard (по умолчанию из настроек)."""

    conf_connect: Mapped["UserData"] = relationship(  # noqa: F821 # type: ignore
        back_populates="configs", lazy="subquery"
    )
    """UserData: Связанные данные пользователя для конфигурации WireGuard."""

    class ValidationSchema(BaseModel):
        """Схема валидации для модели конфигурации WireGuard.

        Эта схема используется для валидации данных, связанных с конфигурациями.
        """

        id: int | None = Field(default=None, title="ID")
        """Уникальный идентификатор конфигурации WireGuard."""

        user_id: int = Field(title="Telegram ID")
        """Идентификатор пользователя в Telegram."""

        name: str = Field(title="Title")
        """Название конфигурации."""

        freeze: FreezeSteps = Field(default=FreezeSteps.no, title="Freeze")
        """Статус заморозки конфигурации."""

        user_private_key: str = Field(title="User Priv Key")
        """Приватный ключ пользователя для WireGuard."""

        address: IPv4Interface = Field(title="Address")
        """IP-адрес конфигурации WireGuard."""

        dns: str = Field(default="10.0.0.1,9.9.9.9", title="DNS")
        """DNS-серверы для конфигурации."""

        server_public_key: str = Field(title="Server Pub Key")
        """Публичный ключ сервера для WireGuard."""

        allowed_ips: IPv4Interface = Field(default="0.0.0.0/0", title="Allowed IPs")
        """Разрешенные IP-адреса для конфигурации."""

        endpoint_ip: IPv4Address = Field(default=settings.WG_HOST, title="Endpoint IP")
        """IP-адрес конечной точки WireGuard."""

        endpoint_port: int = Field(default=settings.WG_PORT, title="Endpoint Port")
        """Порт конечной точки WireGuard."""

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
    """list[DisplayLookup]: Отображение конфигураций WireGuard на сайте."""

    site_display_all = site_display + [
        DisplayLookup(field="user_private_key", mode=DisplayMode.inline_code),
        DisplayLookup(field="server_public_key", mode=DisplayMode.inline_code),
        DisplayLookup(field="dns"),
        DisplayLookup(field="allowed_ips"),
        DisplayLookup(field="endpoint_ip"),
        DisplayLookup(field="endpoint_port"),
    ]
    """list[DisplayLookup]: Полное отображение конфигураций WireGuard на сайте."""

    def __init__(self, **kwargs):
        """Инициализирует модель конфигурации WireGuard.

        Args:
            **kwargs: Дополнительные параметры для инициализации модели.
        """
        if kwargs:
            validated_data = self.ValidationSchema(**kwargs).__dict__
            super().__init__(**(validated_data))
        else:
            super().__init__(**(kwargs))
