import os

from sqlalchemy import DDL, event

from core.config import Base
from core.path import PATH

with open(os.path.join(PATH, "src", "db", "sql", "_update_user_activity.sql")) as sql:
    update_user_activity = DDL(sql.read())
with open(
    os.path.join(PATH, "src", "db", "sql", "trigger_update_user_activity.sql")
) as sql:
    trigger_update_user_activity = DDL(sql.read())
with open(os.path.join(PATH, "src", "db", "sql", "_succesful_pay.sql")) as sql:
    succesful_pay = DDL(sql.read())
with open(os.path.join(PATH, "src", "db", "sql", "trigger_succesful_pay.sql")) as sql:
    trigger_succesful_pay = DDL(sql.read())

event.listen(Base.metadata, "after_create", update_user_activity)
event.listen(Base.metadata, "after_create", trigger_update_user_activity)
event.listen(Base.metadata, "after_create", succesful_pay)
event.listen(Base.metadata, "after_create", trigger_succesful_pay)
