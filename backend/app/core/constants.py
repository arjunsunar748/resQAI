"""
Core domain constants, enums, and RBAC definitions for RESQ AGENT.
"""
from enum import Enum
from typing import Dict, List, Set


class AdminLevel(str, Enum):
    """
    Administrative hierarchy levels, calibrated for Nepal's constitutional federal structure
    and adaptable to international emergency operations.
    """
    FEDERAL = "FEDERAL"              # Level 1: National (NEOC / MoHA / NDRRMA)
    PROVINCIAL = "PROVINCIAL"        # Level 2: Province 1-7 EOCs
    DISTRICT = "DISTRICT"            # Level 3: 77 District Emergency Operations Centers (DEOC)
    MUNICIPALITY = "MUNICIPALITY"    # Level 4: Metro, Sub-Metro, Palika / Gaunpalika
    WARD = "WARD"                    # Level 5: Ward level / CERT / Community responders


class UserRole(str, Enum):
    """System-wide operational roles with specific command and control scopes."""
    SUPER_ADMIN = "SUPER_ADMIN"
    ORG_ADMIN = "ORG_ADMIN"
    EMERGENCY_COORDINATOR = "EMERGENCY_COORDINATOR"
    INCIDENT_OFFICER = "INCIDENT_OFFICER"
    FIELD_RESPONDER = "FIELD_RESPONDER"
    MEDICAL_OFFICER = "MEDICAL_OFFICER"
    RESOURCE_MANAGER = "RESOURCE_MANAGER"
    ANALYST = "ANALYST"
    READ_ONLY_VIEWER = "READ_ONLY_VIEWER"


class Permission(str, Enum):
    """Granular permissions governing system capabilities and safety boundaries."""
    # Organization & User Management
    ORG_CREATE = "org:create"
    ORG_READ = "org:read"
    ORG_UPDATE = "org:update"
    ORG_DELETE = "org:delete"
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_ASSIGN_ROLE = "user:assign_role"

    # Incident Management
    INCIDENT_CREATE = "incident:create"
    INCIDENT_READ = "incident:read"
    INCIDENT_UPDATE = "incident:update"
    INCIDENT_DELETE = "incident:delete"
    INCIDENT_VERIFY = "incident:verify"
    INCIDENT_ESCALATE = "incident:escalate"
    INCIDENT_CLOSE = "incident:close"

    # Resource Management & Dispatch
    RESOURCE_CREATE = "resource:create"
    RESOURCE_READ = "resource:read"
    RESOURCE_UPDATE = "resource:update"
    RESOURCE_DELETE = "resource:delete"
    RESOURCE_DISPATCH = "resource:dispatch"
    RESOURCE_STATUS_UPDATE = "resource:status_update"

    # AI Recommendation Governance (Human-in-the-Loop)
    AI_RECOMMENDATION_VIEW = "ai:view_recommendation"
    AI_RECOMMENDATION_APPROVE = "ai:approve_recommendation"
    AI_RECOMMENDATION_MODIFY = "ai:modify_recommendation"
    AI_RECOMMENDATION_OVERRIDE = "ai:override_recommendation"
    AI_SIMULATION_RUN = "ai:run_simulation"

    # Audit & Compliance
    AUDIT_LOG_READ = "audit:read"
    AUDIT_LOG_EXPORT = "audit:export"

    # Analytics & Reports
    ANALYTICS_READ = "analytics:read"
    ANALYTICS_EXPORT = "analytics:export"


