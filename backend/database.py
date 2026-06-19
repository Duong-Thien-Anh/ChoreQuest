from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from backend.config import settings

IS_SQLITE = settings.DATABASE_URL.startswith("sqlite")

if IS_SQLITE:
    connect_args = {"check_same_thread": False}
else:
    connect_args = {"ssl": "require"}

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def init_db():
    async with engine.begin() as conn:
        if IS_SQLITE:
            await conn.exec_driver_sql("PRAGMA journal_mode=WAL")

        from backend.models import (  # noqa: F401
            User, Chore, ChoreAssignment, ChoreCategory, ChoreRotation,
            ChoreExclusion, ChoreAssignmentRule, QuestTemplate,
            Reward, RewardRedemption, PointTransaction,
            Achievement, UserAchievement, WishlistItem, SeasonalEvent,
            Notification, SpinResult, ApiKey, AuditLog, AppSetting,
            InviteCode, RefreshToken, PushSubscription,
            AvatarItem, UserAvatarItem,
            Shoutout, VacationPeriod,
        )
        await conn.run_sync(Base.metadata.create_all)

        if IS_SQLITE:
            _migrations = [
                ("reward_redemptions", "fulfilled_by", "INTEGER REFERENCES users(id)"),
                ("reward_redemptions", "fulfilled_at", "DATETIME"),
                ("users", "streak_freezes_used", "INTEGER DEFAULT 0"),
                ("users", "streak_freeze_month", "INTEGER"),
                ("chore_assignments", "feedback", "TEXT"),
                ("rewards", "category", "VARCHAR(50)"),
                ("achievements", "tier", "VARCHAR(10)"),
                ("achievements", "group_key", "VARCHAR(50)"),
                ("achievements", "sort_order", "INTEGER DEFAULT 0"),
            ]
            for table, col, typedef in _migrations:
                try:
                    await conn.exec_driver_sql(
                        f"ALTER TABLE {table} ADD COLUMN {col} {typedef}"
                    )
                except Exception:
                    pass


async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()