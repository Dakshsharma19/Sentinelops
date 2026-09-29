from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Incident, Service
from schemas import (
    IncidentCreate,
    IncidentResponse,
    IncidentUpdate,
    ServiceCreate,
    ServiceResponse,
)

app = FastAPI()

Base.metadata.create_all(bind=engine)
print("Database tables created successfully.Hurrayy")


# -------------------------
# Health
# -------------------------

@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/db-health")
def database_health_check():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return {"database": result.scalar() == 1}


# -------------------------
# Services
# -------------------------

@app.post("/services", response_model=ServiceResponse)
def create_service(
    service: ServiceCreate,
    db: Session = Depends(get_db),
):
    new_service = Service(
        name=service.name,
        description=service.description,
        environment=service.environment,
    )

    db.add(new_service)
    db.commit()
    db.refresh(new_service)

    return new_service


@app.get("/services")
def get_services(
    db: Session = Depends(get_db),
):
    services = db.query(Service).all()
    return services


# -------------------------
# Incidents
# -------------------------

@app.post("/incidents", response_model=IncidentResponse)
def create_incident(
    incident: IncidentCreate,
    db: Session = Depends(get_db),
):
    service = db.get(Service, incident.service_id)

    if service is None:
        raise HTTPException(
            status_code=404,
            detail="Service not found",
        )

    new_incident = Incident(
        service_id=incident.service_id,
        title=incident.title,
        description=incident.description,
        severity=incident.severity,
    )

    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)

    return new_incident


@app.get("/incidents")
def get_incidents(
    db: Session = Depends(get_db),
):
    incidents = db.query(Incident).all()
    return incidents


@app.get("/incidents/{incident_id}")
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
):
    incident = db.get(Incident, incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return incident


@app.patch("/incidents/{incident_id}")
def update_incident(
    incident_id: int,
    update: IncidentUpdate,
    db: Session = Depends(get_db),
):
    incident = db.get(Incident, incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    incident.status = update.status

    if update.severity is not None:
        incident.severity = update.severity

    if update.status == "resolved":
        incident.resolved_at = datetime.utcnow()

    db.commit()
    db.refresh(incident)

    return incident