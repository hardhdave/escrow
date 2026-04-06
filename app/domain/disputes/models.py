from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.domain.common import TimestampMixin, generate_id


class Dispute(Base, TimestampMixin):
    __tablename__ = "disputes"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: generate_id("dsp"))
    milestone_id: Mapped[str] = mapped_column(ForeignKey("milestones.id"), index=True)
    opened_by: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    reason_code: Mapped[str] = mapped_column(String(64))
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="open")
