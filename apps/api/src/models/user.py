from sqlalchemy import Column, String, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from .base import Base, TimestampMixin

class UserRole(str, enum.Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    SUPPORT = "SUPPORT"
    READONLY = "READONLY"

class UserStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"

class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    org_id = Column(Integer, ForeignKey("orgs.id"), nullable=False, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.READONLY)
    status = Column(Enum(UserStatus), nullable=False, default=UserStatus.ACTIVE)
    
    # Relationships
    org = relationship("Org", back_populates="users")
    clients = relationship("Client", back_populates="user")
