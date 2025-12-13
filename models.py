from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

class Company(BaseModel):
    id: Optional[str] = None
    name: str
    EIN: str = Field(alias="EIN")
    startDate: str = Field(alias="startDate")
    stateIncorporated: str = Field(alias="stateIncorporated")
    contactPersonName: str = Field(alias="contactPersonName")
    contactPersonPhNumber: str = Field(alias="contactPersonPhNumber")
    address1: str
    address2: str
    city: str
    state: str
    zip: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True

class Task(BaseModel):
    id: Optional[str] = None
    companyId: str = Field(alias="companyId")
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True

class TaskTemplate(BaseModel):
    companyIds: list[str] = Field(alias="companyIds")
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True

class AssignData(BaseModel):
    companyIds: list[str] = Field(alias="companyIds")
    startDate: str = Field(alias="startDate")
    dueDate: str = Field(alias="dueDate")

    class Config:
        populate_by_name = True