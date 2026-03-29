"""
main.py – CLI demo for PawPal+

Demonstrates sorting by time, filtering by pet/status,
recurring task automation, and conflict detection.
"""

from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler


def section(title: str) -> None:
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")


def main() -> None:
    # --- Owner ---
    owner = Owner(name="John", available_minutes=120)

    # --- Pets ---
    mochi = Pet(name="Mochi", species="dog", age=3)
    olive = Pet(name="Olive", species="cat", age=5)

    owner.add_pet(mochi)
    owner.add_pet(olive)

    # --- Tasks added OUT OF ORDER (to demonstrate sorting) ---
    # Mochi tasks
    mochi.add_task(Task(
        title="Evening walk",
        duration_minutes=30,
        priority="medium",
        category="walk",
        preferred_time="evening",
        scheduled_time="18:00",
        frequency="daily",
        due_date=date.today(),
    ))
    mochi.add_task(Task(
        title="Breakfast",
        duration_minutes=10,
        priority="high",
        category="feed",
        preferred_time="morning",
        scheduled_time="07:30",
        frequency="daily",
        due_date=date.today(),
    ))
    mochi.add_task(Task(
        title="Flea treatment",
        duration_minutes=15,
        priority="medium",
        category="meds",
        preferred_time="evening",
        scheduled_time="19:00",
        frequency="weekly",
        due_date=date.today(),
    ))
    mochi.add_task(Task(
        title="Morning walk",
        duration_minutes=30,
        priority="high",
        category="walk",
        preferred_time="morning",
        scheduled_time="08:00",
        frequency="daily",
        due_date=date.today(),
    ))

    # Olive tasks
    olive.add_task(Task(
        title="Dinner",
        duration_minutes=10,
        priority="high",
        category="feed",
        preferred_time="evening",
        scheduled_time="18:00",   # <-- same time as Mochi's Evening walk → conflict!
        frequency="daily",
        due_date=date.today(),
    ))
    olive.add_task(Task(
        title="Brushing",
        duration_minutes=20,
        priority="low",
        category="grooming",
        preferred_time="afternoon",
        scheduled_time="14:00",
        frequency="once",
        due_date=date.today(),
    ))

    scheduler = Scheduler(owner)

    # ------------------------------------------------------------------
    # Step 1: Priority-based plan
    # ------------------------------------------------------------------
    section("Priority-based daily plan")
    print(scheduler.explain_plan())

    # ------------------------------------------------------------------
    # Step 2: Sort all tasks by scheduled_time (HH:MM)
    # ------------------------------------------------------------------
    section("All tasks sorted by scheduled time")
    for pet, task in scheduler.sort_by_time():
        time_label = task.scheduled_time or "no time set"
        print(f"  {time_label}  [{task.priority.upper()}] {task.title} — {pet.name}")

    # ------------------------------------------------------------------
    # Step 3: Filter tasks by pet name
    # ------------------------------------------------------------------
    section("Filter: Mochi's tasks only")
    for pet, task in scheduler.filter_by_pet("Mochi"):
        status = "done" if task.completed else "pending"
        print(f"  {task.title} ({status})")

    # ------------------------------------------------------------------
    # Step 4: Conflict detection
    # ------------------------------------------------------------------
    section("Conflict detection")
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            print(f"  ⚠  {warning}")
    else:
        print("  No conflicts found.")

    # ------------------------------------------------------------------
    # Step 5: Mark a recurring task complete → auto-schedule next occurrence
    # ------------------------------------------------------------------
    section("Recurring task: mark Breakfast complete")
    breakfast = mochi.tasks[1]   # "Breakfast" task
    print(f"  Before: {breakfast.title} due {breakfast.due_date}, completed={breakfast.completed}")

    next_task = scheduler.mark_task_complete(mochi, breakfast)

    print(f"  After:  {breakfast.title} completed={breakfast.completed}")
    if next_task:
        print(f"  Next occurrence added: '{next_task.title}' due {next_task.due_date}")

    # ------------------------------------------------------------------
    # Step 6: Filter pending vs completed
    # ------------------------------------------------------------------
    section("Filter: completed tasks")
    completed = scheduler.filter_by_status(completed=True)
    if completed:
        for pet, task in completed:
            print(f"  {task.title} — {pet.name}")
    else:
        print("  None yet.")

    section("Filter: pending tasks")
    for pet, task in scheduler.filter_by_status(completed=False):
        print(f"  {task.title} — {pet.name}")


if __name__ == "__main__":
    main()
