from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any

from ..models import Node, Task, User, Inbound
from ..models.node import NodeStatus
from ..models.task import TaskStatus

class MetricsService:
    def __init__(self, db: Session):
        self.db = db

    async def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Возвращает метрики для дашборда."""
        
        # Статистика узлов
        nodes_total = self.db.query(Node).count()
        nodes_online = self.db.query(Node).filter(Node.status == NodeStatus.READY).count()
        nodes_offline = self.db.query(Node).filter(Node.status.in_([NodeStatus.DOWN, NodeStatus.DEGRADED])).count()
        
        # Статистика пользователей
        users_total = self.db.query(User).count()
        users_active = self.db.query(User).filter(User.status == "ACTIVE").count()
        
        # Статистика задач
        tasks_total = self.db.query(Task).count()
        tasks_running = self.db.query(Task).filter(Task.status == TaskStatus.RUNNING).count()
        tasks_completed = self.db.query(Task).filter(Task.status == TaskStatus.SUCCESS).count()
        tasks_failed = self.db.query(Task).filter(Task.status == TaskStatus.FAILED).count()
        
        # Статистика inbounds
        inbounds_total = self.db.query(Inbound).count()
        inbounds_active = self.db.query(Inbound).filter(Inbound.status == "APPLIED").count()
        
        return {
            "nodes": {
                "total": nodes_total,
                "online": nodes_online,
                "offline": nodes_offline
            },
            "users": {
                "total": users_total,
                "active": users_active
            },
            "tasks": {
                "total": tasks_total,
                "running": tasks_running,
                "completed": tasks_completed,
                "failed": tasks_failed
            },
            "inbounds": {
                "total": inbounds_total,
                "active": inbounds_active
            }
        }
