from datetime import date as date_cls

from fastui.components.display import DisplayLookup, DisplayMode
from fastui.events import GoToEvent
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Date, func
from sqlalchemy.orm import Mapped, mapped_column

from core.config import Base


class News(Base):
    __tablename__ = "news"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date_cls] = mapped_column(type_=Date, server_default=func.now())
    title: Mapped[str]
    excerpt: Mapped[str]
    content_title: Mapped[str]
    content: Mapped[str]

    class ValidationSchema(BaseModel):
        id: int | None = Field(default=None, title="ID")
        date: date_cls = Field(title="Create date")
        title: str = Field(title="Title")
        excerpt: str = Field(title="Excerpt")
        content_title: str = Field(title="Content Title")
        content: str = Field(title="Content")

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
    site_display_all = site_display + [
        DisplayLookup(field="excerpt"),
        DisplayLookup(field="content_title"),
        DisplayLookup(field="content", mode=DisplayMode.markdown),
    ]

    def __init__(self, **kwargs):
        if kwargs:
            validated_data = self.ValidationSchema(**kwargs).model_dump(
                exclude={"site_date"}
            )

            super().__init__(**(validated_data))
        else:
            super().__init__(**(kwargs))
