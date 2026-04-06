from pydantic import BaseModel


class WalletSummaryResponse(BaseModel):
    currency: str
    available_balance: float
    pending_balance: float
    reserve_balance: float
