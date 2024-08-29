import os
import uuid
from dataclasses import dataclass

import aiofiles
import pyqrcode
from pandas import DataFrame

from core.path import PATH
from db.models import UserActivity, WgConfig

me = {"я", "мои данные", "данные", "конфиги", "мои конфиги", "config"}
DB_ERROR = "Ошибка подключения к БД. Обратитесь к администратору."
WG_ERROR = "Ошибка подключения к серверу wireguard. Обратитесь к администратору."
YOO_ERROR = "Ошибка подключения к серверу yoomoney. Попробуйте еще раз позже"
UNPAY = "Функционал создания конфигураций заблокирован. Действующие конфигурации заблокированы. Для разблокировки оплатите подписку."


@dataclass
class AccountStatuses:
    deleted = "Удален"
    admin = "Администратор"
    user = "Пользовательский"


def get_account_status(user_data: DataFrame):
    if user_data.active[0] == UserActivity.deleted:
        return AccountStatuses.deleted
    elif user_data.admin[0]:
        return AccountStatuses.admin
    else:
        return AccountStatuses.user


def get_sub_status(user_data: DataFrame):
    if user_data.active[0] == UserActivity.active:
        return f"Активна | {user_data.stage[0]} Уровень"
    elif user_data.active[0] == UserActivity.inactive:
        return "Неактивна"
    else:
        return ""


def get_config_data(user_config: WgConfig):
    return f"""[Interface]
PrivateKey = {user_config.user_private_key}
Address = {user_config.address}
DNS = {user_config.dns}
[Peer]
PublicKey = {user_config.server_public_key}
AllowedIPs = {user_config.allowed_ips}
Endpoint = {user_config.endpoint_ip}:{user_config.endpoint_port}
"""


async def create_config_file(config: str):
    path = os.path.join(PATH, "tmp", f"{uuid.uuid3(uuid.NAMESPACE_DNS, config)}.conf")

    async with aiofiles.open(path, "w") as file:
        await file.write(config)

    return path


def create_config_qr(config: str):
    path = os.path.join(PATH, "tmp", f"{uuid.uuid3(uuid.NAMESPACE_DNS, config)}.png")

    qr = pyqrcode.create(config)
    qr.png(path, scale=8)

    return path
