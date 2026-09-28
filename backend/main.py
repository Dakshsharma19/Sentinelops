from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Service
from schemas import ServiceCreate, ServiceResponse

app = FastAPI()

Base.metadata.create_all(bind=engine)
print("DATABASE TABLES CREATED/CHECKED")


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/db-health")
def database_health_check():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return {"database": result.scalar() == 1}


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
def get_services(db: Session = Depends(get_db)):
    services = db.query(Service).all()
    return services