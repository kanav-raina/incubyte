"""Meta endpoints: health checks and (later) reference data."""

from fastapi import APIRouter

router = APIRouter(tags=["meta"])


@router.get("/health")
def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok"}
