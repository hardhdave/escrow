from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_token, get_db
from app.domain.identity.schemas import TokenPayload
from app.domain.payments.schemas import FundMilestoneRequest, PaymentIntentResponse
from app.domain.payments.service import PaymentService

router = APIRouter()


@router.post("/milestones/{milestone_id}/fund", response_model=PaymentIntentResponse, status_code=status.HTTP_202_ACCEPTED)
def fund_milestone(
    milestone_id: str,
    payload: FundMilestoneRequest,
    token: TokenPayload = Depends(get_current_token),
    db: Session = Depends(get_db),
) -> PaymentIntentResponse:
    return PaymentService(db).fund_milestone(milestone_id, payload, token)
