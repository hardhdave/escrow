from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_token, get_db
from app.domain.disputes.schemas import DisputeCreateRequest, DisputeResponse
from app.domain.disputes.service import DisputeService
from app.domain.identity.schemas import TokenPayload

router = APIRouter()


@router.post("/milestones/{milestone_id}", response_model=DisputeResponse, status_code=status.HTTP_201_CREATED)
def open_dispute(
    milestone_id: str,
    payload: DisputeCreateRequest,
    token: TokenPayload = Depends(get_current_token),
    db: Session = Depends(get_db),
) -> DisputeResponse:
    return DisputeService(db).open_dispute(milestone_id, payload, token)
