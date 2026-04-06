from urllib.parse import urlencode

import httpx
from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.domain.identity.schemas import TokenPayload
from app.domain.rooms.models import Room, RoomActivity, RoomMessage, RoomPayment, generate_room_code
from app.domain.rooms.schemas import (
    RoomActivityResponse,
    RoomCreateRequest,
    RoomJoinRequest,
    RoomListItem,
    RoomMessageRequest,
    RoomMessageResponse,
    RoomMoneyRequest,
    RoomRefundDecisionRequest,
    RoomResponse,
    StripeCheckoutRequest,
    StripeCheckoutResponse,
)


class RoomService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_room(self, payload: RoomCreateRequest, token: TokenPayload) -> RoomResponse:
        room = Room(title=payload.title, currency=payload.currency, room_code=self._new_room_code())
        if token.role == "client":
            room.client_id = token.sub
            room.status = "waiting_for_freelancer"
        elif token.role == "freelancer":
            room.freelancer_id = token.sub
            room.status = "waiting_for_client"
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only client or freelancer accounts can create rooms")

        self.db.add(room)
        self.db.flush()
        self._activity(room.id, "room_created", f"Room created. Share code {room.room_code} with the other party.", token.sub)
        self.db.commit()
        return self._build_room(room, token)

    def join_room(self, payload: RoomJoinRequest, token: TokenPayload) -> RoomResponse:
        room = self._room_by_code(payload.room_code)

        if token.role == "freelancer":
            if room.freelancer_id and room.freelancer_id != token.sub:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Room already connected to another freelancer")
            room.freelancer_id = token.sub
        elif token.role == "client":
            if room.client_id and room.client_id != token.sub:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Room already connected to another client")
            room.client_id = token.sub
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only client or freelancer accounts can join rooms")

        if room.client_id and room.freelancer_id:
            room.status = "active"
        elif room.client_id:
            room.status = "waiting_for_freelancer"
        else:
            room.status = "waiting_for_client"

        self._activity(room.id, "room_joined", f"{token.role.capitalize()} joined the room using the room code.", token.sub)
        self.db.commit()
        return self._build_room(room, token)

    def list_rooms(self, token: TokenPayload) -> list[RoomListItem]:
        rooms = self.db.scalars(
            select(Room).where(or_(Room.client_id == token.sub, Room.freelancer_id == token.sub)).order_by(Room.created_at.desc())
        ).all()
        return [
            RoomListItem(
                room_code=room.room_code,
                title=room.title,
                status=room.status,
                current_user_role=self._role_for_user(room, token.sub),
                counterparty_connected=bool(room.client_id and room.freelancer_id),
                hold_amount=float(room.hold_amount),
                released_amount=float(room.released_amount),
            )
            for room in rooms
        ]

    def get_room(self, room_code: str, token: TokenPayload) -> RoomResponse:
        room = self._participant_room(room_code, token.sub)
        return self._build_room(room, token)

    def post_message(self, room_code: str, payload: RoomMessageRequest, token: TokenPayload) -> RoomResponse:
        room = self._participant_room(room_code, token.sub)
        body = payload.body.strip()
        if not body:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Message body is required")
        self.db.add(RoomMessage(room_id=room.id, sender_id=token.sub, body=body))
        self._activity(room.id, "message_posted", "A new message was sent in the room.", token.sub)
        self.db.commit()
        return self._build_room(room, token)

    def create_stripe_checkout(self, room_code: str, payload: StripeCheckoutRequest, token: TokenPayload) -> StripeCheckoutResponse:
        room = self._participant_room(room_code, token.sub)
        if room.client_id != token.sub:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the client can fund hold through Stripe")
        if not room.client_id or not room.freelancer_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Both client and freelancer must be connected before funding")
        if not settings.stripe_secret_key:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Stripe is not configured")

        success_url = f"{settings.frontend_base_url}/rooms/{room.room_code}?" + urlencode({"session_id": "{CHECKOUT_SESSION_ID}"})
        cancel_url = f"{settings.frontend_base_url}/rooms/{room.room_code}"
        amount_cents = int(round(payload.amount * 100))

        response = httpx.post(
            "https://api.stripe.com/v1/checkout/sessions",
            auth=(settings.stripe_secret_key, ""),
            data={
                "mode": "payment",
                "success_url": success_url,
                "cancel_url": cancel_url,
                "line_items[0][price_data][currency]": room.currency.lower(),
                "line_items[0][price_data][unit_amount]": str(amount_cents),
                "line_items[0][price_data][product_data][name]": f"Escrow hold for {room.title}",
                "line_items[0][quantity]": "1",
                "metadata[room_code]": room.room_code,
                "metadata[payer_id]": token.sub,
                "metadata[amount]": f"{payload.amount:.2f}",
            },
            timeout=20.0,
        )
        if response.status_code >= 400:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Stripe checkout session creation failed")

        data = response.json()
        payment = RoomPayment(
            room_id=room.id,
            payer_id=token.sub,
            provider="stripe",
            provider_session_id=data["id"],
            amount=payload.amount,
            currency=room.currency,
            status="created",
        )
        self.db.add(payment)
        self.db.commit()
        return StripeCheckoutResponse(checkout_url=data["url"], provider_session_id=data["id"])

    def confirm_stripe_checkout(self, room_code: str, session_id: str, token: TokenPayload) -> RoomResponse:
        room = self._participant_room(room_code, token.sub)
        payment = self.db.scalar(select(RoomPayment).where(RoomPayment.provider_session_id == session_id, RoomPayment.room_id == room.id))
        if not payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stripe checkout session not found")
        if not settings.stripe_secret_key:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Stripe is not configured")

        response = httpx.get(
            f"https://api.stripe.com/v1/checkout/sessions/{session_id}",
            auth=(settings.stripe_secret_key, ""),
            timeout=20.0,
        )
        if response.status_code >= 400:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Unable to verify Stripe checkout session")

        data = response.json()
        if data.get("payment_status") != "paid":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Stripe payment is not completed")

        if payment.status != "paid":
            payment.status = "paid"
            room.hold_amount = float(room.hold_amount) + float(payment.amount)
            room.status = "active"
            room.refund_status = "none"
            room.refund_note = None
            self._activity(room.id, "money_held", f"Client funded {payment.amount:.2f} {room.currency} through Stripe and money is now on hold.", token.sub)
            self.db.commit()

        return self._build_room(room, token)

    def release_money(self, room_code: str, payload: RoomMoneyRequest, token: TokenPayload) -> RoomResponse:
        room = self._participant_room(room_code, token.sub)
        if room.client_id != token.sub:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the client can release money")
        if room.status == "disputed":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Room is disputed; release is blocked")
        remaining = float(room.hold_amount) - float(room.released_amount)
        if payload.amount > remaining:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Release amount exceeds money on hold")
        room.released_amount = float(room.released_amount) + payload.amount
        if float(room.released_amount) >= float(room.hold_amount) and float(room.hold_amount) > 0:
            room.status = "completed"
        self._activity(room.id, "money_released", f"Client released {payload.amount:.2f} {room.currency} to the freelancer.", token.sub)
        self.db.commit()
        return self._build_room(room, token)

    def request_refund(self, room_code: str, payload: RoomMoneyRequest, token: TokenPayload) -> RoomResponse:
        room = self._participant_room(room_code, token.sub)
        if room.client_id != token.sub:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the client can request a refund")
        remaining = float(room.hold_amount) - float(room.released_amount)
        if remaining <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No held money remains to refund")
        room.refund_status = "requested"
        room.refund_note = payload.note or "Client requested refund of unreleased held money."
        self._activity(room.id, "refund_requested", room.refund_note, token.sub)
        self.db.commit()
        return self._build_room(room, token)

    def decide_refund(self, room_code: str, payload: RoomRefundDecisionRequest, token: TokenPayload) -> RoomResponse:
        room = self._participant_room(room_code, token.sub)
        if room.freelancer_id != token.sub:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the freelancer can approve or reject refund")
        if room.refund_status != "requested":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="There is no pending refund request")

        remaining = float(room.hold_amount) - float(room.released_amount)
        if payload.approve:
            room.hold_amount = float(room.released_amount)
            room.refund_status = "approved"
            room.refund_note = payload.note or "Freelancer approved refund of unreleased money."
            room.status = "refunded"
            self._activity(room.id, "refund_approved", room.refund_note, token.sub)
        else:
            room.refund_status = "rejected"
            room.refund_note = payload.note or "Freelancer rejected refund because service is claimed as delivered."
            room.status = "disputed"
            self._activity(
                room.id,
                "deadlock_dispute",
                f"Refund request rejected. Held amount {remaining:.2f} is now frozen until admin dispute resolution.",
                token.sub,
            )
        self.db.commit()
        return self._build_room(room, token)

    def open_dispute(self, room_code: str, token: TokenPayload, note: str | None = None) -> RoomResponse:
        room = self._participant_room(room_code, token.sub)
        room.status = "disputed"
        self._activity(room.id, "dispute_opened", note or "A dispute was opened. Held money stays frozen until admin review.", token.sub)
        self.db.commit()
        return self._build_room(room, token)


    def _new_room_code(self) -> str:
        for _ in range(10):
            code = generate_room_code()
            existing = self.db.scalar(select(Room).where(Room.room_code == code))
            if not existing:
                return code
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to generate a unique room code")

    def _room_by_code(self, room_code: str) -> Room:
        room = self.db.scalar(select(Room).where(Room.room_code == room_code.upper()))
        if not room:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
        return room

    def _participant_room(self, room_code: str, user_id: str) -> Room:
        room = self._room_by_code(room_code)
        if user_id not in {room.client_id, room.freelancer_id}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to access this room")
        return room

    def _role_for_user(self, room: Room, user_id: str) -> str:
        if room.client_id == user_id:
            return "client"
        if room.freelancer_id == user_id:
            return "freelancer"
        return "guest"

    def _activity(self, room_id: str, event_type: str, summary: str, actor_id: str | None = None) -> None:
        self.db.add(RoomActivity(room_id=room_id, actor_id=actor_id, event_type=event_type, summary=summary))

    def _build_room(self, room: Room, token: TokenPayload) -> RoomResponse:
        messages = self.db.scalars(select(RoomMessage).where(RoomMessage.room_id == room.id).order_by(RoomMessage.created_at.asc())).all()
        activities = self.db.scalars(select(RoomActivity).where(RoomActivity.room_id == room.id).order_by(RoomActivity.created_at.desc())).all()
        return RoomResponse(
            room_code=room.room_code,
            title=room.title,
            status=room.status,
            currency=room.currency,
            client_id=room.client_id,
            freelancer_id=room.freelancer_id,
            current_user_role=self._role_for_user(room, token.sub),
            hold_amount=float(room.hold_amount),
            released_amount=float(room.released_amount),
            remaining_hold_amount=float(room.hold_amount) - float(room.released_amount),
            refund_status=room.refund_status,
            refund_note=room.refund_note,
            messages=[
                RoomMessageResponse(id=item.id, sender_id=item.sender_id, body=item.body, created_at=item.created_at)
                for item in messages
            ],
            activities=[
                RoomActivityResponse(id=item.id, event_type=item.event_type, summary=item.summary, created_at=item.created_at)
                for item in activities
            ],
        )
