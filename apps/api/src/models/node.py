from sqlalchemy import Column, String, Integer, ForeignKey, Enum, JSON, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
import enum

from .base import Base, TimestampMixin

class NodeStatus(str, enum.Enum):
    NEW = "NEW"
    READY = "READY"
    DEGRADED = "DEGRADED"
    DOWN = "DOWN"

class Node(Base, TimestampMixin):
    __tablename__ = "nodes"
    
    # Basic info
    name = Column(String(255), nullable=False, index=True)
    hostname = Column(String(255), nullable=False, unique=True)
    ipv4 = Column(String(45), nullable=True)  # IPv4 or IPv6
    ipv6 = Column(String(45), nullable=True)
    
    # Organization
    org_id = Column(Integer, ForeignKey("orgs.id"), nullable=False, index=True)
    
    # Location and provider
    region = Column(String(100), nullable=True, index=True)
    provider = Column(String(100), nullable=True, index=True)
    
    # Labels for filtering and grouping
    labels = Column(JSONB, nullable=False, default=dict)
    
    # Status and health
    status = Column(Enum(NodeStatus), nullable=False, default=NodeStatus.NEW, index=True)
    last_heartbeat_at = Column(DateTime(timezone=True), nullable=True)
    
    # Agent info
    agent_version = Column(String(50), nullable=True)
    agent_cert_cn = Column(String(255), nullable=True)
    
    # Relationships
    org = relationship("Org", back_populates="nodes")
    capabilities = relationship("NodeCapability", back_populates="node", cascade="all, delete-orphan")
    inbounds = relationship("Inbound", back_populates="node", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="node", cascade="all, delete-orphan")
    traffic_samples = relationship("TrafficSample", back_populates="node", cascade="all, delete-orphan")

class NodeCapability(Base, TimestampMixin):
    __tablename__ = "node_capabilities"
    
    node_id = Column(Integer, ForeignKey("nodes.id"), nullable=False, index=True)
    protocol = Column(String(50), nullable=False)  # XRAY, SINGBOX, WG
    version = Column(String(50), nullable=False)
    features = Column(JSONB, nullable=False, default=dict)
    
    # Relationships
    node = relationship("Node", back_populates="capabilities")
