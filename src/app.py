"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from abc import ABC, abstractmethod
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")


class AbstractActivity(ABC):
    """Base contract for school activities."""

    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def description(self):
        pass

    @property
    @abstractmethod
    def schedule(self):
        pass

    @property
    @abstractmethod
    def max_participants(self):
        pass

    @property
    @abstractmethod
    def participants(self):
        pass

    @abstractmethod
    def add_participant(self, email: str) -> str:
        """Add a participant and return the normalized email."""
        pass

    @abstractmethod
    def is_full(self) -> bool:
        """Return True when the activity has reached capacity."""
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        """Convert the activity to a JSON-serializable dictionary."""
        pass


class Activity(AbstractActivity):
    """Concrete activity model with validation and participant management."""

    def __init__(self, name: str, description: str, schedule: str, max_participants: int,
                 participants=None):
        self._name = name
        self._description = description
        self._schedule = schedule
        self._max_participants = max_participants
        self._participants = [participant.strip().lower() for participant in (participants or [])]

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def schedule(self):
        return self._schedule

    @property
    def max_participants(self):
        return self._max_participants

    @property
    def participants(self):
        return self._participants

    def add_participant(self, email: str) -> str:
        normalized_email = email.strip().lower()
        if not normalized_email:
            raise ValueError("Email is required")

        if normalized_email in {participant.lower() for participant in self._participants}:
            raise ValueError(f"{normalized_email} is already signed up for {self.name}")

        if self.is_full():
            raise ValueError(f"{self.name} is full")

        self._participants.append(normalized_email)
        return normalized_email

    def is_full(self) -> bool:
        return len(self._participants) >= self._max_participants

    def to_dict(self) -> dict:
        return {
            "description": self.description,
            "schedule": self.schedule,
            "max_participants": self.max_participants,
            "participants": self.participants,
        }


# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": Activity(
        name="Chess Club",
        description="Learn strategies and compete in chess tournaments",
        schedule="Fridays, 3:30 PM - 5:00 PM",
        max_participants=12,
        participants=["michael@mergington.edu", "daniel@mergington.edu"],
    ),
    "Programming Class": Activity(
        name="Programming Class",
        description="Learn programming fundamentals and build software projects",
        schedule="Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        max_participants=20,
        participants=["emma@mergington.edu", "sophia@mergington.edu"],
    ),
    "Gym Class": Activity(
        name="Gym Class",
        description="Physical education and sports activities",
        schedule="Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        max_participants=30,
        participants=["john@mergington.edu", "olivia@mergington.edu"],
    ),
    "Soccer Team": Activity(
        name="Soccer Team",
        description="Practice teamwork and compete in local soccer matches",
        schedule="Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        max_participants=18,
        participants=[],
    ),
    "Basketball Club": Activity(
        name="Basketball Club",
        description="Develop shooting, defense, and game strategy skills",
        schedule="Wednesdays, 3:30 PM - 5:00 PM",
        max_participants=15,
        participants=[],
    ),
    "Drama Club": Activity(
        name="Drama Club",
        description="Explore acting, stage performance, and theater production",
        schedule="Mondays, 3:30 PM - 5:00 PM",
        max_participants=20,
        participants=[],
    ),
    "Art Studio": Activity(
        name="Art Studio",
        description="Create paintings, drawings, and visual projects",
        schedule="Thursdays, 3:30 PM - 5:00 PM",
        max_participants=16,
        participants=[],
    ),
    "Math Olympiad": Activity(
        name="Math Olympiad",
        description="Solve challenging problems and prepare for competitions",
        schedule="Fridays, 4:00 PM - 5:00 PM",
        max_participants=12,
        participants=[],
    ),
    "Debate Team": Activity(
        name="Debate Team",
        description="Practice public speaking and argumentation in team competitions",
        schedule="Wednesdays, 3:30 PM - 5:00 PM",
        max_participants=14,
        participants=[],
    ),
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return {name: activity.to_dict() for name, activity in activities.items()}


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]
    normalized_email = (email or "").strip().lower()

    if not normalized_email:
        raise HTTPException(status_code=400, detail="Email is required")

    if normalized_email in {participant.lower() for participant in activity.participants}:
        raise HTTPException(
            status_code=400,
            detail=f"{normalized_email} is already signed up for {activity_name}",
        )

    try:
        signed_up_email = activity.add_participant(email)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"message": f"Signed up {signed_up_email} for {activity_name}"}
