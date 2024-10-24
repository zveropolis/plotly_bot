#!/usr/bin/python3

import argparse
from ipaddress import IPv4Address
from pathlib import Path

START_IP = "10.1.0.1"
FILE = Path("INCREMENTED_IP")


def ip_to_int(ip):
    """Преобразует IP-адрес в целое число."""
    octets = list(map(int, ip.split(".")))
    return (octets[0] << 24) + (octets[1] << 16) + (octets[2] << 8) + octets[3]


def int_to_ip(num):
    """Преобразует целое число обратно в IP-адрес."""
    return f"{(num >> 24) & 255}.{(num >> 16) & 255}.{(num >> 8) & 255}.{num & 255}"


def generate_ip_range(start_ip, end_ip):
    """Генерирует диапазон IP-адресов от start_ip до end_ip."""
    start = ip_to_int(start_ip)
    end = ip_to_int(end_ip)

    for ip in range(start, end + 1):
        yield int_to_ip(ip)


def increment_ip(filename: Path = FILE):
    filename = filename.expanduser()

    if not filename.exists():
        filename.touch()

    with open(filename, "r+") as file:
        _ip = file.read()
        if _ip:
            last_ip = ip_to_int(_ip)
        else:
            last_ip = ip_to_int(START_IP)

        last_ip += 1

        file.seek(0)
        file.truncate(0)

        file.write(int_to_ip(last_ip))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="IP generator",
        description="Util for increment and range ip address",
    )
    parser.add_argument("-f", "--file", type=Path, help="File with IP")
    parser.add_argument(
        "-r",
        "--range",
        action="extend",
        help="Генерирует диапазон IP-адресов, пример --range 10.1.0.1 10.1.1.1",
        nargs="*",
    )

    args = parser.parse_args()
    if args.range:
        try:
            start_ip, end_ip = args.range
            IPv4Address(start_ip)
            IPv4Address(end_ip)
        except Exception as e:
            print("BAD INPUT RANGE")
            print(f"{e.args[0]}\n")
            parser.print_help()
        else:
            if args.file:
                with open(args.file, "w") as file:
                    for ip in generate_ip_range(start_ip, end_ip):
                        file.write(f"{ip}\n")
            else:
                for ip in generate_ip_range(start_ip, end_ip):
                    print(ip)
    else:
        if args.file:
            increment_ip(filename=args.file)
        else:
            increment_ip()
