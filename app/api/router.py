from fastapi import APIRouter

from app.api.v1 import admin, auth, contracts, disputes, milestones, payments, rooms, wallets, webhooks

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(rooms.router, prefix="/rooms", tags=["rooms"])
api_router.include_router(contracts.router, prefix="/contracts", tags=["contracts"])
api_router.include_router(milestones.router, prefix="/milestones", tags=["milestones"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(wallets.router, prefix="/wallets", tags=["wallets"])
api_router.include_router(disputes.router, prefix="/disputes", tags=["disputes"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
