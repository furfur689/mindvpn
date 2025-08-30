from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from ..deps import get_db
from ..services.metrics import MetricsService

router = APIRouter()

@router.get("/prometheus")
async def prometheus_metrics():
    """Возвращает метрики в формате Prometheus."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

@router.get("/dashboard")
async def dashboard_metrics(db: Session = Depends(get_db)):
    """Возвращает метрики для дашборда."""
    service = MetricsService(db)
    return await service.get_dashboard_metrics()
