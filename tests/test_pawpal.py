"""Tests for PawPal+ core logic."""

import pytest
from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler


# ---------------------------------------------------------------------------
# Task tests
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    """mark_complete() should set completed to True."""
    task = Task(title="Morning walk", duration_minutes=30, priority="high", category="walk")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_priority_score_values():
    """priority_score() should return 3/2/1 for high/medium/low."""
    assert Task(title="A", duration_minutes=10, priority="high", category="walk").priority_score() == 3
    assert Task(title="B", duration_minutes=10, priority="medium", category="feed").priority_score() == 2
    assert Task(title="C", duration_minutes=10, priority="low", category="enrichment").priority_score() == 1


def test_is_high_priority():
    """is_high_priority() should return True only for high-priority tasks."""
    high = Task(title="Meds", duration_minutes=5, priority="high", category="meds")
    low = Task(title="Play", duration_minutes=20, priority="low", category="enrichment")
    assert high.is_high_priority() is True
    assert low.is_high_priority() is False


def test_time_slot_order():
    """time_slot_order() should sort morning < afternoon < evening < None."""
    morning = Task(title="A", duration_minutes=10, priority="low", category="walk", preferred_time="morning")
    afternoon = Task(title="B", duration_minutes=10, priority="low", category="walk", preferred_time="afternoon")
    evening = Task(title="C", duration_minutes=10, priority="low", category="walk", preferred_time="evening")
    unspecified = Task(title="D", duration_minutes=10, priority="low", category="walk")
    assert morning.time_slot_order() < afternoon.time_slot_order()
    assert afternoon.time_slot_order() < evening.time_slot_order()
    assert evening.time_slot_order() < unspecified.time_slot_order()


# ---------------------------------------------------------------------------
# Recurrence tests
# ---------------------------------------------------------------------------

def test_next_occurrence_daily_advances_one_day():
    """next_occurrence() on a daily task should advance due_date by 1 day."""
    today = date.today()
    task = Task(
        title="Feed Mochi",
        duration_minutes=10,
        priority="high",
        category="feed",
        frequency="daily",
        due_date=today,
    )
    next_task = task.next_occurrence()
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.completed is False
    assert next_task.title == task.title


def test_next_occurrence_weekly_advances_seven_days():
    """next_occurrence() on a weekly task should advance due_date by 7 days."""
    today = date.today()
    task = Task(
        title="Bath time",
        duration_minutes=30,
        priority="medium",
        category="grooming",
        frequency="weekly",
        due_date=today,
    )
    next_task = task.next_occurrence()
    assert next_task.due_date == today + timedelta(weeks=1)


def test_next_occurrence_raises_for_once_task():
    """next_occurrence() should raise ValueError for a one-time task."""
    task = Task(title="Vet visit", duration_minutes=60, priority="high", category="meds", frequency="once")
    with pytest.raises(ValueError):
        task.next_occurrence()


def test_mark_task_complete_creates_recurrence():
    """Marking a daily task complete via Scheduler should add the next occurrence to the pet."""
    owner = Owner(name="Jordan", available_minutes=480)
    pet = Pet(name="Mochi", species="dog", age=3)
    task = Task(
        title="Feed Mochi",
        duration_minutes=10,
        priority="high",
        category="feed",
        frequency="daily",
        due_date=date.today(),
    )
    pet.add_task(task)
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    new_task = scheduler.mark_task_complete(pet, task)

    assert task.completed is True
    assert new_task is not None
    assert new_task.due_date == date.today() + timedelta(days=1)
    # The new task should be in the pet's task list
    assert new_task in pet.tasks


def test_mark_task_complete_once_returns_none():
    """Marking a one-time task complete should return None (no recurrence)."""
    owner = Owner(name="Jordan", available_minutes=480)
    pet = Pet(name="Luna", species="cat", age=2)
    task = Task(title="Vet visit", duration_minutes=60, priority="high", category="meds", frequency="once")
    pet.add_task(task)
    owner.add_pet(pet)

    result = Scheduler(owner).mark_task_complete(pet, task)
    assert result is None
    assert task.completed is True


# ---------------------------------------------------------------------------
# Sorting tests
# ---------------------------------------------------------------------------

