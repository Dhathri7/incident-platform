from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any


class AIAnalysisCreate(BaseModel):
    """AI analysis creation request schema."""
    incident_id: int


class AIAnalysisResponse(BaseModel):
    """AI analysis response schema."""
    id: int
    incident_id: int
    diagnosis: str
    recommendations: str
    metadata: Optional[dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True