"""
Organization data model representing administrative and operational hierarchies.
"""
from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin, SoftDeleteMixin


class Organization(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(64), unique=True, nullable=False, index=True)
    admin_level = Column(String(32), nullable=False, index=True)  # FEDERAL, PROVINCIAL, etc.
    
    parent_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)
    province_id = Column(Integer, nullable=True)
    district_name = Column(String(100), nullable=True)
    municipality_name = Column(String(100), nullable=True)
    ward_number = Column(Integer, nullable=True)
    
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    boundary_geojson = Column(Text, nullable=True)
    
    is_active = Column(Boolean, default=True, nullable=False)

    # Hierarchical parent-child relationship
    parent = relationship("Organization", remote_side=[id], backref="children")
    users = relationship("User", back_populates="organization")
