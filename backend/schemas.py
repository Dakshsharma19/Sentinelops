from datetime import datetime

from pydantic import BaseModel


class ServiceCreate(BaseModel):
    name: str
    description: str | None = None
    environment: str = "development"


class ServiceResponse(ServiceCreate):
    id: int
    status: str


class IncidentCreate(BaseModel):
    service_id: int
    title: str
    description: str | None = None
    severity: str = "medium"


class IncidentResponse(IncidentCreate):
    id: int
    status: str
    created_at: datetime
    resolved_at: datetime | None = None


class IncidentUpdate(BaseModel):
    status: str
    severity: str | None = None


class UserCreate(BaseModel):
    email: str
    full_name: str
    password: str


class UserResponse(BaseModel):



    id: int
    email: str
    full_name: str
    is_active: bool


class EventCreate(BaseModel):
    service_id: int
    event_type: str
    metric_name: str | None = None
    value: float | None = None
    severity: str = "info"
    message: str | None = None


class EventResponse(EventCreate):
    id: int
    created_at: datetime