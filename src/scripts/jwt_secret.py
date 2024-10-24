import os
import secrets
import sys

from passlib.context import CryptContext

sys.path.insert(1, os.path.dirname(sys.path[0]))


from core.config import settings

JWT_SECRET = secrets.token_hex(32)  # Генерирует 64-символьный шестнадцатеричный ключ
print(f"{JWT_SECRET=}")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
password_hash = pwd_context.hash(settings.ADMIN_PASS.get_secret_value())
print(f"{password_hash=}")
