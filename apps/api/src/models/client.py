from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin

class Client(Base, TimestampMixin):
    __tablename__ = "clients"
    
    org_id = Column(Integer, ForeignKey("orgs.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    device_name = Column(String(255), nullable=False)
    public_key = Column(String(255), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="clients")
