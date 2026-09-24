from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db
from app.schemas.incidents import (
    IncidentCreate,
    IncidentUpdate,
    IncidentResponse,
    IncidentListResponse,
)
from app.services.incident_service import IncidentService
from app.services.audit_service import AuditService
from app.routers.auth import get_current_user_id

router = APIRouter(tags=["Incidents"])


@router.post(
    "",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new incident",
    responses={
        201: {"description": "Incident created successfully"},
        422: {"description": "Invalid request body"},
    },
)
async def create_incident(
    incident_data: IncidentCreate,
    current_user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
) -> IncidentResponse:
    """
    Create a new IT incident.
    
    - **title**: Incident title (5-255 characters)
    - **description**: Detailed description (minimum 10 characters)
    - **severity**: One of: low, medium, high, critical
    
    Returns the created incident with ID.
    """
    try:
        # Create incident
        incident = await IncidentService.create_incident(
            session=session,
            incident_data=incident_data,
            created_by_id=current_user_id,
        )
        
        # Log action
        await AuditService.log_action(
            session=session,
            user_id=current_user_id,
            action="INCIDENT_CREATED",
            resource="incident",
            resource_id=incident.id,
            details={
                "title": incident.title,
                "severity": incident.severity.value,
                "status": incident.status.value,
            },
        )
        
        return IncidentResponse.model_validate(incident)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create incident",
        )


@router.get(
    "",
    response_model=IncidentListResponse,
    summary="List all incidents",
    responses={
        200: {"description": "Incidents retrieved successfully"},
    },
)
async def list_incidents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: str | None = Query(None, regex="^(open|investigating|resolved)$"),
    severity: str | None = Query(None, regex="^(low|medium|high|critical)$"),
    current_user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
) -> IncidentListResponse:
    """
    List all incidents with optional filtering and pagination.
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Number of records to return (default: 100, max: 1000)
    - **status**: Filter by status (open, investigating, resolved)
    - **severity**: Filter by severity (low, medium, high, critical)
    """
    try:
        incidents, total = await IncidentService.list_incidents(
            session=session,
            skip=skip,
            limit=limit,
            status=status,
            severity=severity,
        )
        
        return IncidentListResponse(
            total=total,
            incidents=[IncidentResponse.model_validate(i) for i in incidents],
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list incidents",
        )


@router.get(
    "/{incident_id}",
    response_model=IncidentResponse,
    summary="Get incident by ID",
    responses={
        200: {"description": "Incident retrieved successfully"},
        404: {"description": "Incident not found"},
    },
)
async def get_incident(
    incident_id: int,
    current_user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
) -> IncidentResponse:
    """
    Get a specific incident by ID.
    
    - **incident_id**: The ID of the incident to retrieve
    """
    incident = await IncidentService.get_incident_by_id(session, incident_id)
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with ID {incident_id} not found",
        )
    
    return IncidentResponse.model_validate(incident)


@router.patch(
    "/{incident_id}",
    response_model=IncidentResponse,
    summary="Update incident",
    responses={
        200: {"description": "Incident updated successfully"},
        404: {"description": "Incident not found"},
        422: {"description": "Invalid request body"},
    },
)
async def update_incident(
    incident_id: int,
    update_data: IncidentUpdate,
    current_user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
) -> IncidentResponse:
    """
    Update an existing incident.
    
    - **incident_id**: The ID of the incident to update
    - **title**: New title (optional, 5-255 characters)
    - **description**: New description (optional, minimum 10 characters)
    - **severity**: New severity (optional)
    - **status**: New status (optional)
    
    Only provided fields will be updated.
    """
    incident = await IncidentService.get_incident_by_id(session, incident_id)
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with ID {incident_id} not found",
        )
    
    try:
        # Store old values for audit
        old_values = {
            "title": incident.title,
            "severity": incident.severity.value,
            "status": incident.status.value,
        }
        
        # Update incident
        updated_incident = await IncidentService.update_incident(
            session=session,
            incident=incident,
            update_data=update_data,
        )
        
        # Log action
        await AuditService.log_action(
            session=session,
            user_id=current_user_id,
            action="INCIDENT_UPDATED",
            resource="incident",
            resource_id=incident_id,
            details={
                "old_values": old_values,
                "new_values": {
                    "title": updated_incident.title,
                    "severity": updated_incident.severity.value,
                    "status": updated_incident.status.value,
                },
            },
        )
        
        return IncidentResponse.model_validate(updated_incident)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update incident",
        )


@router.delete(
    "/{incident_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete incident",
    responses={
        204: {"description": "Incident deleted successfully"},
        404: {"description": "Incident not found"},
    },
)
async def delete_incident(
    incident_id: int,
    current_user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete an incident by ID.
    
    - **incident_id**: The ID of the incident to delete
    
    **Note**: This action cannot be undone. The incident and all related analyses will be deleted.
    """
    incident = await IncidentService.get_incident_by_id(session, incident_id)
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with ID {incident_id} not found",
        )
    
    try:
        # Log action before deletion
        await AuditService.log_action(
            session=session,
            user_id=current_user_id,
            action="INCIDENT_DELETED",
            resource="incident",
            resource_id=incident_id,
            details={
                "title": incident.title,
                "severity": incident.severity.value,
            },
        )
        
        # Delete incident
        await IncidentService.delete_incident(session, incident)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete incident",
        )


@router.get(
    "/stats/overview",
    summary="Get incident statistics",
    responses={
        200: {"description": "Statistics retrieved successfully"},
    },
)
async def get_incident_stats(
    current_user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get high-level incident statistics.
    
    Returns:
    - Total incidents
    - Critical incidents count
    - High severity incidents count
    """
    try:
        stats = await IncidentService.get_incident_statistics(session)
        return stats
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get statistics",
        )