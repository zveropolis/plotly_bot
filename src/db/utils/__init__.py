from db.utils.admin import get_all_users, set_admin
# from db.utils.redis import CashManager
from db.utils.save import async_dump
from db.utils.transactions import confirm_success_pay, insert_transaction
from db.utils.user import (add_user, clear_cash, delete_user, get_user,
                           recover_user)
from db.utils.wg import add_wg_config, get_user_with_configs, get_wg_config
