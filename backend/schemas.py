from pydantic import BaseModel


class ServiceCreate(BaseModel):
    name: str
    description: str | None = None
    environment: str = "development"


class ServiceResponse(ServiceCreate):
    id: int
    status: str