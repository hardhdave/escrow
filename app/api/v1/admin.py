from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_token
from app.domain.identity.schemas import TokenPayload

router = APIRouter()


@router.get("/ping")
def admin_ping(token: TokenPayload = Depends(get_current_token)) -> dict[str, str]:
    if token.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return {"status": "admin-ok"}
