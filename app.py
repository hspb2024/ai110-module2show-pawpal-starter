import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Step 1 – Initialize session state (runs once; persists across reruns)
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None   # set when the owner form is submitted

# ---------------------------------------------------------------------------
# Section 1 – Owner setup
# ---------------------------------------------------------------------------
st.header("Owner Info")

with st.form("owner_form"):
    owner_name = st.text_input("Your name", value="John")
    available_minutes = st.number_input(
        "Minutes available today", min_value=10, max_value=480, value=90, step=10
    )
    if st.form_submit_button("Save owner"):
        st.session_state.owner = Owner(
            name=owner_name, available_minutes=int(available_minutes)
        )
        st.success(f"Owner saved: {owner_name} ({available_minutes} min available)")

if st.session_state.owner is None:
    st.info("Fill in your name above to get started.")
    st.stop()

owner: Owner = st.session_state.owner

# ---------------------------------------------------------------------------
# Section 2 – Add a pet
# ---------------------------------------------------------------------------
st.divider()
st.header("Pets")

with st.form("add_pet_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_name = st.text_input("Pet name", value="Mochi")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with col3:
        age = st.number_input("Age (years)", min_value=0, max_value=30, value=3)

    if st.form_submit_button("Add pet"):
        existing_names = [p.name for p in owner.pets]
        if pet_name in existing_names:
            st.warning(f"{pet_name} is already on the list.")
        else:
            owner.add_pet(Pet(name=pet_name, species=species, age=int(age)))
            st.success(f"Added {pet_name} the {species}!")

if owner.pets:
    st.write(f"**{owner.name}'s pets:** " + ", ".join(p.name for p in owner.pets))
else:
    st.info("No pets yet. Add one above.")

# ---------------------------------------------------------------------------
# Section 3 – Add tasks to a pet
# ---------------------------------------------------------------------------
st.divider()
st.header("Tasks")

if not owner.pets:
    st.info("Add a pet first before adding tasks.")
else:
    with st.form("add_task_form"):
        pet_choice = st.selectbox("Assign to pet", [p.name for p in owner.pets])
        col1, col2, col3 = st.columns(3)
        with col1:
            task_title = st.text_input("Task title", value="Morning walk")
        with col2:
            duration = st.number_input(
                "Duration (min)", min_value=1, max_value=240, value=20
            )
        with col3:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

        col4, col5 = st.columns(2)
        with col4:
            category = st.selectbox(
                "Category", ["walk", "feed", "meds", "grooming", "enrichment"]
            )
        with col5:
            preferred_time = st.selectbox(
                "Preferred time", ["morning", "afternoon", "evening", "any"]
            )

        if st.form_submit_button("Add task"):
            target_pet = next(p for p in owner.pets if p.name == pet_choice)
            target_pet.add_task(Task(
                title=task_title,
                duration_minutes=int(duration),
                priority=priority,
                category=category,
                preferred_time=None if preferred_time == "any" else preferred_time,
            ))
            st.success(f"Added '{task_title}' to {pet_choice}.")

    # Show current tasks per pet
    all_pairs = owner.get_all_tasks()
    if all_pairs:
        rows = [
            {
                "Pet": pet.name,
                "Task": task.title,
                "Duration (min)": task.duration_minutes,
                "Priority": task.priority,
                "Time": task.preferred_time or "any",
                "Done": "✓" if task.completed else "",
            }
            for pet, task in all_pairs
        ]
        st.table(rows)
    else:
        st.info("No tasks yet.")

# ---------------------------------------------------------------------------
# Section 4 – Generate schedule
# ---------------------------------------------------------------------------
st.divider()
st.header("Today's Schedule")

if st.button("Generate schedule"):
    if not owner.get_all_tasks():
        st.warning("Add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler(owner)
        plan = scheduler.generate_plan()
        explanation = scheduler.explain_plan()

        if plan:
            st.success(f"Scheduled {len(plan)} task(s) for {owner.name}.")
            plan_rows = [
                {
                    "Pet": pet.name,
                    "Task": task.title,
                    "Duration (min)": task.duration_minutes,
                    "Priority": task.priority,
                    "Time": task.preferred_time or "any",
                }
                for pet, task in plan
            ]
            st.table(plan_rows)
        else:
            st.error("No tasks fit within your available time.")

        with st.expander("Plan explanation"):
            st.text(explanation)
