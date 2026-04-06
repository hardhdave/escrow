from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.domain.common import TimestampMixin, generate_id


class Contract(Base, TimestampMixin):
    __tablename__ = "contracts"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: generate_id("ctr"))
    client_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    freelancer_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    currency: Mapped[str] = mapped_column(String(8), default="USD")
    status: Mapped[str] = mapped_column(String(32), default="draft")

    milestones: Mapped[list["Milestone"]] = relationship(back_populates="contract", cascade="all, delete-orphan")


class Milestone(Base, TimestampMixin):
    __tablename__ = "milestones"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: generate_id("ms"))
    contract_id: Mapped[str] = mapped_column(ForeignKey("contracts.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    sequence_no: Mapped[int] = mapped_column(Integer)
    amount: Mapped[float] = mapped_column(Numeric(12, 2))
    status: Mapped[str] = mapped_column(String(32), default="pending_funding")
    funded_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    released_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)

    contract: Mapped[Contract] = relationship(back_populates="milestones")
