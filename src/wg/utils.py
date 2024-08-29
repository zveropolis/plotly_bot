import asyncio
import logging
import os
import sys
from typing import Literal

import asyncssh
from asyncssh import SSHClientConnection
from pydantic import validate_call

sys.path.insert(1, os.path.join("C:\\code\\vpn_dan_bot\\src"))

from core.config import settings
from core.exceptions import WireguardError

logger = logging.getLogger()


class WgConfigMaker:
    peer_counter = "~/Scripts/test"

    def __init__(self) -> None:
        self.private_key: str = None
        self.public_key: str = None
        self.countpeers: int = None

    async def _create_keys(self, conn: SSHClientConnection):
        try:
            private_key = await conn.run("wg genkey", check=True)
            self.private_key = private_key.stdout.strip("\n")

            public_key = await conn.run(
                f"echo {self.private_key} | wg pubkey", check=True
            )
            self.public_key = public_key.stdout.strip("\n")
        except (OSError, asyncssh.Error) as e:
            logger.exception(
                "Сбой при получении приватного и публичного ключа wireguard"
            )
            raise WireguardError from e

    async def _increment_counter(self, conn: SSHClientConnection):
        try:
            await conn.run(
                f'echo "$(($(cat {self.peer_counter})+1))" > {self.peer_counter}',
                check=True,
            )
            countpeers_future = await conn.run(f"cat {self.peer_counter}", check=True)
            self.countpeers = int(countpeers_future.stdout.strip("\n"))

        except (OSError, asyncssh.Error) as e:
            logger.exception("Сбой при инкрементировании счетчика пиров")
            raise WireguardError from e

    async def _add_server_wg_config(self, conn: SSHClientConnection, user_id):
        try:
            await conn.run("", check=True)  # TODO Команда на добавление пира на сервер
        except (OSError, asyncssh.Error) as e:
            logger.exception("Сбой при добавлении пира в конфигурацию сервера")
            raise WireguardError from e

    async def _ban_server_wg_config(self, conn: SSHClientConnection, user_id):
        try:
            await conn.run("", check=True)  # TODO Команда на бан пира на сервере
        except (OSError, asyncssh.Error) as e:
            logger.exception("Сбой бана пира на сервере")
            raise WireguardError from e

    async def _recover_server_wg_config(self, conn: SSHClientConnection, user_id):
        try:
            await conn.run("", check=True)  # TODO Команда на разбан пира на сервере
        except (OSError, asyncssh.Error) as e:
            logger.exception("Сбой разбана пира на сервере")
            raise WireguardError from e

    def _create_db_wg_model(self, user_id, cfg_name):
        self.user_config = dict(
            user_id=user_id,
            name=cfg_name,
            user_private_key=self.private_key,
            address=f"10.0.0.{self.countpeers}/32",
            dns="9.9.9.9",
            server_public_key=self.public_key,
            allowed_ips="0.0.0.0/0",
            endpoint_ip=settings.WG_IP,
            endpoint_port=settings.WG_PORT,
        )
        return self.user_config

    @validate_call
    async def move_user(
        self, user_id: int, move: Literal["add", "ban", "unban"], cfg_name: str = None
    ):
        async with asyncssh.connect(
            settings.WG_IP,
            username=settings.WG_USERNAME,
            client_keys=settings.WG_KEY.get_secret_value(),
        ) as conn:
            await self._create_keys(conn)
            await self._increment_counter(conn)

            match move:
                case "add":
                    # self._add_server_wg_config(conn, user_id)
                    return self._create_db_wg_model(user_id, cfg_name)
                case "ban":
                    pass  # self._ban_server_wg_config(conn, user_id)
                case "unban":
                    pass  # self._recover_server_wg_config(conn, user_id)


if __name__ == "__main__":
    wg = WgConfigMaker()

    asyncio.run(wg.move_user(user_id=6987832296, move="add"))
