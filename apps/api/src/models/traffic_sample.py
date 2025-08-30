from sqlalchemy import Column, String, Integer, ForeignKey, Date, Float
from sqlalchemy.orm import relationship

from .base import Base

class TrafficSample(Base):
    __tablename__ = "traffic_samples"
    
    day = Column(Date, nullable=False, index=True)
    node_id = Column(Integer, ForeignKey("nodes.id"), nullable=False, index=True)
    users_online = Column(Integer, nullable=False, default=0)
    gb_in = Column(Float, nullable=False, default=0.0)
    gb_out = Column(Float, nullable=False, default=0.0)
    
    # Relationships
    node = relationship("Node", back_populates="traffic_samples")
