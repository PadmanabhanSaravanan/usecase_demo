from fastapi import APIRouter
from starlette.responses import JSONResponse

router = APIRouter()

# dev-only toggle to simulate downtime
_is_healthy = True

@router.get("/")
def health():
    if _is_healthy:
        return JSONResponse({"status": "ok"}, status_code=200)
    return JSONResponse({"status": "down"}, status_code=503)

@router.post("/")
def toggle_health(down: bool = False):
    """
    DEV ONLY: Simulate health down/up.
    curl -X POST "http://localhost:8000/health?down=true"
    """
    global _is_healthy
    _is_healthy = not down
    return {"is_healthy": _is_healthy}