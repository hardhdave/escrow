from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_token, get_db
from app.domain.collaboration.schemas import (
    ContractListItem,
    ContractRoomResponse,
    ContractStateRequest,
    MessageCreateRequest,
    MessageResponse,
)
from app.domain.collaboration.service import CollaborationService
from app.domain.identity.schemas import TokenPayload
from app.domain.marketplace.schemas import ContractCreateRequest, ContractResponse
from app.domain.marketplace.service import ContractService

router = APIRouter()


@router.get("/mine", response_model=list[ContractListItem])
def list_my_contracts(
    token: TokenPayload = Depends(get_current_token),
    db: Session = Depends(get_db),
) -> list[ContractListItem]:
    return CollaborationService(db).list_contracts(token)


@router.post("", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
def create_contract(
    payload: ContractCreateRequest,
    token: TokenPayload = Depends(get_current_token),
    db: Session = Depends(get_db),
) -> ContractResponse:
    return ContractService(db).create_contract(payload, token)


@router.get("/{contract_id}", response_model=ContractRoomResponse)
def get_contract_room(
    contract_id: str,
    token: TokenPayload = Depends(get_current_token),
    db: Session = Depends(get_db),
) -> ContractRoomResponse:
    return CollaborationService(db).get_contract_room(contract_id, token)


@router.post("/{contract_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def post_contract_message(
    contract_id: str,
    payload: MessageCreateRequest,
    token: TokenPayload = Depends(get_current_token),
    db: Session = Depends(get_db),
) -> MessageResponse:
    return CollaborationService(db).post_message(contract_id, payload, token)


@router.post("/{contract_id}/pause", response_model=ContractRoomResponse)
def pause_contract(
    contract_id: str,
    payload: ContractStateRequest,
    token: TokenPayload = Depends(get_current_token),
    db: Session = Depends(get_db),
) -> ContractRoomResponse:
    return CollaborationService(db).pause_contract(contract_id, payload, token)


@router.post("/{contract_id}/resume", response_model=ContractRoomResponse)
def resume_contract(
    contract_id: str,
    payload: ContractStateRequest,
    token: TokenPayload = Depends(get_current_token),
    db: Session = Depends(get_db),
) -> ContractRoomResponse:
    return CollaborationService(db).resume_contract(contract_id, payload, token)
