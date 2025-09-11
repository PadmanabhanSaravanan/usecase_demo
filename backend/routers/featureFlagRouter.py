from fastapi import APIRouter, HTTPException
from typing import Dict
import json
import os

router = APIRouter(prefix="/feature-flags", tags=["feature-flags"])

FEATURE_FLAG_PATH = os.path.join(os.path.dirname(__file__), "..", "feature-flags.json")

@router.get("/")
def get_flags() -> Dict:
    try:
        with open(FEATURE_FLAG_PATH, "r") as f:
            return json.load(f)
    except Exception:
        raise HTTPException(status_code=500, detail="Could not read feature flags")

@router.post("/")
def update_flags(flags: Dict):
    try:
        with open(FEATURE_FLAG_PATH, "w") as f:
            json.dump(flags, f)
        return {"status": "updated", "flags": flags}
    except Exception:
        raise HTTPException(status_code=500, detail="Could not update feature flags")
