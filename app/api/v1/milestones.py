from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_token, get_db
from app.domain.escrow.schemas import ApprovalRequest, DeliverySubmissionRequest, MilestoneResponse
from app.domain.escrow.service import EscrowService
from app.domain.identity.schemas import TokenPayload

router = APIRouter()


@router.post("/{milestone_id}/submit", response_model=MilestoneResponse)
def submit_delivery(
    milestone_id: str,
    payload: DeliverySubmissionRequest,
    token: TokenPayload = Depends(get_current_token),
    db: Session = Depends(get_db),
) -> MilestoneResponse:
    return EscrowService(db).submit_delivery(milestone_id, payload, token)


@router.post("/{milestone_id}/approve", response_model=MilestoneResponse)
def approve_milestone(
    milestone_id: str,
    payload: ApprovalRequest,
    token: TokenPayload = Depends(get_current_token),
    db: Session = Depends(get_db),
) -> MilestoneResponse:
    return EscrowService(db).approve_milestone(milestone_id, payload, token)
