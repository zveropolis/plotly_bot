#!/usr/bin/python3

import argparse
import fcntl
import functools
import logging
import pathlib
import sys
from ipaddress import IPv4Interface
from subprocess import Popen
from time import time

logger = logging.getLogger()


WIREGUARD_CONF = "/etc/wireguard/wg1.conf"
# WIREGUARD_CONF = "C:\\code\\vpn_dan_bot\\src\\wg\\wg1.conf"
WIREGUARD_LOG = "/home/zadira/Scripts/ErrorsPyWG"


class ConfigChanger:
    def __init__(self, public_key, allowed_ips=None, raises=False) -> None:
        self.public_key = public_key
        self.allowed_ips = allowed_ips
        self.raises = raises

    def __find_key(self):
        lines = []
        for i, line in enumerate(self.config):
            if self.public_key in line:
                lines.append(i)

        if not len(lines):
            raise Exception("PEER NOT FOUND")

        validated_lines = []
        for i in lines:
            assert "peer" in self.config[i - 1].lower()
            validated_lines.extend((i - 1, i))

            assert "allowedips" in self.config[i + 1].lower()
            validated_lines.append(i + 1)

            try:
                assert "endpoint" in self.config[i + 2].lower()
            except (AssertionError, IndexError):
                pass
            else:
                validated_lines.append(i + 2)

        for i in validated_lines:
            yield i

    def process(mode):
        def decorator(func):
            @functools.wraps(func)
            def conf_changer(self, *args, **kwargs):
                try:
                    start = time()

                    with open(WIREGUARD_CONF, "r+") as file:
                        fcntl.flock(file, fcntl.LOCK_EX)
                        self.config = file.read().split("\n")
                        func(self, *args, **kwargs)

                        file.seek(0)
                        file.truncate(0)
                        file.write("\n".join(self.config))
                        fcntl.flock(file, fcntl.LOCK_UN)

                    proc = time() - start

                    reload_cmd = " && ".join(
                        (
                            f'echo -n "$(date) :: {func.__name__} :: {self.public_key[:4]}... ::" >> {WIREGUARD_LOG}',
                            f"sudo systemctl reload wg-quick@wg1.service 2>> {WIREGUARD_LOG}",
                            f'echo " " >> {WIREGUARD_LOG}',
                        )
                    )

                    error_code = Popen(
                        f"flock {WIREGUARD_LOG} --command '{reload_cmd}'", shell=True
                    ).returncode
                    if not error_code:
                        logger.info(f'Peer "{self.public_key[:4]}..." {mode}ed')
                    else:
                        raise Exception(
                            f"execute wireguard reload error. Exit code {error_code}"
                        )

                except Exception as e:
                    logger.error(e.args[0])
                    if self.raises:
                        raise e
                else:
                    logger.debug(
                        f"METRIC::{func.__name__}::proc::[  {int(proc)*1000}  ]msec"
                    )
                finally:
                    logger.debug(
                        f"METRIC::{func.__name__}::end::[  {int((time()-start)*1000)}  ]msec"
                    )

            return conf_changer

        return decorator

    @process("add")
    def register(self):
        new_user = (
            "[Peer]",
            f"PublicKey = {self.public_key}",
            f"AllowedIPs = {self.allowed_ips}",
        )
        config = "\n".join(self.config)
        if self.public_key in config:
            logger.warning("Peer already added")
            raise Exception("NEW USER ERROR")

        self.config.extend(new_user)

    @process("delet")
    def delete(self):
        lines = self.__find_key()
        for n in sorted(lines, reverse=True):
            self.config.pop(n)

    @process("bann")
    def ban(self):
        lines = self.__find_key()
        for n in lines:
            if self.config[n].startswith("#"):
                logger.warning("Peer already banned")
                raise Exception("BAN USER ERROR")
            else:
                self.config[n] = f"# {self.config[n]}"

    @process("unbann")
    def unban(self):
        lines = self.__find_key()
        for n in lines:
            if not self.config[n].startswith("#"):
                logger.warning("Peer already unbanned")
                raise Exception("UNBAN USER ERROR")
            else:
                self.config[n] = self.config[n].strip("# ")


def create_parser():
    parser = argparse.ArgumentParser(
        prog="Python Wireguard Utils",
        description="Python tools for the wireguard server",
        epilog="Text at the bottom of help",
    )

    parser.add_argument("pubkey", type=str, help="Public key of new(old) user")
    parser.add_argument(
        "-ips", "--allowed_ips", type=IPv4Interface, help="AllowedIPs for new peer"
    )
    parser.add_argument(
        "-m",
        "--mode",
        choices=["new", "ban", "unban", "del"],
        default="new",
        help="Tool for change wireguard config (default 'new')",
    )
    parser.add_argument(
        "--wgpath",
        type=pathlib.Path,
        default=WIREGUARD_CONF,
        help=f"Path wireguard config file (default '{WIREGUARD_CONF}')",
    )
    parser.add_argument(
        "--raises",
        action="store_true",
        help="Interruption in case of an error",
    )
    return parser


def main():
    logger.info("Start")

    parser = create_parser()

    args = parser.parse_args()
    cc = ConfigChanger(
        public_key=args.pubkey, allowed_ips=args.allowed_ips, raises=args.raises
    )
    if args.mode == "new":
        if not args.allowed_ips:
            logger.error("Argument ALLOWED_IPS: empty value")
            sys.exit()
        cc.register()
    elif args.mode == "ban":
        cc.ban()
    elif args.mode == "unban":
        cc.unban()
    elif args.mode == "del":
        cc.delete()

    logger.info("End")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(levelname)-8s] %(funcName)s(%(lineno)d): %(message)s",
    )

    main()
