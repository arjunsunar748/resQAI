from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum

class UserRole(str, enum.Enum):
    CITIZEN = "CITIZEN"
    RESCUE_TEAM = "RESCUE_TEAM"
    ADMIN = "ADMIN"

class IncidentStatus(str, enum.Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    ASSIGNED = "ASSIGNED"
    EN_ROUTE = "EN_ROUTE"
    ARRIVED = "ARRIVED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"

class SeverityLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.CITIZEN)
    phone = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    incident_code = Column(String, unique=True, index=True) # jastai RSQ-1024
    emergency_type = Column(String, nullable=False) # Flood, Fire, etc.
    description = Column(Text, nullable=True)
    people_affected = Column(Integer, default=1)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    image_url = Column(String, nullable=True)
    
    # AI & Severity
    severity_score = Column(Integer, default=0) # 0 - 100
    severity_level = Column(SQLEnum(SeverityLevel), default=SeverityLevel.LOW)
    ai_summary = Column(Text, nullable=True)
    
    status = Column(SQLEnum(IncidentStatus), default=IncidentStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)

    citizen_id = Column(Integer, ForeignKey("users.id"))
    citizen = relationship("User", backref="incidents")

class RescueTeam(Base):
    __tablename__ = "rescue_teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    specialization = Column(String, nullable=False) # Flood Rescue, Fire, etc.
    current_location = Column(String, nullable=True)
    is_available = Column(Integer, default=1) # 1 = Available, 0 = Busy
    contact_info = Column(String, nullable=True)

class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    resource_type = Column(String, nullable=False) # Ambulance, Rescue Boat, etc.
    status = Column(String, default="AVAILABLE") # AVAILABLE, ASSIGNED, MAINTENANCE
    location = Column(String, nullable=True)