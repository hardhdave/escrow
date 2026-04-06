from app.core.db import Base, engine
from app.domain.collaboration.models import ActivityEvent, ContractMessage, ContractReadState
from app.domain.disputes.models import Dispute
from app.domain.escrow.models import EscrowAccount
from app.domain.identity.models import User
from app.domain.marketplace.models import Contract, Milestone
from app.domain.payments.models import PaymentIntent
from app.domain.rooms.models import Room, RoomActivity, RoomMessage, RoomPayment
from app.domain.wallet.models import Wallet


def initialize_database() -> None:
    _ = (
        User,
        Contract,
        Milestone,
        EscrowAccount,
        Wallet,
        PaymentIntent,
        Dispute,
        ContractMessage,
        ActivityEvent,
        ContractReadState,
        Room,
        RoomMessage,
        RoomActivity,
        RoomPayment,
    )
    Base.metadata.create_all(bind=engine)
