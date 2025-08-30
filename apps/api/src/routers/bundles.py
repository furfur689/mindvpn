from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..deps import get_db
from ..models import User
from ..schemas.bundle import BundleResponse
from ..services.bundles import BundleService

router = APIRouter()

@router.get("/{user_id}/bundle", response_model=BundleResponse)
async def get_user_bundle(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Генерирует bundle для пользователя."""
    service = BundleService(db)
    bundle = await service.generate_bundle(user_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="User not found or no inbounds available")
    return bundle
