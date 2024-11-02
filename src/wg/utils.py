import asyncio
import logging
import logging.config
import os
import sys
from re import escape
from time import time
from typing import Literal

import asyncssh
from asyncssh import SSHClientConnection
from pydantic import validate_call

sys.path.insert(1, os.path.join("C:\\code\\vpn_dan_bot\\src"))

from core.config import settings
from core.exceptions import WireguardError
from core.metric import async_speed_metric
from wg.connect import WgConnection

logger = logging.getLogger("asyncssh")

SSH = WgConnection()


class WgConfigMaker:
    peer_counter = "~/Scripts/LastPeerAddress"

    def __init__(self) -> None:
        self.private_key: str = None
        self.public_key: str = None
        self.countpeers: int = None

    async def _create_peer(self, conn: SSHClientConnection):
        try:
            cmd = (
                "tmp_private_key=$(wg genkey)",
                "tmp_public_key=$(echo $tmp_private_key | wg pubkey)",
                "echo $tmp_private_key",
                "echo $tmp_public_key",
                # f'flock {self.peer_counter} --command \'printf "%d" "$(cat {self.peer_counter})"+1 > {self.peer_counter} && cat {self.peer_counter}\'',
                f"flock {self.peer_counter} --command '~/Scripts/IPgen.py --file={self.peer_counter} && cat {self.peer_counter}' ",
                f'tmp_allowed_ips="$(cat {self.peer_counter})/32"',
                f"echo {escape(settings.WG_PASS.get_secret_value())} | sudo -S ~/Scripts/pywg.py $tmp_public_key -ips=$tmp_allowed_ips --raises",
            )
            completed_proc = await conn.run("\n" + "\n".join(cmd), check=True)
            keys = completed_proc.stdout.strip("\n").split("\n")
            self.private_key, self.public_key, self.countpeers, *_ = keys
            logger.info(completed_proc.stderr)

        except (OSError, asyncssh.Error) as e:
            logger.exception(
                "Сбой при добавлении пира в конфигурацию сервера wireguard"
            )
            raise WireguardError from e

    async def _ban_peer(self, conn: SSHClientConnection, reverse=False):
        if reverse:
            ban = "unban"
        else:
            ban = "ban"

        try:
            cmd = f"echo {escape(settings.WG_PASS.get_secret_value())} | sudo -S ~/Scripts/pywg.py -m {ban} {self.public_key} --raises"
            completed_proc = await conn.run(f"\n{cmd}", check=True)
            logger.info(completed_proc.stderr)

        except (OSError, asyncssh.Error) as e:
            logger.exception(
                "Сбой при изменении пира в конфигурации сервера wireguard"
            )
            raise WireguardError from e

    def _create_db_wg_model(self, user_id):
        self.user_config = dict(
            user_id=user_id,
            user_private_key=self.private_key,
            address=f"{self.countpeers}/32",
            server_public_key=self.public_key,
        )
        return self.user_config

    async def _check_connection(self):
        conn = SSH.connection

        if conn.is_closed():
            await SSH.connect()
            conn = SSH.connection
            try:
                assert conn is SSH.connection
                assert not conn.is_closed()
            except AssertionError as e:
                raise WireguardError from e
        return conn

    @async_speed_metric
    @validate_call
    async def move_user(
        self,
        move: Literal["add", "ban", "unban"],
        user_id: int = None,
        user_pubkey: str = None,
    ):
        conn = await self._check_connection()

        match move:
            case "add":
                await self._create_peer(conn)
                usr_cfg = self._create_db_wg_model(user_id)
                logger.info(f"{usr_cfg['address']=}")
                return usr_cfg
            case "ban":
                self.public_key = user_pubkey
                await self._ban_peer(conn)
            case "unban":
                self.public_key = user_pubkey
                await self._ban_peer(conn, reverse=True)

    async def get_peer_list(self):
        conn = await self._check_connection()
        try:
            cmd = f"echo {escape(settings.WG_PASS.get_secret_value())} | sudo -S ~/Scripts/pywg.py -l --raises"
            completed_proc = await conn.run(f"\n{cmd}", check=True)
            peers = completed_proc.stdout.strip("\n").split("[Peer]")

            clean_peers = []
            for peer in peers:
                clean_peer = {
                    line[: line.find("=")].strip(" ").lower(): line[
                        line.find("=") + 1 :
                    ].strip(" ")
                    for line in peer.splitlines()
                    if "=" in line
                }

                if clean_peer:
                    if "ban" in peer.lower():
                        clean_peer["ban"] = True
                    else:
                        clean_peer["ban"] = False

                    clean_peers.append(clean_peer)

        except (OSError, asyncssh.Error) as e:
            logger.exception("Сбой при получении списка пиров wireguard")
            raise WireguardError from e
        else:
            logger.info(f"Got {len(clean_peers)} peer's")

            return clean_peers


async def test_100():
    wg = WgConfigMaker()
    start = time()

    await SSH.connect()

    coros = [wg.get_peer_list() for _ in range(1)]
    # coros = [wg.move_user(user_id=6987832296, move="add") for _ in range(15)]
    # coros = [
    #     wg.move_user(
    #         user_pubkey="CkMG0Cx+T4IQzpN8q7D02Nq15om8OGPDWEB1wlpkkjs=",
    #         move="unban",
    #         conn=conn,
    #     )
    #     for _ in range(1)
    # ]

    coros_gen = time() - start

    await asyncio.gather(*coros)

    end = time() - start - coros_gen

    print(f"{coros_gen=}  {end=}")


if __name__ == "__main__":
    logging.config.fileConfig("log.ini", disable_existing_loggers=False)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_100())
