from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(nullable=False)
    access_token: Mapped[str] = mapped_column(nullable=False, unique=True)
    refresh_token: Mapped[str] = mapped_column(nullable=False, unique=True)
    token_expiry: Mapped[int] = mapped_column(nullable=False)


class AnilistUser(Base):
    __tablename__ = "anilist_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    access_token: Mapped[str] = mapped_column(nullable=False, unique=True)
    refresh_token: Mapped[str] = mapped_column(nullable=False, unique=True)
    token_expiry: Mapped[int] = mapped_column(nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
