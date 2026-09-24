from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any


class AuditLogResponse(BaseModel):
    """Audit log response schema."""
    id: int
    user_id: int
    action: str
    resource: str
    resource_id: Optional[int] = None
    details: Optional[dict[str, Any]] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True