# Role-to-Permissions Mapping Table
ROLE_PERMISSIONS_MAP: Dict[UserRole, Set[Permission]] = {
    UserRole.SUPER_ADMIN: set(Permission),  # All permissions
    UserRole.ORG_ADMIN: {
        Permission.ORG_READ,
        Permission.ORG_UPDATE,
        Permission.USER_CREATE,
        Permission.USER_READ,
        Permission.USER_UPDATE,
        Permission.USER_ASSIGN_ROLE,
        Permission.INCIDENT_CREATE,
        Permission.INCIDENT_READ,
        Permission.INCIDENT_UPDATE,
        Permission.INCIDENT_VERIFY,
        Permission.RESOURCE_CREATE,
        Permission.RESOURCE_READ,
        Permission.RESOURCE_UPDATE,
        Permission.RESOURCE_DISPATCH,
        Permission.AI_RECOMMENDATION_VIEW,
        Permission.AI_RECOMMENDATION_APPROVE,
        Permission.AI_RECOMMENDATION_MODIFY,
        Permission.AI_RECOMMENDATION_OVERRIDE,
        Permission.AUDIT_LOG_READ,
        Permission.ANALYTICS_READ,
    },
    UserRole.EMERGENCY_COORDINATOR: {
        Permission.ORG_READ,
        Permission.USER_READ,
        Permission.INCIDENT_CREATE,
        Permission.INCIDENT_READ,
        Permission.INCIDENT_UPDATE,
        Permission.INCIDENT_VERIFY,
        Permission.INCIDENT_ESCALATE,
        Permission.INCIDENT_CLOSE,
        Permission.RESOURCE_READ,
        Permission.RESOURCE_DISPATCH,
        Permission.RESOURCE_STATUS_UPDATE,
        Permission.AI_RECOMMENDATION_VIEW,
        Permission.AI_RECOMMENDATION_APPROVE,
        Permission.AI_RECOMMENDATION_MODIFY,
        Permission.AI_RECOMMENDATION_OVERRIDE,
        Permission.AI_SIMULATION_RUN,
        Permission.AUDIT_LOG_READ,
        Permission.ANALYTICS_READ,
    },
    UserRole.INCIDENT_OFFICER: {
        Permission.ORG_READ,
        Permission.INCIDENT_CREATE,
        Permission.INCIDENT_READ,
        Permission.INCIDENT_UPDATE,
        Permission.INCIDENT_VERIFY,
        Permission.RESOURCE_READ,
        Permission.RESOURCE_DISPATCH,
        Permission.AI_RECOMMENDATION_VIEW,
        Permission.AUDIT_LOG_READ,
    },
    UserRole.FIELD_RESPONDER: {
        Permission.ORG_READ,
        Permission.INCIDENT_READ,
        Permission.INCIDENT_UPDATE,
        Permission.RESOURCE_READ,
        Permission.RESOURCE_STATUS_UPDATE,
        Permission.AI_RECOMMENDATION_VIEW,
    },
    UserRole.MEDICAL_OFFICER: {
        Permission.ORG_READ,
        Permission.INCIDENT_READ,
        Permission.INCIDENT_UPDATE,
        Permission.RESOURCE_READ,
        Permission.RESOURCE_DISPATCH,
        Permission.RESOURCE_STATUS_UPDATE,
        Permission.AI_RECOMMENDATION_VIEW,
        Permission.ANALYTICS_READ,
    },
    UserRole.RESOURCE_MANAGER: {
        Permission.ORG_READ,
        Permission.INCIDENT_READ,
        Permission.RESOURCE_CREATE,
        Permission.RESOURCE_READ,
        Permission.RESOURCE_UPDATE,
        Permission.RESOURCE_STATUS_UPDATE,
        Permission.AI_RECOMMENDATION_VIEW,
        Permission.ANALYTICS_READ,
    },
    UserRole.ANALYST: {
        Permission.ORG_READ,
        Permission.INCIDENT_READ,
        Permission.RESOURCE_READ,
        Permission.AI_RECOMMENDATION_VIEW,
        Permission.AUDIT_LOG_READ,
        Permission.ANALYTICS_READ,
        Permission.ANALYTICS_EXPORT,
    },
    UserRole.READ_ONLY_VIEWER: {
        Permission.ORG_READ,
        Permission.INCIDENT_READ,
        Permission.RESOURCE_READ,
        Permission.ANALYTICS_READ,
    },
}


class DisasterType(str, Enum):
    """Standard disaster classification types."""
    FLOOD = "FLOOD"
    LANDSLIDE = "LANDSLIDE"
    EARTHQUAKE = "EARTHQUAKE"
    FIRE = "FIRE"
    ROAD_ACCIDENT = "ROAD_ACCIDENT"
    STORM = "STORM"
    LIGHTNING = "LIGHTNING"
    AVALANCHE = "AVALANCHE"
    INDUSTRIAL_ACCIDENT = "INDUSTRIAL_ACCIDENT"
    OTHER = "OTHER"


class IncidentSeverity(str, Enum):
    """Disaster severity classification matrix."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IncidentStatus(str, Enum):
    """Strict state machine for incident progression."""
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    ASSIGNED = "ASSIGNED"
    EN_ROUTE = "EN_ROUTE"
    ARRIVED = "ARRIVED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CANCELLED = "CANCELLED"


class ResourceStatus(str, Enum):
    """Operational status for emergency equipment, ambulances, and teams."""
    AVAILABLE = "AVAILABLE"
    ASSIGNED = "ASSIGNED"
    EN_ROUTE = "EN_ROUTE"
    ON_SCENE = "ON_SCENE"
    MAINTENANCE = "MAINTENANCE"
    OFFLINE = "OFFLINE"


class AuditAction(str, Enum):
    """Actions captured in the immutable audit trail."""
    AUTH_LOGIN_SUCCESS = "AUTH_LOGIN_SUCCESS"
    AUTH_LOGIN_FAILED = "AUTH_LOGIN_FAILED"
    AUTH_LOGOUT = "AUTH_LOGOUT"
    AUTH_TOKEN_REFRESH = "AUTH_TOKEN_REFRESH"
    USER_CREATE = "USER_CREATE"
    USER_UPDATE = "USER_UPDATE"
    USER_ROLE_ASSIGN = "USER_ROLE_ASSIGN"
    ORG_CREATE = "ORG_CREATE"
    ORG_UPDATE = "ORG_UPDATE"
    INCIDENT_CREATE = "INCIDENT_CREATE"
    INCIDENT_UPDATE = "INCIDENT_UPDATE"
    INCIDENT_VERIFY = "INCIDENT_VERIFY"
    INCIDENT_STATUS_CHANGE = "INCIDENT_STATUS_CHANGE"
    RESOURCE_DISPATCH = "RESOURCE_DISPATCH"
    AI_RECOMMENDATION_GENERATE = "AI_RECOMMENDATION_GENERATE"
    AI_RECOMMENDATION_APPROVE = "AI_RECOMMENDATION_APPROVE"
    AI_RECOMMENDATION_OVERRIDE = "AI_RECOMMENDATION_OVERRIDE"
    SYSTEM_CONFIG_CHANGE = "SYSTEM_CONFIG_CHANGE"
