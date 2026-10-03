"""
Tamper-evident audit logging service.
"""
from datetime import datetime, timezone
import json
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.audit import AuditLog
from app.core.security import compute_audit_checksum
from app.core.logging import logger


class AuditService:
    @staticmethod
    def _format_timestamp_for_checksum(dt: datetime) -> str:
        """
        Normalize datetime to integer unix timestamp string to guarantee
        database-independent, timezone-invariant HMAC verification.
        """
        return str(int(dt.timestamp()))

    @classmethod
    def create_audit_log(
        cls,
        db: Session,
        action: str,
        entity_type: str,
        actor_id: Optional[int] = None,
        organization_id: Optional[int] = None,
        entity_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        changes: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        """
        Record an immutable audit log entry signed with HMAC-SHA256.
        """
        now = datetime.now(timezone.utc)
        ts_str = cls._format_timestamp_for_checksum(now)
        action_str = action.value if hasattr(action, "value") else str(action)
        entity_type_str = entity_type.value if hasattr(entity_type, "value") else str(entity_type)
        
        changes_json = json.dumps(changes, sort_keys=True) if changes else "{}"
        checksum = compute_audit_checksum(
            actor_id=str(actor_id) if actor_id else "",
            action=action_str,
            entity_type=entity_type_str,
            entity_id=str(entity_id) if entity_id else "",
            timestamp_iso=ts_str,
            details_str=changes_json,
        )

        audit_entry = AuditLog(
            actor_id=actor_id,
            organization_id=organization_id,
            action=action_str,
            entity_type=entity_type_str,
            entity_id=str(entity_id) if entity_id else None,
            ip_address=ip_address,
            user_agent=user_agent,
            changes=changes_json,
            checksum=checksum,
            created_at=now,
        )
        db.add(audit_entry)
        db.commit()
        db.refresh(audit_entry)
        logger.info(f"Audit log recorded: {action} on {entity_type}:{entity_id} by actor {actor_id}")
        return audit_entry

    @classmethod
    def verify_integrity(cls, log: AuditLog) -> bool:
        """
        Verify that an audit entry has not been altered in the database.
        """
        ts_str = cls._format_timestamp_for_checksum(log.created_at)
        computed = compute_audit_checksum(
            actor_id=str(log.actor_id) if log.actor_id else "",
            action=log.action,
            entity_type=log.entity_type,
            entity_id=str(log.entity_id) if log.entity_id else "",
            timestamp_iso=ts_str,
            details_str=log.changes or "{}",
        )
        return computed == log.checksum

    @staticmethod
    def get_logs(
        db: Session,
        organization_id: Optional[int] = None,
        actor_id: Optional[int] = None,
        action: Optional[str] = None,
        entity_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[AuditLog], int]:
        """
        Retrieve paginated audit logs filtered by organization and parameters.
        """
        query = db.query(AuditLog)
        if organization_id:
            query = query.filter(AuditLog.organization_id == organization_id)
        if actor_id:
            query = query.filter(AuditLog.actor_id == actor_id)
        if action:
            query = query.filter(AuditLog.action == action)
        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)

        total = query.count()
        items = (
            query.order_by(desc(AuditLog.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total


audit_service = AuditService()
