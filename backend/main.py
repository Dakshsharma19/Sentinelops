from datetime import datetime

from detection import evaluate_event
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from database import Base, engine, get_db
from models import Event, Incident, Service , User
from schemas import (
    EventCreate,
    EventResponse,
    IncidentCreate,
    IncidentResponse,
    IncidentUpdate,
    ServiceCreate,
    ServiceResponse,
    UserCreate,
    UserResponse,
)
from auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)

app = FastAPI()

Base.metadata.create_all(bind=engine)
print("Database tables created successfully.Hurrayy!!!!!!")
#----------------------------------------------- EVENTS--------------------------------------------
@app.post("/events", response_model=EventResponse)
def create_event(
    event: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = db.get(Service, event.service_id)

    if service is None:
        raise HTTPException(
            status_code=404,
            detail="Service not found",
        )

    new_event = Event(
        service_id=event.service_id,
        event_type=event.event_type,
        metric_name=event.metric_name,
        value=event.value,
        severity=event.severity,
        message=event.message,
    )

    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    evaluate_event(
        new_event,
        db,
    )

    return new_event

@app.get("/events")
def get_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    events = (
        db.query(Event)
        .order_by(Event.created_at.desc())
        .all()
    )

    return events

@app.get("/services/{service_id}/events")
def get_service_events(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = db.get(Service, service_id)

    if service is None:
        raise HTTPException(
            status_code=404,
            detail="Service not found",
        )

    events = (
        db.query(Event)
        .filter(Event.service_id == service_id)
        .order_by(Event.created_at.desc())
        .all()
    )

    return events

#----------------------------------LOGIN, REGISTER AND GET CURRENT USER--------------------------------------------

@app.post("/auth/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.email == form_data.username)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    if not verify_password(
        form_data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    token = create_access_token(user.id)

    return {
        "access_token": token,
        "token_type": "bearer",
    }

@app.get("/auth/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user

@app.post("/auth/register", response_model=UserResponse)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    new_user = User(
        email=user.email,
        full_name=user.full_name,
        password_hash=hash_password(user.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
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
    current_user: User = Depends(get_current_user)
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
    current_user: User = Depends(get_current_user)
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