from sqlalchemy import Column, String, Integer, ForeignKey, Enum, JSON, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
import enum

from .base import Base, TimestampMixin

class TaskStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"

class TaskAction(str, enum.Enum):
    APPLY_INBOUND = "APPLY_INBOUND"
    RELOAD_SERVICES = "RELOAD_SERVICES"
    ROTATE_CERTS = "ROTATE_CERTS"
    PING = "PING"
    SPEEDTEST = "SPEEDTEST"
    DRAIN_NODE = "DRAIN_NODE"

class TargetType(str, enum.Enum):
    NODE = "NODE"
    INBOUND = "INBOUND"

class Task(Base, TimestampMixin):
    __tablename__ = "tasks"
    
    # Task identification
    action = Column(Enum(TaskAction), nullable=False, index=True)
    target_type = Column(Enum(TargetType), nullable=False, index=True)
    target_id = Column(Integer, nullable=False, index=True)
    
    # Organization
    org_id = Column(Integer, ForeignKey("orgs.id"), nullable=False, index=True)
    
    # Node (for node-specific tasks)
    node_id = Column(Integer, ForeignKey("nodes.id"), nullable=True, index=True)
    
    # Status and execution
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.QUEUED, index=True)
    payload = Column(JSONB, nullable=False, default=dict)
    logs = Column(Text, nullable=True)
    
    # Timing
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Retry info
    retry_count = Column(Integer, nullable=False, default=0)
    max_retries = Column(Integer, nullable=False, default=3)
    
    # Relationships
    org = relationship("Org", back_populates="tasks")
    node = relationship("Node", back_populates="tasks")
