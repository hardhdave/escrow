from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.domain.common import TimestampMixin, generate_id


class EscrowAccount(Base, TimestampMixin):
    __tablename__ = "escrow_accounts"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: generate_id("esc"))
    milestone_id: Mapped[str] = mapped_column(ForeignKey("milestones.id"), unique=True, index=True)
    funded_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    released_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    refunded_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    status: Mapped[str] = mapped_column(String(32), default="pending")
