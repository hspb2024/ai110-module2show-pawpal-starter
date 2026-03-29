# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**
Core User Actions:
- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

Three core actions anybody should be able to perform:

1. Provide basic details of the owner and the pet, and the scheduler will know whom it is planning for.
2. Create tasks with a title, duration, priority (low, medium, high), and category (walk, feed, medication, etc.) with an optional time of day.
3. Ask the scheduler to generate an ordered plan of tasks for the day, fitting them in the owner's available time and prioritizing the tasks.

The structure is based on four classes:

- **Owner**: Holds information about the owner's name, minutes available per day for pet care, and personal preferences. Manages representing the human side of the equation.
- **Pet**: Holds information about the pet's name, species, and age. Links to an Owner. Manages representing the animal being cared for.
- **Task**: A dataclass for information about what needs to be done (title and category), how long it takes, and a preferred time slot. Manages representing individual care activities.
- **Scheduler**: Holds information about an Owner, a Pet, and a list of Tasks. Manages generating a daily plan.

After asking Claude Code to create a Mermaid.js class diagram based on brainstormed attributes and methods.
UML class diagram (Mermaid):

```mermaid
classDiagram
    class Owner {
        +str name
        +int available_minutes
        +list~str~ preferences
        +add_preference(preference: str) None
        +set_available_time(minutes: int) None
    }

    class Pet {
        +str name
        +str species
        +int age
        +get_species_defaults() list~str~
    }

    class Task {
        +str title
        +int duration_minutes
        +str priority
        +str category
        +Optional~str~ preferred_time
        +is_high_priority() bool
        +priority_score() int
    }

    class Scheduler {
        +Owner owner
        +Pet pet
        +list~Task~ tasks
        +add_task(task: Task) None
        +remove_task(title: str) None
        +generate_plan() list~Task~
        +explain_plan() str
    }

    Owner "1" --> "1..*" Pet : owns
    Scheduler "1" --> "1" Owner : uses
    Scheduler "1" --> "1" Pet : plans for
    Scheduler "1" --> "0..*" Task : schedules
```

---

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

No design changes were made during implementation. The four classes and their attributes and methods remained exactly as defined in the initial UML diagram.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The constraints it will consider are the amount of time the owner has in a day and the level of priority of each task. The scheduler will fill the day by choosing the most important tasks first and continue until there's no time left for the next task.

I have decided that the most important factor was the level of priority of each task. This was due to the fact that there are tasks that must be completed, like giving medication to a pet. The amount of time was the second most important factor. This was due to the fact that regardless of the importance of the task, the owner only had so much time in a day. The time of day was used as a tiebreaker if two tasks had the same level of priority.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The conflict detector only checks if two tasks are scheduled at exactly the same time. However, it does not verify if two tasks might have a conflict by checking if the end time of one task might overlap with the start time of the other. For example, if one task has a duration of 30 minutes and starts at 8:00, and another task starts at 8:15, it will not be detected by this function. However, it will be running at the same time. This trade-off is acceptable for now. However, it does catch obvious errors like two tasks being scheduled at the same time by accident. In the future, we could extend this function by also checking the duration of each task.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I utilized Claude Code to develop an initial UML diagram from my class concepts. Then, I utilized Copilot to assist in writing the code. It was more effective if I provided precise and detailed instructions, such as how to implement a method. Vague instructions were not very effective. Inline suggestions from the Copilot were more effective if I had a precise docstring.

I also maintained individual chat windows for each process to keep the AI focused only on the specific task.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

I chose to do a simple string comparison instead of using datetime as Copilot had suggested, and it worked just fine. I also tested it to confirm this.

I made all the design decisions myself. I let the AI do all the coding, and I just checked to make sure it worked.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

The 26 tests verify sorting by time, recurrence, conflicts, priority planning within a time budget, pet/task management, including edge cases where the pet has no tasks. These tests are important because if the sorting or priority planning logic is flawed, it would result in incorrect plans without any warning.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

Confidence level: ★★★★★ All 26 tests pass. More time would allow me to add tests for duration-based conflicts like where Task A from 8:00 for 30 minutes conflicts with Task B from 8:20 for instance.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

Separating the logic layer (`pawpal_system.py`) from the UI (`app.py`) made testing very easy and kept the code clean and simple for all four phases.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would expand the conflict detection to check for duration conflicts, implement an "Edit Task" form for the UI, and implement data persistence to allow the schedule to survive a page reload.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

Having a clear UML plan and design helped the AI have a clear goal to aim for, resulting in better suggestions and fewer corrections. AI is most effective when the human has already thought through the most important decisions.
