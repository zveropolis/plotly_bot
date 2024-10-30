import os

from sqlalchemy import DDL, event

from core.config import Base
from core.path import PATH

sql_path = os.path.join(PATH, "src", "db", "sql")

with open(os.path.join(sql_path, "_update_user_status.sql")) as sql:
    update_user_status = DDL(sql.read())
with open(os.path.join(sql_path, "trigger_update_user_status.sql")) as sql:
    trigger_update_user_status = DDL(sql.read())
with open(os.path.join(sql_path, "_succesful_pay.sql")) as sql:
    succesful_pay = DDL(sql.read())
with open(os.path.join(sql_path, "trigger_succesful_pay.sql")) as sql:
    trigger_succesful_pay = DDL(sql.read())
with open(os.path.join(sql_path, "_unfreeze_configs.sql")) as sql:
    unfreeze_configs = DDL(sql.read())
with open(os.path.join(sql_path, "_delete_old_transactions.sql")) as sql:
    delete_old_transactions = DDL(sql.read())
with open(os.path.join(sql_path, "trigger_old_transactions.sql")) as sql:
    trigger_old_transactions = DDL(sql.read())

event.listen(Base.metadata, "after_create", update_user_status)
event.listen(Base.metadata, "after_create", trigger_update_user_status)
event.listen(Base.metadata, "after_create", succesful_pay)
event.listen(Base.metadata, "after_create", trigger_succesful_pay)
event.listen(Base.metadata, "after_create", unfreeze_configs)
event.listen(Base.metadata, "after_create", delete_old_transactions)
event.listen(Base.metadata, "after_create", trigger_old_transactions)
