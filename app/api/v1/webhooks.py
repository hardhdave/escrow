from fastapi import APIRouter

router = APIRouter()


@router.post("/stripe")
def stripe_webhook() -> dict[str, str]:
    return {"status": "received"}


@router.post("/razorpay")
def razorpay_webhook() -> dict[str, str]:
    return {"status": "received"}
