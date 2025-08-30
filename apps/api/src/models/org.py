from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin

class Org(Base, TimestampMixin):
    __tablename__ = "orgs"
    
    slug = Column(String(100), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    
    # Relationships
    nodes = relationship("Node", back_populates="org")
    users = relationship("User", back_populates="org")
    tasks = relationship("Task", back_populates="org")
