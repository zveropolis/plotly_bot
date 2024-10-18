import asyncio
import logging
import logging.config

import asyncssh
from asyncssh import SSHClientConnection

from core.config import settings

logger = logging.getLogger("asyncssh")


class WgConnection:
    connection: SSHClientConnection

    async def connect(self):
        await asyncio.wait([self.__create_connection()])

        self.connection.set_keepalive(interval=120)

    async def __create_connection(self):
        self.connection = await asyncssh.connect(
            settings.WG_HOST,
            username=settings.WG_USER,
            client_keys=settings.WG_KEY.get_secret_value(),
        )
