import asyncio
import logging
import logging.config
import os
import sys
from multiprocessing import Pool
from random import choices, randint
from time import time

from pandas import DataFrame
from random_word import RandomWords
from sqlalchemy import insert

sys.path.insert(1, os.path.join("C:\\code\\vpn_dan_bot\\src"))


from core.metric import async_speed_metric
from db.database import execute_query
from db.models import UserActivity, UserData
from db.utils import get_user

logging.config.fileConfig("log.ini", disable_existing_loggers=True)
logger = logging.getLogger()
# logging.disable()

RETRIES = 6
USERS = [
    21961196079,
    5766455756,
    7876585680,
    1983024464,
    6249506746,
    3414363804,
    3951259021,
    3608093301,
    3509943539,
    7357936784,
    5658991188,
    5397942177,
    7283172964,
    1110228860,
    3303363220,
    1575600861,
    3974746514,
    8125904079,
    6884596657,
    4167325277,
    2966111339,
    6748508019,
    2075702833,
    7193617229,
    3708585489,
    7276976802,
    8332784380,
    3856297703,
    5080395829,
    5053532069,
    6557897454,
    6563153471,
    8013938111,
    7709157112,
    6202669037,
    1963564595,
    4171874395,
    8885901981,
    7556467243,
    6486021343,
    1200234746,
    8850792022,
    2884972347,
    7595057070,
    2383329976,
    8612906239,
    6100016623,
    4282016161,
    3783504993,
    3970942438,
    2405245024,
    3640403578,
    9947853312,
    1411285390,
    3884003723,
    6016978816,
    9606847866,
    2833999139,
    8875566758,
    2926119855,
    9284919021,
    5221560385,
    7182773556,
    2890348793,
    5774611281,
    1570057945,
    6964430609,
    2749331914,
    9380226016,
    5641764541,
    9793708072,
    7047840775,
    2913686193,
    7731601813,
    5897127562,
    8626440422,
    5354594007,
    6648948305,
    7809659540,
    6577431340,
    5127847616,
    2483958146,
    1963678649,
    9477622562,
    6004057998,
    6342225201,
    2681801322,
    4174374131,
    3674444097,
    9533776342,
    3722747655,
    1424125441,
    3358676198,
    3455099689,
    9345393082,
    8367555736,
    2631305504,
    5570519232,
    5937260153,
    2200572715,
]


async def main():
    start = time()

    for _ in range(RETRIES):
        coros = [get_user(user) for user in choices(USERS, k=60)]

        coros_gen = time() - start

        await asyncio.gather(*coros, return_exceptions=True)

    end = time() - start - coros_gen

    print(f"{coros_gen=}  end={int(end*1000)} msec")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
