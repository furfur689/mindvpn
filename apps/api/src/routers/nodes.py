from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from ..deps import get_db
from ..models import Node, NodeCapability
from ..models.node import NodeStatus
from ..schemas.node import NodeCreate, NodeResponse, NodeHeartbeat, NodeRegister
from ..services.node_registry import NodeRegistryService

router = APIRouter()

@router.post("/register", response_model=NodeRegister)
async def register_node(
    node_data: NodeCreate,
    db: Session = Depends(get_db)
):
    """Регистрирует новый узел."""
    service = NodeRegistryService(db)
    return await service.register_node(node_data)

@router.post("/{node_id}/heartbeat")
async def node_heartbeat(
    node_id: int,
    heartbeat: NodeHeartbeat,
    db: Session = Depends(get_db)
):
    """Обновляет heartbeat от узла."""
    service = NodeRegistryService(db)
    return await service.update_heartbeat(node_id, heartbeat)

@router.get("/", response_model=List[NodeResponse])
async def list_nodes(
    region: Optional[str] = Query(None),
    provider: Optional[str] = Query(None),
    status: Optional[NodeStatus] = Query(None),
    labels: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Список узлов с фильтрацией."""
    service = NodeRegistryService(db)
    return await service.list_nodes(region, provider, status, labels)

@router.get("/{node_id}", response_model=NodeResponse)
async def get_node(
    node_id: int,
    db: Session = Depends(get_db)
):
    """Получает информацию об узле."""
    service = NodeRegistryService(db)
    node = await service.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node

@router.post("/{node_id}/drain")
async def drain_node(
    node_id: int,
    enabled: bool = True,
    db: Session = Depends(get_db)
):
    """Включает/выключает режим drain для узла."""
    service = NodeRegistryService(db)
    return await service.drain_node(node_id, enabled)
