import secrets

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.domain.common import TimestampMixin, generate_id


def generate_room_code() -> str:
    return secrets.token_hex(3).upper()


class Room(Base, TimestampMixin):
    __tablename__ = "rooms"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: generate_id("room"))
    room_code: Mapped[str] = mapped_column(String(16), unique=True, index=True, default=generate_room_code)
    title: Mapped[str] = mapped_column(String(255))
    client_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    freelancer_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    currency: Mapped[str] = mapped_column(String(8), default="USD")
    status: Mapped[str] = mapped_column(String(32), default="waiting_for_counterparty")
    hold_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    released_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    refund_status: Mapped[str] = mapped_column(String(32), default="none")
    refund_note: Mapped[str | None] = mapped_column(Text(), nullable=True)


class RoomMessage(Base, TimestampMixin):
    __tablename__ = "room_messages"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: generate_id("rmsg"))
    room_id: Mapped[str] = mapped_column(ForeignKey("rooms.id"), index=True)
    sender_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    body: Mapped[str] = mapped_column(Text())


class RoomActivity(Base, TimestampMixin):
    __tablename__ = "room_activities"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: generate_id("ract"))
    room_id: Mapped[str] = mapped_column(ForeignKey("rooms.id"), index=True)
    actor_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    summary: Mapped[str] = mapped_column(Text())


class RoomPayment(Base, TimestampMixin):
    __tablename__ = "room_payments"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: generate_id("rpay"))
    room_id: Mapped[str] = mapped_column(ForeignKey("rooms.id"), index=True)
    payer_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    provider: Mapped[str] = mapped_column(String(32), default="stripe")
    provider_session_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    amount: Mapped[float] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(8), default="USD")
    status: Mapped[str] = mapped_column(String(32), default="created")
