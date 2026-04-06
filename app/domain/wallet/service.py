from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.wallet.models import Wallet
from app.domain.wallet.schemas import WalletSummaryResponse


class WalletService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_wallet_summary(self, user_id: str) -> WalletSummaryResponse:
        wallet = self.db.scalar(select(Wallet).where(Wallet.user_id == user_id))
        if not wallet:
            wallet = Wallet(user_id=user_id)
            self.db.add(wallet)
            self.db.commit()
            self.db.refresh(wallet)

        return WalletSummaryResponse(
            currency=wallet.currency,
            available_balance=float(wallet.available_balance),
            pending_balance=float(wallet.pending_balance),
            reserve_balance=float(wallet.reserve_balance),
        )
