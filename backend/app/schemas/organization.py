"""
Organization schemas for administrative and disaster response authorities.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    code: str = Field(..., min_length=2, max_length=64, description="Unique identifier e.g. NEOC-FED, DEOC-KTM")
    admin_level: str = Field(..., description="FEDERAL | PROVINCIAL | DISTRICT | MUNICIPALITY | WARD")
    parent_id: Optional[int] = None
    province_id: Optional[int] = Field(None, ge=1, le=7)
    district_name: Optional[str] = Field(None, max_length=100)
    municipality_name: Optional[str] = Field(None, max_length=100)
    ward_number: Optional[int] = Field(None, ge=1, le=50)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=50)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    boundary_geojson: Optional[str] = None


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    parent_id: Optional[int] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=50)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    boundary_geojson: Optional[str] = None
    is_active: Optional[bool] = None


class OrganizationOut(OrganizationBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
