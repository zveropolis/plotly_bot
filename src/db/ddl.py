import os

from sqlalchemy import DDL, event

from core.config import Base
from core.path import PATH

with open(os.path.join(PATH, "sql", "update_user_activity.sql")) as sql:
    update_user_activity = DDL(sql.read())
with open(os.path.join(PATH, "sql", "user_activity_trigger.sql")) as sql:
    user_activity_trigger = DDL(sql.read())

event.listen(Base.metadata, "after_create", update_user_activity)
event.listen(Base.metadata, "after_create", user_activity_trigger)
