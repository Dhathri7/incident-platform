from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class IncidentCreate(BaseModel):
    """Incident creation request schema."""
    title: str = Field(..., min_length=5, max_length=255)
    description: str = Field(..., min_length=10)
    severity: str = Field(default="medium", pattern="^(low|medium|high|critical)$")


class IncidentUpdate(BaseModel):
    """Incident update request schema."""
    title: Optional[str] = Field(None, min_length=5, max_length=255)
    description: Optional[str] = Field(None, min_length=10)
    severity: Optional[str] = Field(None, pattern="^(low|medium|high|critical)$")
    status: Optional[str] = Field(None, pattern="^(open|investigating|resolved)$")


class IncidentResponse(BaseModel):
    """Incident response schema."""
    id: int
    title: str
    description: str
    severity: str
    status: str
    created_by: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class IncidentListResponse(BaseModel):
    """Incident list response with pagination."""
    total: int
    incidents: list[IncidentResponse]