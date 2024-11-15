from datetime import date as date_cls

from fastui.components.display import DisplayLookup, DisplayMode
from fastui.events import GoToEvent
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Date, func
from sqlalchemy.orm import Mapped, mapped_column

from core.config import Base


class News(Base):
    """Модель новостей.

    Эта модель представляет собой структуру данных для хранения новостей,
    включая заголовок, содержание и другие атрибуты.
    """

    __tablename__ = "news"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    """int: Уникальный идентификатор новости."""

    date: Mapped[date_cls] = mapped_column(type_=Date, server_default=func.now())
    """date_cls: Дата создания новости (по умолчанию - текущая дата)."""

    title: Mapped[str]
    """str: Заголовок новости."""

    excerpt: Mapped[str]
    """str: Краткое содержание новости."""

    content_title: Mapped[str]
    """str: Заголовок содержания новости."""

    content: Mapped[str]
    """str: Полное содержание новости."""

    class ValidationSchema(BaseModel):
        """Схема валидации для модели новостей.

        Эта схема используется для валидации данных, связанных с новостями.
        """

        id: int | None = Field(default=None, title="ID")
        """Уникальный идентификатор новости."""

        date: date_cls = Field(title="Create date")
        """Дата создания новости."""

        title: str = Field(title="Title")
        """Заголовок новости."""

        excerpt: str = Field(title="Excerpt")
        """Краткое содержание новости."""

        content_title: str = Field(title="Content Title")
        """Заголовок содержания новости."""

        content: str = Field(title="Content")
        """Полное содержание новости."""

        model_config = ConfigDict(extra="ignore")

    # INTERFACE (fastui)
    site_display = [
        DisplayLookup(
            field="id",
            on_click=GoToEvent(url="/bot/tables/news/?news_id={id}"),
        ),
        DisplayLookup(field="title"),
        DisplayLookup(field="date", mode=DisplayMode.date),
    ]
    """list[DisplayLookup]: Отображение новостей на сайте."""

    site_display_all = site_display + [
        DisplayLookup(field="excerpt"),
        DisplayLookup(field="content_title"),
        DisplayLookup(field="content", mode=DisplayMode.markdown),
    ]
    """list[DisplayLookup]: Полное отображение новостей на сайте."""

    def __init__(self, **kwargs):
        """Инициализирует модель новостей.

        Args:
            **kwargs: Дополнительные параметры для инициализации модели.
        """
        if kwargs:
            validated_data = self.ValidationSchema(**kwargs).model_dump(
                exclude={"site_date"}
            )
            super().__init__(**(validated_data))
        else:
            super().__init__(**(kwargs))
