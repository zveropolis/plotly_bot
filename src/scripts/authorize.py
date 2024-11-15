import os
import sys

from yoomoney import Authorize

sys.path.insert(1, os.path.dirname(sys.path[0]))


from core.config import AuthorizeVar, settings

if __name__ == "__main__":
    auth_v = AuthorizeVar()

    Authorize(
        client_id=auth_v.client_id.get_secret_value(),
        client_secret=auth_v.client_secret.get_secret_value(),
        redirect_uri=settings.BOT_URL,
        scope=[
            "account-info",
            "operation-history",
            "operation-details",
            "incoming-transfers",
            # "payment-p2p",
            # "payment-shop",
        ],
    )
