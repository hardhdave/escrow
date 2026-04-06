from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_token, get_db
from app.domain.identity.schemas import TokenPayload
from app.domain.rooms.schemas import (
    RoomCreateRequest,
    RoomJoinRequest,
    RoomListItem,
    RoomMessageRequest,
    RoomMoneyRequest,
    RoomRefundDecisionRequest,
    RoomResponse,
    StripeCheckoutRequest,
    StripeCheckoutResponse,
)
from app.domain.rooms.service import RoomService

router = APIRouter()


@router.get("", response_model=list[RoomListItem])
def list_rooms(token: TokenPayload = Depends(get_current_token), db: Session = Depends(get_db)) -> list[RoomListItem]:
    return RoomService(db).list_rooms(token)


@router.post("", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def create_room(
    payload: RoomCreateRequest,
    token: TokenPayload = Depends(get_current_token),
    db: Session = Depends(get_db),
) -> RoomResponse:
    return RoomService(db).create_room(payload, token)


@router.post("/join", response_model=RoomResponse)
def join_room(
    payload: RoomJoinRequest,
    token: TokenPayload = Depends(get_current_token),
    db: Session = Depends(get_db),
) -> RoomResponse:
    return RoomService(db).join_room(payload, token)


@router.get("/{room_code}", response_model=RoomResponse)
def get_room(
    room_code: str,
    token: TokenPayload = Depends(get_current_token),
    db: Session = Depends(get_db),
) -> RoomResponse:
    return RoomService(db).get_room(room_code, token)


@router.post("/{room_code}/messages", response_model=RoomResponse)
def post_message(
    room_code: str,
    payload: RoomMessageRequest,
    token: TokenPayload = Depends(get_current_token),
    db: Session = Depends(get_db),
) -> RoomResponse:
    return RoomService(db).post_message(room_code, payload, token)


@router.post("/{room_code}/stripe-checkout", response_model=StripeCheckoutResponse)
def create_stripe_checkout(
    room_code: str,
    payload: StripeCheckoutRequest,
    token: TokenPayload = Depends(get_current_token),
    db: Session = Depends(get_db),
) -> StripeCheckoutResponse:
    return RoomService(db).create_stripe_checkout(room_code, payload, token)


@router.post("/{room_code}/stripe-confirm", response_model=RoomResponse)
def confirm_stripe_checkout(
    room_code: str,
    session_id: str = Query(...),
    token: TokenPayload = Depends(get_current_token),
    db: Session = Depends(get_db),
) -> RoomResponse:
    return RoomService(db).confirm_stripe_checkout(room_code, session_id, token)


@router.post("/{room_code}/release", response_model=RoomResponse)
def release_money(
    room_code: str,
    payload: RoomMoneyRequest,
    token: TokenPayload = Depends(get_current_token),
    db: Session = Depends(get_db),
) -> RoomResponse:
    return RoomService(db).release_money(room_code, payload, token)


@router.post("/{room_code}/refund-request", response_model=RoomResponse)
def request_refund(
    room_code: str,
    payload: RoomMoneyRequest,
    token: TokenPayload = Depends(get_current_token),
    db: Session = Depends(get_db),
) -> RoomResponse:
    return RoomService(db).request_refund(room_code, payload, token)


@router.post("/{room_code}/refund-decision", response_model=RoomResponse)
def refund_decision(
    room_code: str,
    payload: RoomRefundDecisionRequest,
    token: TokenPayload = Depends(get_current_token),
    db: Session = Depends(get_db),
) -> RoomResponse:
    return RoomService(db).decide_refund(room_code, payload, token)


@router.post("/{room_code}/dispute", response_model=RoomResponse)
def open_dispute(
    room_code: str,
    payload: RoomMessageRequest,
    token: TokenPayload = Depends(get_current_token),
    db: Session = Depends(get_db),
) -> RoomResponse:
    return RoomService(db).open_dispute(room_code, token, payload.body)
