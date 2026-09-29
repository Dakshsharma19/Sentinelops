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