"""
PawPal+ – logic layer
All backend classes live here. The Streamlit UI in app.py imports from this module.
"""

from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

@dataclass
class Owner:
    """Represents the pet owner and their scheduling constraints."""

    name: str
    available_minutes: int = 480  # default: 8 hours
    preferences: list[str] = field(default_factory=list)

    def add_preference(self, preference: str) -> None:
        """Add a scheduling preference (e.g. 'morning_walks')."""
        pass

    def set_available_time(self, minutes: int) -> None:
        """Update how many minutes per day are available for pet care."""
        pass


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    """Represents the pet whose care is being planned."""

    name: str
    species: str  # e.g. "dog", "cat", "other"
    age: int      # in years

    def get_species_defaults(self) -> list[str]:
        """Return a list of default task categories typical for this species."""
        pass


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """A single pet care activity."""

    title: str
    duration_minutes: int
    priority: str           # "low" | "medium" | "high"
    category: str           # "walk" | "feed" | "meds" | "grooming" | "enrichment"
    preferred_time: Optional[str] = None  # "morning" | "afternoon" | "evening" | None

    def is_high_priority(self) -> bool:
        """Return True if this task has high priority."""
        pass

    def priority_score(self) -> int:
        """Return a numeric score for sorting (higher = more urgent)."""
        pass


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    """
    Builds a daily care plan for a pet.

    Selects and orders tasks so they fit within the owner's available time,
    respecting priority and preferred time-of-day hints.
    """

    def __init__(self, owner: Owner, pet: Pet) -> None:
        self.owner = owner
        self.pet = pet
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        """Add a task to the pool of candidates for scheduling."""
        pass

    def remove_task(self, title: str) -> None:
        """Remove a task by title from the candidate pool."""
        pass

    def generate_plan(self) -> list[Task]:
        """
        Return an ordered list of tasks that fit within available_minutes.
        Higher-priority tasks are selected first; ties broken by duration.
        """
        pass

    def explain_plan(self) -> str:
        """
        Return a human-readable explanation of why each task was included
        (or excluded) in the generated plan.
        """
        pass
