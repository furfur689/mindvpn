from sqlalchemy import Column, String, Integer, ForeignKey, Enum, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
import enum

from .base import Base, TimestampMixin

class InboundStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPLIED = "APPLIED"
    ERROR = "ERROR"

class Inbound(Base, TimestampMixin):
    __tablename__ = "inbounds"
    
    org_id = Column(Integer, ForeignKey("orgs.id"), nullable=False, index=True)
    node_id = Column(Integer, ForeignKey("nodes.id"), nullable=False, index=True)
    protocol = Column(String(50), nullable=False)  # XRAY, SINGBOX
    port = Column(Integer, nullable=False)
    settings = Column(JSONB, nullable=False, default=dict)
    status = Column(Enum(InboundStatus), nullable=False, default=InboundStatus.PENDING, index=True)
    last_applied_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    node = relationship("Node", back_populates="inbounds")
