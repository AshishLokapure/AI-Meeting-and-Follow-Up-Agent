from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter()


@router.get("")
def health_check() -> dict[str, str]:
    now = datetime.now(timezone.utc).isoformat()
    return {"status": "ok", "timestamp": now}
