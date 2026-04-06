from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.domain.common import TimestampMixin, generate_id


class PaymentIntent(Base, TimestampMixin):
    __tablename__ = "payment_intents"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: generate_id("pay"))
    milestone_id: Mapped[str] = mapped_column(ForeignKey("milestones.id"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    provider: Mapped[str] = mapped_column(String(32), default="manual")
    provider_reference: Mapped[str | None] = mapped_column(String(128), nullable=True)
    amount: Mapped[float] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(8), default="USD")
    status: Mapped[str] = mapped_column(String(32), default="processing")
    idempotency_key: Mapped[str] = mapped_column(String(128), unique=True)
