from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Incident, IncidentSeverity, IncidentStatus
from app.schemas.incidents import (
    IncidentCreate,
    IncidentUpdate,
    IncidentResponse,
)


class IncidentService:
    """Service for incident management operations."""
    
    @staticmethod
    async def create_incident(
        session: AsyncSession,
        incident_data: IncidentCreate,
        created_by_id: int,
    ) -> Incident:
        """Create a new incident."""
        incident = Incident(
            title=incident_data.title,
            description=incident_data.description,
            severity=IncidentSeverity(incident_data.severity),
            status=IncidentStatus.OPEN,
            created_by=created_by_id,
        )
        session.add(incident)
        await session.commit()
        await session.refresh(incident)
        return incident
    
    @staticmethod
    async def get_incident_by_id(
        session: AsyncSession,
        incident_id: int,
    ) -> Incident | None:
        """Get incident by ID."""
        stmt = select(Incident).where(Incident.id == incident_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def list_incidents(
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
        severity: str | None = None,
    ) -> tuple[list[Incident], int]:
        """List incidents with optional filtering."""
        query = select(Incident)
        
        # Apply filters
        if status:
            query = query.where(Incident.status == IncidentStatus(status))
        if severity:
            query = query.where(Incident.severity == IncidentSeverity(severity))
        
        # Get total count
        count_stmt = select(func.count()).select_from(Incident)
        if status:
            count_stmt = count_stmt.where(Incident.status == IncidentStatus(status))
        if severity:
            count_stmt = count_stmt.where(Incident.severity == IncidentSeverity(severity))
        
        count_result = await session.execute(count_stmt)
        total = count_result.scalar()
        
        # Get paginated results
        query = query.order_by(Incident.created_at.desc()).offset(skip).limit(limit)
        result = await session.execute(query)
        incidents = result.scalars().all()
        
        return incidents, total
    
    @staticmethod
    async def update_incident(
        session: AsyncSession,
        incident: Incident,
        update_data: IncidentUpdate,
    ) -> Incident:
        """Update an incident."""
        if update_data.title is not None:
            incident.title = update_data.title
        if update_data.description is not None:
            incident.description = update_data.description
        if update_data.severity is not None:
            incident.severity = IncidentSeverity(update_data.severity)
        if update_data.status is not None:
            incident.status = IncidentStatus(update_data.status)
        
        await session.commit()
        await session.refresh(incident)
        return incident
    
    @staticmethod
    async def delete_incident(
        session: AsyncSession,
        incident: Incident,
    ) -> None:
        """Delete an incident."""
        await session.delete(incident)
        await session.commit()
    
    @staticmethod
    async def get_incident_statistics(
        session: AsyncSession,
    ) -> dict:
        """Get incident statistics."""
        # Total incidents
        total_stmt = select(func.count()).select_from(Incident)
        total_result = await session.execute(total_stmt)
        total = total_result.scalar()
        
        # By status
        for status in IncidentStatus:
            stmt = select(func.count()).select_from(Incident).where(
                Incident.status == status
            )
            result = await session.execute(stmt)
            count = result.scalar()
            # This will be returned in the response
        
        # By severity
        critical_stmt = select(func.count()).select_from(Incident).where(
            Incident.severity == IncidentSeverity.CRITICAL
        )
        critical_result = await session.execute(critical_stmt)
        critical_count = critical_result.scalar()
        
        high_stmt = select(func.count()).select_from(Incident).where(
            Incident.severity == IncidentSeverity.HIGH
        )
        high_result = await session.execute(high_stmt)
        high_count = high_result.scalar()
        
        return {
            "total_incidents": total,
            "critical_count": critical_count,
            "high_count": high_count,
        }