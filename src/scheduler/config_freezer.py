import logging

from core.exceptions import DatabaseError, WireguardError
from db.models import FreezeSteps
from db.utils import freeze_config, get_all_wg_configs
from wg.utils import WgConfigMaker

logger = logging.getLogger("apscheduler")
logging.getLogger("apscheduler.executors.default").setLevel(logging.WARNING)


async def check_freeze_configs():
    try:
        configs = await get_all_wg_configs()

        wait_no_cfg = [cfg for cfg in configs if cfg.freeze == FreezeSteps.wait_no]
        for config in wait_no_cfg:
            await WgConfigMaker().move_user(
                move="unban", user_pubkey=config.server_public_key
            )
        if wait_no_cfg:
            await freeze_config(wait_no_cfg, freeze=FreezeSteps.no)

        wait_yes_cfg = [cfg for cfg in configs if cfg.freeze == FreezeSteps.wait_yes]
        for config in wait_yes_cfg:
            await WgConfigMaker().move_user(
                move="ban", user_pubkey=config.server_public_key
            )
        if wait_yes_cfg:
            await freeze_config(wait_yes_cfg, freeze=FreezeSteps.yes)

    except DatabaseError:
        logger.exception("Ошибка связи с БД при заморозке конфигураций")
    except WireguardError:
        logger.exception("Ошибка связи с wireguard сервером при заморозке конфигураций")
    else:
        if wait_no_cfg:
            logger.info(
                "Разморожены конфигурации",
                extra={"configs.ids": [config.id for config in wait_no_cfg]},
            )
        if wait_yes_cfg:
            logger.info(
                "Заморожены конфигурации",
                extra={"configs.ids": [config.id for config in wait_yes_cfg]},
            )
