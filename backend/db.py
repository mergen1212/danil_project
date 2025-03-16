from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from sqlalchemy.ext.declarative import declarative_base
import os
from models import UserReqst
from sys import exit


from dotenv import load_dotenv


# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение значения переменной DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    print(f"ENV {None}")
    exit(1)
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    full_name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column()
    hashed_password: Mapped[str] = mapped_column()
    disabled: Mapped[bool] = mapped_column(default=False)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_db():
    async with AsyncSessionLocal() as db:
        yield db


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def create_test_user(db: AsyncSession, user: UserReqst):
    test_user = User(
        username=user.username,
        full_name=user.full_name,
        email=user.email,
        hashed_password=user.hashed_password,
        disabled=user.disabled,
    )
    db.add(test_user)
    await db.commit()
    return {"OK": 200}
