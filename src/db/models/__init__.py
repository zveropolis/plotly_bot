from core.config import Base
from db import ddl as _  # NOTE TRIGGERS
from db.models.enums import FreezeSteps, ReportStatus, UserActivity
from db.models.news import News
from db.models.reports import Reports
from db.models.transactions import Transactions
from db.models.userdata import UserData
from db.models.wg_config import WgConfig
from db.models.yoomoney import (YoomoneyOperation, YoomoneyOperationDetails,
                                yoomoney_site_display)

TABLES_SCHEMA = {
    UserData.__tablename__: UserData,
    Transactions.__tablename__: Transactions,
    WgConfig.__tablename__: WgConfig,
    Reports.__tablename__: Reports,
    YoomoneyOperation.__tablename__: YoomoneyOperation,
    News.__tablename__: News,
}
