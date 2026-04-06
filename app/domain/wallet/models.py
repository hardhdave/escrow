from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.domain.common import TimestampMixin, generate_id


class Wallet(Base, TimestampMixin):
    __tablename__ = "wallets"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: generate_id("wal"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    currency: Mapped[str] = mapped_column(String(8), default="USD")
    available_balance: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    pending_balance: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    reserve_balance: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
