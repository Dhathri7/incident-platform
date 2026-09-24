from typing import Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AuditLog


class AuditService:
    """Service for audit logging operations."""
    
    @staticmethod
    async def log_action(
        session: AsyncSession,
        user_id: int,
        action: str,
        resource: str,
        resource_id: Optional[int] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> AuditLog:
        """Log a user action for audit trail."""
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            details=details or {},
        )
        session.add(audit_log)
        await session.commit()
        await session.refresh(audit_log)
        return audit_log
    
    @staticmethod
    async def get_audit_logs(
        session: AsyncSession,
        user_id: Optional[int] = None,
        resource: Optional[str] = None,
        action: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[AuditLog], int]:
        """Get audit logs with optional filtering."""
        query = select(AuditLog)
        
        # Apply filters
        if user_id is not None:
            query = query.where(AuditLog.user_id == user_id)
        if resource:
            query = query.where(AuditLog.resource == resource)
        if action:
            query = query.where(AuditLog.action == action)
        
        # Get total count
        count_stmt = select(count_expression()).select_from(AuditLog)
        if user_id is not None:
            count_stmt = count_stmt.where(AuditLog.user_id == user_id)
        if resource:
            count_stmt = count_stmt.where(AuditLog.resource == resource)
        if action:
            count_stmt = count_stmt.where(AuditLog.action == action)
        
        count_result = await session.execute(count_stmt)
        total = count_result.scalar()
        
        # Get paginated results, sorted by most recent first
        query = query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit)
        result = await session.execute(query)
        logs = result.scalars().all()
        
        return logs, total
    
    @staticmethod
    async def get_user_action_history(
        session: AsyncSession,
        user_id: int,
        limit: int = 50,
    ) -> list[AuditLog]:
        """Get recent action history for a specific user."""
        stmt = (
            select(AuditLog)
            .where(AuditLog.user_id == user_id)
            .order_by(AuditLog.timestamp.desc())
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def get_resource_history(
        session: AsyncSession,
        resource: str,
        resource_id: int,
        limit: int = 50,
    ) -> list[AuditLog]:
        """Get change history for a specific resource."""
        stmt = (
            select(AuditLog)
            .where(
                (AuditLog.resource == resource) & (AuditLog.resource_id == resource_id)
            )
            .order_by(AuditLog.timestamp.desc())
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()


def count_expression():
    """Helper to get count expression."""
    from sqlalchemy import func
    return func.count()