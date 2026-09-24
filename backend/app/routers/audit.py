from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from app.core import get_db
from app.schemas.audit import AuditLogResponse
from app.services.audit_service import AuditService
from app.routers.auth import get_current_user_id

router = APIRouter(tags=["Audit"])


class AuditLogListResponse(BaseModel):
    """Audit log list response."""
    total: int
    logs: list[AuditLogResponse]


@router.get(
    "",
    response_model=AuditLogListResponse,
    summary="List audit logs",
    responses={
        200: {"description": "Audit logs retrieved successfully"},
    },
)
async def list_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[int] = Query(None),
    resource: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    current_user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
) -> AuditLogListResponse:
    """
    List audit logs with optional filtering and pagination.
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Number of records to return (default: 100, max: 1000)
    - **user_id**: Filter by user ID (optional)
    - **resource**: Filter by resource type (user, incident, etc.) (optional)
    - **action**: Filter by action (USER_LOGIN, INCIDENT_CREATED, etc.) (optional)
    """
    try:
        logs, total = await AuditService.get_audit_logs(
            session=session,
            user_id=user_id,
            resource=resource,
            action=action,
            skip=skip,
            limit=limit,
        )
        
        return AuditLogListResponse(
            total=total,
            logs=[AuditLogResponse.model_validate(log) for log in logs],
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve audit logs",
        )


@router.get(
    "/user/{user_id}/history",
    response_model=list[AuditLogResponse],
    summary="Get user action history",
    responses={
        200: {"description": "User history retrieved successfully"},
    },
)
async def get_user_history(
    user_id: int,
    limit: int = Query(50, ge=1, le=500),
    current_user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
) -> list[AuditLogResponse]:
    """
    Get action history for a specific user.
    
    - **user_id**: The user ID to get history for
    - **limit**: Maximum number of records to return (default: 50, max: 500)
    """
    try:
        logs = await AuditService.get_user_action_history(
            session=session,
            user_id=user_id,
            limit=limit,
        )
        
        return [AuditLogResponse.model_validate(log) for log in logs]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user history",
        )


@router.get(
    "/resource/{resource}/{resource_id}/changes",
    response_model=list[AuditLogResponse],
    summary="Get resource change history",
    responses={
        200: {"description": "Resource history retrieved successfully"},
    },
)
async def get_resource_changes(
    resource: str,
    resource_id: int,
    limit: int = Query(50, ge=1, le=500),
    current_user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
) -> list[AuditLogResponse]:
    """
    Get change history for a specific resource (e.g., incident).
    
    - **resource**: Resource type (incident, user, etc.)
    - **resource_id**: The ID of the resource
    - **limit**: Maximum number of records to return (default: 50, max: 500)
    """
    try:
        logs = await AuditService.get_resource_history(
            session=session,
            resource=resource,
            resource_id=resource_id,
            limit=limit,
        )
        
        return [AuditLogResponse.model_validate(log) for log in logs]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve resource history",
        )