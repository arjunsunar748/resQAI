"""
Audit log schemas for compliance and activity tracing.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class AuditLogOut(BaseModel):
    id: int
    actor_id: Optional[int] = None
    organization_id: Optional[int] = None
    action: str
    entity_type: str
    entity_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    changes: Optional[str] = None
    checksum: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditLogFilter(BaseModel):
    actor_id: Optional[int] = None
    organization_id: Optional[int] = None
    action: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
