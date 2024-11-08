import logging
import os
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select

from server.utils.auth_user import User
from src.app import models as mod
from src.core.path import PATH
from src.db.database import execute_query

router = APIRouter()
logger = logging.getLogger()


templates = Jinja2Templates(directory=os.path.join(PATH, "server", "templates"))

configs = [
    {
        "name": "Config Name",
        "PrivateKey": "GLzrInt9vGguqXi8r+Dli6K5CCzSe/5Zg8OH8wfk4V8=",
        "Address": "10.1.0.181/32",
        "DNS": " 10.0.0.1,9.9.9.9",
        "PublicKey": "xlaQzDNN/L5VWGVfW2r4pR9ufa0tr0kXwA1U2kilNho=",
        "AllowedIPs": "0.0.0.0/0",
        "Endpoint": "185.242.107.63:51830",
        "PersistentKeepalive": "25",
    }
] * 5


@router.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    query = select(mod.News).order_by(mod.News.id)
    news: list[mod.News] = (await execute_query(query)).scalars().all()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "news": [
                {
                    "date": new.date.ctime().replace("00:00:00", ""),
                    "title": new.title,
                    "excerpt": new.excerpt,
                    "id": new.news_id,
                }
                for new in news
            ],
            "news_content": {
                new.news_id: {"title": new.content_title, "content": new.content}
                for new in news
            },
        },
    )


# @router.get("/profile", response_class=HTMLResponse)
# async def profile_page(request: Request):
#     return templates.TemplateResponse(
#         "profile.html", {"request": request, "configsData": configs}
#     )


# @router.get("/auth", response_class=HTMLResponse)
# async def auth_page(request: Request):
#     return templates.TemplateResponse("auth.html", {"request": request})


@router.get("/pricing", response_class=HTMLResponse)
async def pricing_page(request: Request):
    return templates.TemplateResponse("pricing.html", {"request": request})


@router.get("/{path:path}", response_class=HTMLResponse)
async def not_found(request: Request):
    return templates.TemplateResponse("404.html", {"request": request})