def test_sort_by_time_chronological_order():
    """sort_by_time() should return tasks in ascending HH:MM order."""
    owner = Owner(name="Jordan", available_minutes=480)
    pet = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(Task(title="Evening walk", duration_minutes=30, priority="low", category="walk", scheduled_time="18:00"))
    pet.add_task(Task(title="Morning meds", duration_minutes=5, priority="high", category="meds", scheduled_time="08:00"))
    pet.add_task(Task(title="Lunch feed", duration_minutes=10, priority="medium", category="feed", scheduled_time="12:30"))
    owner.add_pet(pet)

    sorted_tasks = Scheduler(owner).sort_by_time()
    times = [task.scheduled_time for _, task in sorted_tasks]
    assert times == sorted(times)


def test_sort_by_time_unscheduled_tasks_last():
    """Tasks without a scheduled_time should appear at the end of sort_by_time()."""
    owner = Owner(name="Jordan", available_minutes=480)
    pet = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(Task(title="No time task", duration_minutes=10, priority="high", category="enrichment"))
    pet.add_task(Task(title="Morning task", duration_minutes=10, priority="low", category="walk", scheduled_time="07:00"))
    owner.add_pet(pet)

    sorted_tasks = Scheduler(owner).sort_by_time()
    titles = [task.title for _, task in sorted_tasks]
    assert titles[-1] == "No time task"


# ---------------------------------------------------------------------------
# Conflict detection tests
# ---------------------------------------------------------------------------

def test_detect_conflicts_flags_same_time():
    """detect_conflicts() should return a warning when two tasks share the same scheduled_time."""
    owner = Owner(name="Jordan", available_minutes=480)
    pet = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(Task(title="Walk", duration_minutes=20, priority="high", category="walk", scheduled_time="08:00"))
    pet.add_task(Task(title="Feed", duration_minutes=10, priority="high", category="feed", scheduled_time="08:00"))
    owner.add_pet(pet)

    warnings = Scheduler(owner).detect_conflicts()
    assert len(warnings) == 1
    assert "08:00" in warnings[0]


def test_detect_conflicts_no_conflicts():
    """detect_conflicts() should return an empty list when no times overlap."""
    owner = Owner(name="Jordan", available_minutes=480)
    pet = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(Task(title="Walk", duration_minutes=20, priority="high", category="walk", scheduled_time="08:00"))
    pet.add_task(Task(title="Feed", duration_minutes=10, priority="high", category="feed", scheduled_time="12:00"))
    owner.add_pet(pet)

    warnings = Scheduler(owner).detect_conflicts()
    assert warnings == []


def test_detect_conflicts_tasks_without_time_ignored():
    """Tasks with no scheduled_time should not trigger conflict warnings."""
    owner = Owner(name="Jordan", available_minutes=480)
    pet = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(Task(title="Walk", duration_minutes=20, priority="high", category="walk"))
    pet.add_task(Task(title="Feed", duration_minutes=10, priority="high", category="feed"))
    owner.add_pet(pet)

    warnings = Scheduler(owner).detect_conflicts()
    assert warnings == []


# ---------------------------------------------------------------------------
# Pet tests
# ---------------------------------------------------------------------------

def test_add_task_increases_count():
    """Adding a task to a Pet should increase its task count by one."""
    pet = Pet(name="Mochi", species="dog", age=3)
    assert len(pet.tasks) == 0
    pet.add_task(Task(title="Walk", duration_minutes=20, priority="high", category="walk"))
    assert len(pet.tasks) == 1


def test_remove_task_decreases_count():
    """Removing a task by title should decrease the pet's task count."""
    pet = Pet(name="Luna", species="cat", age=2)
    pet.add_task(Task(title="Brushing", duration_minutes=15, priority="low", category="grooming"))
    pet.remove_task("Brushing")
    assert len(pet.tasks) == 0


def test_remove_nonexistent_task_no_error():
    """Removing a title that doesn't exist should leave the task list unchanged."""
    pet = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(Task(title="Walk", duration_minutes=20, priority="high", category="walk"))
    pet.remove_task("Nonexistent")
    assert len(pet.tasks) == 1


