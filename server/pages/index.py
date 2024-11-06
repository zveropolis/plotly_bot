import logging
import os
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from server.utils.auth_user import User
from src.core.path import PATH

router = APIRouter()
logger = logging.getLogger()


templates = Jinja2Templates(directory=os.path.join(PATH, "server", "templates"))

# Пример данных новостей
news_data = [
    {
        "date": "Nov 1, 2024",
        "title": "Запуск сервиса в тестовом режиме",
        "excerpt": "Уважаемый пользователь, сейчас наш сервис находится на стадии тестирования. Если вы столкнетесь с какой-либо проблемой в работе сервиса, пожалуйста воспользуйтесь командой /bug и сообщите нам о ней.",
        "id": "news1",
    }
]

news_content = {
    "news1": {
        "title": "🚀 Первый запуск! Полет нормальный.",
        "content": """
    <p>Дорогие пользователи! Мы рады сообщить, что наш VPN сервис успешно запущен и сейчас работает в тестовом режиме! 🎉</p>
    <p>Мы стремимся предоставить вам надежное и безопасное соединение, и на этом этапе мы будем внимательно следить за работой сервиса, чтобы устранить любые возможные проблемы.</p>
    <p>Пожалуйста, делитесь своими впечатлениями и сообщайте о любых замеченных ошибках. Для этого воспользуйтесь <a href="/bot/bug/create">ссылкой</a> либо командой `<a href="https://t.me/vpn_dan_bot">/bug</a>` в нашем чат-боте. Ваши отзывы помогут нам улучшить наш сервис!</p>""",
    }
}


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
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "news": news_data,
            "news_content": news_content,
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
