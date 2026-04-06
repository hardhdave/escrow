from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.domain.common import TimestampMixin, generate_id


class ContractMessage(Base, TimestampMixin):
    __tablename__ = "contract_messages"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: generate_id("msg"))
    contract_id: Mapped[str] = mapped_column(ForeignKey("contracts.id"), index=True)
    sender_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    message_type: Mapped[str] = mapped_column(String(32), default="user")
    body: Mapped[str] = mapped_column(Text())


class ActivityEvent(Base, TimestampMixin):
    __tablename__ = "activity_events"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: generate_id("evt"))
    contract_id: Mapped[str] = mapped_column(ForeignKey("contracts.id"), index=True)
    actor_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    summary: Mapped[str] = mapped_column(Text())


class ContractReadState(Base):
    __tablename__ = "contract_read_states"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: generate_id("read"))
    contract_id: Mapped[str] = mapped_column(ForeignKey("contracts.id"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