def test_pet_with_no_tasks():
    """A pet with no tasks should return an empty list and produce an empty plan."""
    owner = Owner(name="Jordan", available_minutes=480)
    pet = Pet(name="Ghost", species="cat", age=1)
    owner.add_pet(pet)

    plan = Scheduler(owner).generate_plan()
    assert plan == []


def test_get_species_defaults_dog():
    """Dogs should have walk, feed, and grooming as default categories."""
    pet = Pet(name="Rex", species="dog", age=5)
    defaults = pet.get_species_defaults()
    assert "walk" in defaults
    assert "feed" in defaults


def test_get_species_defaults_unknown():
    """Unknown species should fall back to ['feed']."""
    pet = Pet(name="Scales", species="lizard", age=2)
    assert pet.get_species_defaults() == ["feed"]


# ---------------------------------------------------------------------------
# Scheduler tests
# ---------------------------------------------------------------------------

def test_scheduler_respects_time_budget():
    """generate_plan() should not exceed the owner's available_minutes."""
    owner = Owner(name="Jordan", available_minutes=30)
    pet = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(Task(title="Walk", duration_minutes=20, priority="high", category="walk"))
    pet.add_task(Task(title="Grooming", duration_minutes=20, priority="medium", category="grooming"))
    owner.add_pet(pet)

    plan = Scheduler(owner).generate_plan()
    total = sum(task.duration_minutes for _, task in plan)
    assert total <= owner.available_minutes


def test_scheduler_skips_completed_tasks():
    """generate_plan() should not include tasks that are already completed."""
    owner = Owner(name="Jordan", available_minutes=120)
    pet = Pet(name="Mochi", species="dog", age=3)
    done_task = Task(title="Walk", duration_minutes=20, priority="high", category="walk")
    done_task.mark_complete()
    pet.add_task(done_task)
    owner.add_pet(pet)

    plan = Scheduler(owner).generate_plan()
    assert all(task.title != "Walk" for _, task in plan)


def test_scheduler_prioritizes_high_priority_tasks():
    """High-priority tasks should appear before low-priority ones in the plan."""
    owner = Owner(name="Jordan", available_minutes=120)
    pet = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(Task(title="Low task", duration_minutes=10, priority="low", category="enrichment"))
    pet.add_task(Task(title="High task", duration_minutes=10, priority="high", category="meds"))
    owner.add_pet(pet)

    plan = Scheduler(owner).generate_plan()
    titles = [task.title for _, task in plan]
    assert titles.index("High task") < titles.index("Low task")


def test_filter_by_pet_case_insensitive():
    """filter_by_pet() should match regardless of name casing."""
    owner = Owner(name="Jordan", available_minutes=480)
    pet = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(Task(title="Walk", duration_minutes=20, priority="high", category="walk"))
    owner.add_pet(pet)

    results = Scheduler(owner).filter_by_pet("mochi")
    assert len(results) == 1
    results_upper = Scheduler(owner).filter_by_pet("MOCHI")
    assert len(results_upper) == 1


def test_filter_by_status_completed():
    """filter_by_status(True) should return only completed tasks."""
    owner = Owner(name="Jordan", available_minutes=480)
    pet = Pet(name="Mochi", species="dog", age=3)
    done = Task(title="Walk", duration_minutes=20, priority="high", category="walk")
    done.mark_complete()
    pending = Task(title="Feed", duration_minutes=10, priority="medium", category="feed")
    pet.add_task(done)
    pet.add_task(pending)
    owner.add_pet(pet)

    completed = Scheduler(owner).filter_by_status(True)
    assert all(task.completed for _, task in completed)
    assert len(completed) == 1


def test_filter_by_status_pending():
    """filter_by_status(False) should return only incomplete tasks."""
    owner = Owner(name="Jordan", available_minutes=480)
    pet = Pet(name="Mochi", species="dog", age=3)
    done = Task(title="Walk", duration_minutes=20, priority="high", category="walk")
    done.mark_complete()
    pending = Task(title="Feed", duration_minutes=10, priority="medium", category="feed")
    pet.add_task(done)
    pet.add_task(pending)
    owner.add_pet(pet)

    pending_tasks = Scheduler(owner).filter_by_status(False)
    assert all(not task.completed for _, task in pending_tasks)
    assert len(pending_tasks) == 1
