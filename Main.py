import json
from datetime import datetime

# Step 1: Load previously saved tasks
try:
    with open("tasks.json", "r") as file:
        TASKS = json.load(file)
except FileNotFoundError:
    TASKS = []


# Function to save tasks
def save_tasks():
    with open("tasks.json", "w") as file:
        json.dump(TASKS, file, indent=4)


# Step 2: Add a new task
def add_task():
    name = input("Enter task name: ")
    task_type = input("Enter task type: ")

    date = input("Enter due date (YYYY-MM-DD): ")

    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        print("Invalid date! Please use YYYY-MM-DD.")
        return

    task = {
        "name": name,
        "type": task_type,
        "date": date
    }

    TASKS.append(task)
    save_tasks()

    print("Task added successfully!")


# Step 3: View all tasks
def view_tasks():
    if not TASKS:
        print("No tasks available!")
        return

    print("\n===== ALL TASKS =====")

    for task in TASKS:
        print("Name:", task["name"])
        print("Type:", task["type"])
        print("Date:", task["date"])
        print("--------------------")


# Step 4: Check deadline clashes
def check_clash():
    date_groups = {}

    for task in TASKS:
        date = task["date"]

        if date not in date_groups:
            date_groups[date] = []

        date_groups[date].append(task)

    found = False

    for date, tasks in date_groups.items():

        if len(tasks) > 1:
            found = True

            print("\nDEADLINE COLLISION ALERT!")
            print("Date:", date)

            for task in tasks:
                print("-", task["name"])

    if not found:
        print("No deadline clashes found!")


# Step 5: Show priority tasks
def show_priority():
    if not TASKS:
        print("No tasks available!")
        return

    sorted_tasks = sorted(
        TASKS,
        key=lambda task: datetime.strptime(
            task["date"], "%Y-%m-%d"
        )
    )

    print("\n===== PRIORITY TASKS =====")

    for i, task in enumerate(sorted_tasks, start=1):
        print(i, task["name"], "-", task["date"])

    print("\nComplete the nearest deadline tasks first!")


# Step 6: Main menu
while True:

    print("\n===== STUDENT DEADLINE DETECTOR =====")
    print("1. Add New Task")
    print("2. View All Tasks")
    print("3. Check Deadline Clash")
    print("4. Show Priority Tasks")
    print("5. Exit")

    try:
        choice = int(input("Enter your choice: "))
    except ValueError:
        print("Please enter a valid number!")
        continue

    if choice == 1:
        add_task()

    elif choice == 2:
        view_tasks()

    elif choice == 3:
        check_clash()

    elif choice == 4:
        show_priority()

    elif choice == 5:
        print("Thank You for using Student Deadline Detector!")
        break

    else:
        print("Invalid Choice! Please try again.")

#python project student deadline clasher
