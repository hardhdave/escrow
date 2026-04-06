from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_token, get_db
from app.domain.identity.schemas import TokenPayload
from app.domain.wallet.schemas import WalletSummaryResponse
from app.domain.wallet.service import WalletService

router = APIRouter()


@router.get("/me", response_model=WalletSummaryResponse)
def get_my_wallet(
    token: TokenPayload = Depends(get_current_token),
    db: Session = Depends(get_db),
) -> WalletSummaryResponse:
    return WalletService(db).get_wallet_summary(token.sub)
