from sqlalchemy.orm import Session

from models import Event, Incident


def evaluate_event(
    event: Event,
    db: Session,
):
    """
    Evaluate a newly received event and create an incident
    if the event crosses a defined threshold.
    """

    incident_data = None

    if event.metric_name == "cpu_usage" and event.value is not None:
        if event.value > 90:
            incident_data = {
                "title": "High CPU usage detected",
                "severity": "high",
                "description": (
                    f"CPU usage reached {event.value}% "
                    f"on service {event.service_id}."
                ),
            }

    elif event.metric_name == "memory_usage" and event.value is not None:
        if event.value > 90:
            incident_data = {
                "title": "High memory usage detected",
                "severity": "high",
                "description": (
                    f"Memory usage reached {event.value}% "
                    f"on service {event.service_id}."
                ),
            }

    elif event.metric_name == "latency" and event.value is not None:
        if event.value > 2000:
            incident_data = {
                "title": "High API latency detected",
                "severity": "high",
                "description": (
                    f"API latency reached {event.value} ms "
                    f"on service {event.service_id}."
                ),
            }

    elif event.metric_name == "error_rate" and event.value is not None:
        if event.value > 5:
            incident_data = {
                "title": "High error rate detected",
                "severity": "high",
                "description": (
                    f"Error rate reached {event.value}% "
                    f"on service {event.service_id}."
                ),
            }

    elif event.event_type == "health_check":
        if event.severity == "critical":
            incident_data = {
                "title": "Service health check failed",
                "severity": "critical",
                "description": event.message
                or "Service health check failed.",
            }

    if incident_data is None:
        return None

    existing_incident = (
        db.query(Incident)
        .filter(
            Incident.service_id == event.service_id,
            Incident.title == incident_data["title"],
            Incident.status != "resolved",
        )
        .first()
    )

    if existing_incident:
        return existing_incident

    incident = Incident(
        service_id=event.service_id,
        title=incident_data["title"],
        description=incident_data["description"],
        severity=incident_data["severity"],
        status="open",
    )

    db.add(incident)
    db.commit()
    db.refresh(incident)

    return incident