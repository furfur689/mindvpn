from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB

from .base import Base, TimestampMixin

class RoutingPolicy(Base, TimestampMixin):
    __tablename__ = "routing_policies"
    
    org_id = Column(Integer, ForeignKey("orgs.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    rules = Column(JSONB, nullable=False, default=dict)
