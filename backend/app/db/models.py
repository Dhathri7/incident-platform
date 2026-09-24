from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
import enum

from app.core import Base


class UserRole(str, enum.Enum):
    """User role enumeration."""
    ADMIN = "admin"
    ENGINEER = "engineer"


class IncidentSeverity(str, enum.Enum):
    """Incident severity enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(str, enum.Enum):
    """Incident status enumeration."""
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"


class User(Base):
    """User model for authentication and audit tracking."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(
        Enum(UserRole),
        default=UserRole.ENGINEER,
        nullable=False,
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    is_active = Column(type_=type(True), default=True, nullable=False)
    
    # Relationships
    incidents = relationship("Incident", back_populates="created_by_user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username}>"


class Incident(Base):
    """Incident model for IT issue tracking."""
    __tablename__ = "incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    severity = Column(
        Enum(IncidentSeverity),
        default=IncidentSeverity.MEDIUM,
        nullable=False,
        index=True,
    )
    status = Column(
        Enum(IncidentStatus),
        default=IncidentStatus.OPEN,
        nullable=False,
        index=True,
    )
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    
    # Relationships
    created_by_user = relationship("User", back_populates="incidents")
    ai_analyses = relationship("AIAnalysis", back_populates="incident", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Incident id={self.id} title={self.title} status={self.status}>"


class AIAnalysis(Base):
    """AI analysis model for storing RAG-generated diagnoses and recommendations."""
    __tablename__ = "ai_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False, index=True)
    diagnosis = Column(Text, nullable=False)
    recommendations = Column(Text, nullable=False)
    metadata = Column(JSON, nullable=True, default={})
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    
    # Relationships
    incident = relationship("Incident", back_populates="ai_analyses")
    
    def __repr__(self) -> str:
        return f"<AIAnalysis id={self.id} incident_id={self.incident_id}>"


class AuditLog(Base):
    """Audit log model for tracking user actions."""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String(100), nullable=False)
    resource = Column(String(255), nullable=False)
    resource_id = Column(Integer, nullable=True)
    details = Column(JSON, nullable=True, default={})
    timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self) -> str:
        return f"<AuditLog id={self.id} action={self.action} resource={self.resource}>"