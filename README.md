# PawPal+ (Module 2 Project)

The application is named PawPal+ and is built using Streamlit. This application is designed to assist a busy pet owner with their pet care planning, considering multiple pets. The application utilizes a priority-first scheduling algorithm, conflict detection, recurring task automation, and filtering.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

## Smarter Scheduling

Phase 3 adds four new features to make the scheduler more useful:

- **Sort by time** — Tasks can be listed in order from earliest to latest based on their scheduled time.
- **Filter by pet or status** — You can view only the tasks for a specific pet, or only tasks that are done or still pending.
- **Recurring tasks** — Tasks can be set to repeat daily or weekly. When you mark one complete, the next occurrence is automatically added.
- **Conflict detection** — The scheduler warns you if two tasks are set to start at the exact same time.

## After polishing with use of Claude:
Features
- Multiple pets: Manage all your pets in one place.
- Smart scheduling: Important tasks are handled first so nothing critical is missed.
- Time preferences: Tasks are ordered by morning, afternoon, and evening.
- Daily timeline: View tasks in the order they’re scheduled.
- Conflict alerts: Get notified if two tasks overlap.
- Repeating tasks: Set tasks to repeat daily or weekly automatically.
- Easy filtering: Quickly view tasks by pet or status.
- Schedule summary: See a simple explanation of what was scheduled and skipped.
- Quick complete: Mark tasks as done with one click.

--- 

## Running the App

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Testing PawPal+

Run the tests with:

```bash
python3 -m pytest
```

The 26 tests include:
- **Sorting correctness**: tasks returned in chronological order, unscheduled tasks sort last
- **Recurrence logic**: daily/weekly tasks auto-add next occurrence, one-time tasks raise error
- **Conflict detection**: detects two tasks at same time, ignores tasks without scheduled time
- **Priority & planning**: respects time budget, skips completed tasks, prioritizes high priority tasks
- **Pet & Owner management**: add/remove tasks, case-insensitive pet filtering, status filtering, pet with no tasks

**Confidence Level: ★★★★★** — All 26 tests pass across both happy-path and edge-case scenarios.

---
## 📸 Demo



---
