from sqlalchemy.ext.asyncio import create_async_engine

from core.config import settings

async_engine = create_async_engine(
    url=settings.DATABASE_URL,
    echo=True,  # Логирование всех выполняемых операций
    pool_size=5,  # Максимальное количество подключений к базе
    max_overflow=10,  # Количество дополнительных подключений при переполнении
)
