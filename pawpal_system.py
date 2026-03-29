"""
PawPal+ – logic layer
All backend classes live here. The Streamlit UI in app.py imports from this module.
"""

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """A single pet care activity with completion tracking."""

    title: str
    duration_minutes: int
    priority: str                  # "low" | "medium" | "high"
    category: str                  # "walk" | "feed" | "meds" | "grooming" | "enrichment"
    preferred_time: Optional[str] = None  # "morning" | "afternoon" | "evening" | None
    scheduled_time: Optional[str] = None  # "HH:MM" format, e.g. "08:30"
    frequency: str = "once"        # "once" | "daily" | "weekly"
    due_date: Optional[date] = None
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done for the day."""
        self.completed = True

    def is_high_priority(self) -> bool:
        """Return True if this task has high priority."""
        return self.priority == "high"

    def priority_score(self) -> int:
        """Return a numeric score for sorting; higher means more urgent."""
        return {"high": 3, "medium": 2, "low": 1}.get(self.priority, 0)

    def time_slot_order(self) -> int:
        """Return a sort key so morning < afternoon < evening < unspecified."""
        return {"morning": 0, "afternoon": 1, "evening": 2}.get(
            self.preferred_time or "", 3
        )

    def next_occurrence(self) -> "Task":
        """
        Return a new Task for the next recurrence of this task.

        Uses timedelta to advance the due_date by 1 day (daily) or 7 days (weekly).
        Raises ValueError if frequency is 'once'.
        """
        if self.frequency == "once":
            raise ValueError(f"Task '{self.title}' is not recurring.")

        base = self.due_date or date.today()
        delta = timedelta(days=1) if self.frequency == "daily" else timedelta(weeks=1)

        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            category=self.category,
            preferred_time=self.preferred_time,
            scheduled_time=self.scheduled_time,
            frequency=self.frequency,
            due_date=base + delta,
            completed=False,
        )


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    """Represents a pet and the tasks associated with its care."""

    name: str
    species: str          # e.g. "dog", "cat", "other"
    age: int              # in years
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        """Remove a task by title; does nothing if the title is not found."""
        self.tasks = [t for t in self.tasks if t.title != title]

    def get_tasks(self) -> list[Task]:
        """Return all tasks belonging to this pet."""
        return list(self.tasks)

    def get_species_defaults(self) -> list[str]:
        """Return default task categories typical for this species."""
        defaults = {
            "dog": ["walk", "feed", "grooming"],
            "cat": ["feed", "enrichment", "grooming"],
        }
        return defaults.get(self.species, ["feed"])


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

@dataclass
class Owner:
    """Manages one or more pets and exposes scheduling constraints."""

    name: str
    available_minutes: int = 480        # default: 8 hours
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's roster."""
        self.pets.append(pet)

    def remove_pet(self, name: str) -> None:
        """Remove a pet by name; does nothing if the name is not found."""
        self.pets = [p for p in self.pets if p.name != name]

    def add_preference(self, preference: str) -> None:
        """Add a scheduling preference (e.g. 'morning_walks')."""
        self.preferences.append(preference)

    def set_available_time(self, minutes: int) -> None:
        """Update how many minutes per day are available for pet care."""
        self.available_minutes = minutes

    def get_all_tasks(self) -> list[tuple["Pet", Task]]:
        """Return all (pet, task) pairs across every pet this owner has."""
        pairs: list[tuple[Pet, Task]] = []
        for pet in self.pets:
            for task in pet.get_tasks():
                pairs.append((pet, task))
        return pairs


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    """
    Builds a daily care plan across all of an owner's pets.

    Retrieves tasks from the owner's pets, filters out completed ones,
    selects tasks that fit within the owner's available time (highest
    priority first), and can explain why each task was included or skipped.
    Supports sorting by scheduled time, filtering by pet or status,
    recurring task automation, and conflict detection.
    """

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def _sorted_candidates(self) -> list[tuple[Pet, Task]]:
        """Return incomplete tasks sorted by priority (desc) then time slot."""
        pairs = [
            (pet, task)
            for pet, task in self.owner.get_all_tasks()
            if not task.completed
        ]
        return sorted(
            pairs,
            key=lambda pt: (-pt[1].priority_score(), pt[1].time_slot_order()),
        )

    def sort_by_time(self) -> list[tuple[Pet, Task]]:
        """
        Return all tasks sorted by their scheduled_time in ascending order.

        Tasks with a scheduled_time in "HH:MM" format come first (earliest to
        latest). Tasks without a scheduled_time are sorted to the end using
        "99:99" as a sentinel so they never compare before real times.
        """
        all_pairs = self.owner.get_all_tasks()
        return sorted(
            all_pairs,
            key=lambda pt: pt[1].scheduled_time or "99:99",
        )

    def filter_by_pet(self, pet_name: str) -> list[tuple[Pet, Task]]:
        """
        Return all (pet, task) pairs where the pet's name matches pet_name.

        The comparison is case-insensitive so 'mochi' and 'Mochi' both match.
        """
        name_lower = pet_name.lower()
        return [
            (pet, task)
            for pet, task in self.owner.get_all_tasks()
            if pet.name.lower() == name_lower
        ]

    def filter_by_status(self, completed: bool) -> list[tuple[Pet, Task]]:
        """
        Return all (pet, task) pairs whose completed flag equals the given value.

        Pass completed=True to see finished tasks; False to see pending tasks.
        """
        return [
            (pet, task)
            for pet, task in self.owner.get_all_tasks()
            if task.completed == completed
        ]

    def mark_task_complete(self, pet: Pet, task: Task) -> Optional[Task]:
        """
        Mark a task complete and, for recurring tasks, automatically add a new
        occurrence to the same pet.

        Returns the newly created Task if one was generated, otherwise None.
        """
        task.mark_complete()
        if task.frequency != "once":
            next_task = task.next_occurrence()
            pet.add_task(next_task)
            return next_task
        return None

    def detect_conflicts(self) -> list[str]:
        """
        Check whether any two tasks share the same scheduled_time.

        Returns a list of warning strings describing each conflict found.
        Tasks without a scheduled_time are skipped. This is a lightweight
        exact-match check: only tasks at the identical "HH:MM" value collide.
        """
        warnings: list[str] = []
        timed_pairs = [
            (pet, task)
            for pet, task in self.owner.get_all_tasks()
            if task.scheduled_time is not None
        ]

        # Compare every unique pair (i, j) with i < j to avoid duplicates.
        for i in range(len(timed_pairs)):
            for j in range(i + 1, len(timed_pairs)):
                pet_a, task_a = timed_pairs[i]
                pet_b, task_b = timed_pairs[j]
                if task_a.scheduled_time == task_b.scheduled_time:
                    warnings.append(
                        f"CONFLICT at {task_a.scheduled_time}: "
                        f"'{task_a.title}' ({pet_a.name}) "
                        f"and '{task_b.title}' ({pet_b.name})"
                    )

        return warnings

    def generate_plan(self) -> list[tuple[Pet, Task]]:
        """
        Return an ordered list of (pet, task) pairs that fit within
        available_minutes. Higher-priority tasks are selected first.
        """
        budget = self.owner.available_minutes
        plan: list[tuple[Pet, Task]] = []
        for pet, task in self._sorted_candidates():
            if task.duration_minutes <= budget:
                plan.append((pet, task))
                budget -= task.duration_minutes
        return plan

    def explain_plan(self) -> str:
        """Return a human-readable summary of the generated plan and any skipped tasks."""
        candidates = self._sorted_candidates()
        plan = self.generate_plan()
        planned_titles = {task.title for _, task in plan}

        lines: list[str] = [
            f"Daily plan for {self.owner.name} "
            f"({self.owner.available_minutes} min available)\n"
            f"{'='*50}"
        ]

        if not plan:
            lines.append("No tasks fit within the available time.")
        else:
            total = 0
            for pet, task in plan:
                slot = task.preferred_time or "any time"
                lines.append(
                    f"  [{task.priority.upper()}] {task.title} "
                    f"({task.duration_minutes} min, {slot}) — {pet.name}"
                )
                total += task.duration_minutes
            lines.append(f"\nTotal scheduled: {total} min")

        skipped = [
            (pet, task)
            for pet, task in candidates
            if task.title not in planned_titles
        ]
        if skipped:
            lines.append("\nSkipped (did not fit in remaining time):")
            for pet, task in skipped:
                lines.append(
                    f"  {task.title} ({task.duration_minutes} min) — {pet.name}"
                )

        return "\n".join(lines)
