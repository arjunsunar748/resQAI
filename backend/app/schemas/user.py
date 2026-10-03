"""
User, Role, and Permission schemas.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PermissionOut(BaseModel):
    id: int
    code: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class RoleOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    permissions: List[PermissionOut] = []

    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=50)
    full_name: str = Field(..., min_length=2, max_length=255)
    preferred_locale: str = Field(default="en", max_length=10)
    organization_id: Optional[int] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Strong password (min 8 chars)")
    roles: List[str] = Field(default_factory=list, description="List of role names to assign")


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    preferred_locale: Optional[str] = Field(None, max_length=10)
    organization_id: Optional[int] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class UserRoleAssignRequest(BaseModel):
    role_names: List[str] = Field(..., min_length=1, description="Assigned roles list")


class UserOut(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    last_login_at: Optional[datetime] = None
    created_at: datetime
    roles: List[RoleOut] = []
    permissions: List[str] = []

    model_config = ConfigDict(from_attributes=True)
