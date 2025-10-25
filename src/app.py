"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi import status
import os
from pathlib import Path

from src.models import SessionLocal, Activity, Participant, create_tables

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Ensure DB tables exist on startup
create_tables()


def _activities_from_db():
    """Return a dict shaped like the original in-memory `activities` object.

    This keeps the API contract stable for the frontend while using the DB.
    """
    db = SessionLocal()
    try:
        result = {}
        activities = db.query(Activity).all()
        for a in activities:
            participants = [p.email for p in a.participants]
            result[a.name] = {
                "description": a.description,
                "schedule": a.schedule,
                "max_participants": a.max_participants,
                "participants": participants,
            }
        return result
    finally:
        db.close()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return _activities_from_db()


@app.post("/activities/{activity_name}/signup", status_code=status.HTTP_201_CREATED)
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity (persists to DB)."""
    db = SessionLocal()
    try:
        activity = db.query(Activity).filter(Activity.name == activity_name).first()
        if not activity:
            raise HTTPException(status_code=404, detail="Activity not found")

        # Check if already signed up
        existing = db.query(Participant).filter(Participant.activity_id == activity.id,
                                                 Participant.email == email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Student is already signed up")

        # Check capacity if set
        if activity.max_participants and len(activity.participants) >= activity.max_participants:
            raise HTTPException(status_code=400, detail="Activity is full")

        participant = Participant(activity_id=activity.id, email=email)
        db.add(participant)
        db.commit()
        return {"message": f"Signed up {email} for {activity_name}"}
    finally:
        db.close()


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity (persists to DB)."""
    db = SessionLocal()
    try:
        activity = db.query(Activity).filter(Activity.name == activity_name).first()
        if not activity:
            raise HTTPException(status_code=404, detail="Activity not found")

        participant = db.query(Participant).filter(Participant.activity_id == activity.id,
                                                   Participant.email == email).first()
        if not participant:
            raise HTTPException(status_code=400, detail="Student is not signed up for this activity")

        db.delete(participant)
        db.commit()
        return {"message": f"Unregistered {email} from {activity_name}"}
    finally:
        db.close()
