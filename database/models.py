from datetime import datetime

from sqlalchemy import String, DateTime, Boolean, ForeignKey, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now(), onupdate=datetime.now())


class Chat(Base):
    __tablename__ = "chat"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[str] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    allowed_members: Mapped[int] = mapped_column(Integer, default=200, nullable=False)
    arab_filter_flag: Mapped[Boolean] = mapped_column(Boolean, default=True, nullable=False)

    members: Mapped[list["Member"]] = relationship(
        back_populates="chats",
        secondary="chats_members"
    )


class Member(Base):
    __tablename__ = "member"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[str] = mapped_column(nullable=False)
    username: Mapped[str] = mapped_column(String(255))
    first_name: Mapped[str] = mapped_column(String(255))
    last_name: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(50))
    photo_flag: Mapped[Boolean] = mapped_column(Boolean)
    premium_flag: Mapped[Boolean] = mapped_column(Boolean)
    status: Mapped[str] = mapped_column(String(50), default="in", nullable=False)

    chats: Mapped[list["Chat"]] = relationship(
        back_populates="members",
        secondary="chats_members"
    )


class ChatsMembers(Base):
    __tablename__ = "chats_members"

    chat_id: Mapped[int] = mapped_column(ForeignKey("chat.id", ondelete="SET NULL"), primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("member.id", ondelete="SET NULL"), primary_key=True)
