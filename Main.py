
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import csv
import os
import calendar
import uuid
from datetime import datetime, date

# ==========================================
# STUDENT DEADLINE MANAGER PRO
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "tasks.json")

BG = "#0B1120"
SIDEBAR = "#111827"
PANEL = "#172235"
CARD = "#1E293B"
BLUE = "#3B82F6"
CYAN = "#06B6D4"
GREEN = "#10B981"
RED = "#EF4444"
YELLOW = "#F59E0B"
WHITE = "#F8FAFC"
MUTED = "#94A3B8"


# ==========================================
# DATA MANAGEMENT
# ==========================================

def load_tasks():
    try:
        with open(DATA_FILE, "r") as file:
            data = json.load(file)

        if not isinstance(data, list):
            return []

        for task in data:
            task.setdefault("id", str(uuid.uuid4()))
            task.setdefault("subject", "General")
            task.setdefault("type", "Assignment")
            task.setdefault("priority", "Medium")
            task.setdefault("description", "")
            task.setdefault("status", "Pending")

        return data

    except (FileNotFoundError, json.JSONDecodeError):
        return []


TASKS = load_tasks()


def save_tasks():
    with open(DATA_FILE, "w") as file:
        json.dump(TASKS, file, indent=4)


def valid_date(value):
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def task_status(task):
    if task.get("status") == "Completed":
        return "Completed"

    if task["date"] < date.today().isoformat():
        return "Overdue"

    return "Pending"


# ==========================================
# MAIN APPLICATION
# ==========================================

class DeadlineApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Student Deadline Manager Pro")
        self.root.geometry("1250x780")
        self.root.minsize(1000, 650)
        self.root.configure(bg=BG)

        self.current_page = "Dashboard"
        self.search_var = tk.StringVar()
        self.filter_var = tk.StringVar(value="All")
        self.calendar_year = date.today().year
        self.calendar_month = date.today().month
        self.reminded = set()

        self.setup_styles()
        self.show_login()

    # ======================================
    # STYLES
    # ======================================

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background=CARD,
            foreground=WHITE,
            fieldbackground=CARD,
            rowheight=38,
            borderwidth=0,
            font=("Arial", 10)
        )

        style.configure(
            "Treeview.Heading",
            background=SIDEBAR,
            foreground=WHITE,
            font=("Arial", 10, "bold"),
            relief="flat",
            padding=10
        )

        style.map(
            "Treeview",
            background=[("selected", BLUE)],
            foreground=[("selected", WHITE)]
        )

        style.configure(
            "TCombobox",
            fieldbackground=CARD,
            background=CARD,
            foreground=WHITE
        )

    # ======================================
    # LOGIN
    # ======================================

    def show_login(self):
        self.login_frame = tk.Frame(self.root, bg=BG)
        self.login_frame.pack(fill="both", expand=True)

        box = tk.Frame(
            self.login_frame,
            bg=PANEL,
            padx=45,
            pady=40
        )
        box.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            box,
            text="STUDENT MANAGER",
            bg=PANEL,
            fg=BLUE,
            font=("Arial", 12, "bold")
        ).pack(pady=8)

        tk.Label(
            box,
            text="Welcome Back",
            bg=PANEL,
            fg=WHITE,
            font=("Arial", 25, "bold")
        ).pack(pady=5)

        tk.Label(
            box,
            text="Manage your academic deadlines",
            bg=PANEL,
            fg=MUTED
        ).pack(pady=5)

        tk.Label(
            box,
            text="Username",
            bg=PANEL,
            fg=WHITE
        ).pack(anchor="w", pady=(20, 5))

        self.username_entry = tk.Entry(
            box,
            width=32,
            bg=CARD,
            fg=WHITE,
            insertbackground=WHITE,
            relief="flat",
            font=("Arial", 12)
        )
        self.username_entry.pack(ipady=10)

        tk.Label(
            box,
            text="Password",
            bg=PANEL,
            fg=WHITE
        ).pack(anchor="w", pady=(15, 5))

        self.password_entry = tk.Entry(
            box,
            width=32,
            show="*",
            bg=CARD,
            fg=WHITE,
            insertbackground=WHITE,
            relief="flat",
            font=("Arial", 12)
        )
        self.password_entry.pack(ipady=10)

        tk.Button(
            box,
            text="LOGIN",
            command=self.login,
            bg=BLUE,
            fg=WHITE,
            relief="flat",
            font=("Arial", 11, "bold"),
            cursor="hand2"
        ).pack(fill="x", pady=25, ipady=10)

        tk.Label(
            box,
            text="Demo: student / 1234",
            bg=PANEL,
            fg=MUTED
        ).pack()

        self.password_entry.bind(
            "<Return>",
            lambda event: self.login()
        )

    def login(self):
        if (
            self.username_entry.get() == "student"
            and self.password_entry.get() == "1234"
        ):
            self.login_frame.destroy()
            self.build_dashboard()
            self.check_reminders()
        else:
            messagebox.showerror(
                "Login Failed",
                "Incorrect username or password!"
            )

    def logout(self):
        self.main.destroy()
        self.show_login()

    # ======================================
    # MAIN DASHBOARD LAYOUT
    # ======================================

    def build_dashboard(self):

        self.main = tk.Frame(self.root, bg=BG)
        self.main.pack(fill="both", expand=True)

        self.sidebar = tk.Frame(
            self.main,
            bg=SIDEBAR,
            width=230
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(
            self.sidebar,
            text="DEADLINE PRO",
            bg=SIDEBAR,
            fg=BLUE,
            font=("Arial", 18, "bold")
        ).pack(pady=30)

        self.nav_buttons = {}

        navigation = [
            "Dashboard",
            "Add Task",
            "Manage Tasks",
            "Calendar",
            "Clash Detector",
            "Priority Tasks",
            "Analytics",
            "Reports"
        ]

        for page in navigation:
            btn = tk.Button(
                self.sidebar,
                text="   " + page,
                anchor="w",
                command=lambda p=page: self.show_page(p),
                bg=SIDEBAR,
                fg=MUTED,
                activebackground=CARD,
                activeforeground=WHITE,
                relief="flat",
                font=("Arial", 11),
                cursor="hand2",
                padx=12,
                pady=13
            )
            btn.pack(fill="x", padx=10, pady=3)
            self.nav_buttons[page] = btn

        tk.Frame(
            self.sidebar,
            bg="#334155",
            height=1
        ).pack(fill="x", padx=15, pady=20)

        tk.Label(
            self.sidebar,
            text="STUDENT ACCOUNT",
            bg=SIDEBAR,
            fg=MUTED
        ).pack(pady=5)

        tk.Label(
            self.sidebar,
            text="Student",
            bg=SIDEBAR,
            fg=WHITE,
            font=("Arial", 12, "bold")
        ).pack(pady=5)

        tk.Button(
            self.sidebar,
            text="Logout",
            command=self.logout,
            bg="#7F1D1D",
            fg=WHITE,
            relief="flat",
            cursor="hand2",
            pady=10
        ).pack(side="bottom", fill="x", padx=15, pady=20)

        self.content = tk.Frame(self.main, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)

        self.header = tk.Frame(
            self.content,
            bg=BG,
            height=75
        )
        self.header.pack(fill="x", padx=25, pady=15)

        self.page_title = tk.Label(
            self.header,
            text="Dashboard",
            bg=BG,
            fg=WHITE,
            font=("Arial", 23, "bold")
        )
        self.page_title.pack(side="left")

        tk.Label(
            self.header,
            text=date.today().strftime("%d %B %Y"),
            bg=BG,
            fg=MUTED
        ).pack(side="right", padx=10)

        self.page_area = tk.Frame(self.content, bg=BG)
        self.page_area.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=10
        )

        self.show_page("Dashboard")

    # ======================================
    # COMMON FUNCTIONS
    # ======================================

    def clear_page(self):
        for widget in self.page_area.winfo_children():
            widget.destroy()

    def show_page(self, page):
        self.current_page = page
        self.clear_page()
        self.page_title.config(text=page)

        for name, btn in self.nav_buttons.items():
            btn.config(
                bg=BLUE if name == page else SIDEBAR,
                fg=WHITE if name == page else MUTED
            )

        pages = {
            "Dashboard": self.dashboard_page,
            "Add Task": self.add_task_page,
            "Manage Tasks": self.manage_page,
            "Calendar": self.calendar_page,
            "Clash Detector": self.clash_page,
            "Priority Tasks": self.priority_page,
            "Analytics": self.analytics_page,
            "Reports": self.reports_page
        }

        pages[page]()

    def make_label(self, parent, text, size=11, color=WHITE, bold=False):
        return tk.Label(
            parent,
            text=text,
            bg=parent.cget("bg"),
            fg=color,
            font=("Arial", size, "bold" if bold else "normal")
        )

    def make_button(self, parent, text, command, color=BLUE):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg=WHITE,
            activebackground=CYAN,
            activeforeground=WHITE,
            relief="flat",
            padx=15,
            pady=9,
            cursor="hand2",
            font=("Arial", 10, "bold")
        )

    def make_card(self, parent, title, value, color):
        card = tk.Frame(
            parent,
            bg=CARD,
            padx=20,
            pady=20
        )

        tk.Label(
            card,
            text=title,
            bg=CARD,
            fg=MUTED,
            font=("Arial", 11)
        ).pack(anchor="w")

        tk.Label(
            card,
            text=str(value),
            bg=CARD,
            fg=color,
            font=("Arial", 25, "bold")
        ).pack(anchor="w", pady=12)

        return card

    # ======================================
    # DASHBOARD
    # ======================================

    def dashboard_page(self):
        total = len(TASKS)

        completed = sum(
            1 for t in TASKS if task_status(t) == "Completed"
        )
        overdue = sum(
            1 for t in TASKS if task_status(t) == "Overdue"
        )
        pending = total - completed - overdue

        cards = tk.Frame(self.page_area, bg=BG)
        cards.pack(fill="x", pady=10)

        data = [
            ("TOTAL TASKS", total, BLUE),
            ("PENDING", pending, YELLOW),
            ("COMPLETED", completed, GREEN),
            ("OVERDUE", overdue, RED)
        ]

        for title, value, color in data:
            card = self.make_card(cards, title, value, color)
            card.pack(side="left", fill="both", expand=True, padx=6)

        progress = completed / total * 100 if total else 0

        panel = tk.Frame(
            self.page_area,
            bg=PANEL,
            padx=20,
            pady=20
        )
        panel.pack(fill="x", pady=15)

        self.make_label(
            panel,
            "Overall Completion Progress",
            14,
            WHITE,
            True
        ).pack(anchor="w")

        tk.Label(
            panel,
            text=f"{progress:.1f}% completed",
            bg=PANEL,
            fg=GREEN,
            font=("Arial", 19, "bold")
        ).pack(anchor="w", pady=10)

        ttk.Progressbar(
            panel,
            maximum=100,
            value=progress
        ).pack(fill="x", pady=5)

        upcoming_panel = tk.Frame(
            self.page_area,
            bg=PANEL,
            padx=20,
            pady=15
        )
        upcoming_panel.pack(fill="both", expand=True, pady=10)

        self.make_label(
            upcoming_panel,
            "Upcoming Deadlines",
            14,
            WHITE,
            True
        ).pack(anchor="w", pady=8)

        upcoming = sorted(
            [t for t in TASKS if task_status(t) != "Completed"],
            key=lambda t: t["date"]
        )[:5]

        if not upcoming:
            self.make_label(
                upcoming_panel,
                "No pending deadlines!",
                11,
                GREEN
            ).pack(anchor="w", pady=15)

        for task in upcoming:
            tk.Label(
                upcoming_panel,
                text=(
                    f"  {task['name']} | {task['date']} | "
                    f"{task.get('priority', 'Medium')}"
                ),
                bg=PANEL,
                fg=WHITE
            ).pack(anchor="w", pady=7)

        self.make_button(
            self.page_area,
            "+ Add New Task",
            lambda: self.show_page("Add Task")
        ).pack(anchor="e", pady=8)

    # ======================================
    # ADD / EDIT TASK
    # ======================================

    def add_task_page(self, existing=None):
        editing = existing is not None

        panel = tk.Frame(
            self.page_area,
            bg=PANEL,
            padx=30,
            pady=25
        )
        panel.pack(fill="both", expand=True)

        self.make_label(
            panel,
            "Edit Task" if editing else "Create New Task",
            19,
            WHITE,
            True
        ).pack(anchor="w", pady=(0, 20))

        fields = tk.Frame(panel, bg=PANEL)
        fields.pack(anchor="w")

        def create_field(label, row, col, width=30):
            tk.Label(
                fields,
                text=label,
                bg=PANEL,
                fg=MUTED,
                font=("Arial", 10, "bold")
            ).grid(
                row=row * 2,
                column=col,
                sticky="w",
                padx=12,
                pady=(8, 4)
            )

            entry = tk.Entry(
                fields,
                width=width,
                bg=CARD,
                fg=WHITE,
                insertbackground=WHITE,
                relief="flat",
                font=("Arial", 11)
            )
            entry.grid(
                row=row * 2 + 1,
                column=col,
                padx=12,
                pady=5,
                ipady=9,
                sticky="w"
            )
            return entry

        name = create_field("Task Name *", 0, 0)
        subject = create_field("Subject *", 0, 1)
        task_type = create_field("Task Type", 1, 0)
        due_date = create_field("Due Date (YYYY-MM-DD) *", 1, 1)

        tk.Label(
            fields,
            text="Priority",
            bg=PANEL,
            fg=MUTED
        ).grid(row=4, column=0, sticky="w", padx=12, pady=8)

        priority = ttk.Combobox(
            fields,
            values=["High", "Medium", "Low"],
            state="readonly",
            width=27
        )
        priority.grid(row=5, column=0, padx=12, pady=5, ipady=5)
        priority.set("Medium")

        tk.Label(
            fields,
            text="Description",
            bg=PANEL,
            fg=MUTED
        ).grid(row=6, column=0, sticky="w", padx=12, pady=8)

        description = tk.Text(
            panel,
            height=4,
            bg=CARD,
            fg=WHITE,
            insertbackground=WHITE,
            relief="flat",
            font=("Arial", 11)
        )
        description.pack(fill="x", pady=8)

        if editing:
            name.insert(0, existing["name"])
            subject.insert(0, existing.get("subject", ""))
            task_type.insert(0, existing.get("type", "Assignment"))
            due_date.insert(0, existing["date"])
            priority.set(existing.get("priority", "Medium"))
            description.insert("1.0", existing.get("description", ""))

        def save_form():
            task_name = name.get().strip()
            task_subject = subject.get().strip()
            task_date = due_date.get().strip()

            if not task_name or not task_subject or not task_date:
                messagebox.showwarning(
                    "Missing Information",
                    "Fill all required fields!"
                )
                return

            if not valid_date(task_date):
                messagebox.showerror(
                    "Invalid Date",
                    "Use YYYY-MM-DD format!"
                )
                return

            if editing:
                existing.update({
                    "name": task_name,
                    "subject": task_subject,
                    "type": task_type.get().strip() or "Assignment",
                    "date": task_date,
                    "priority": priority.get(),
                    "description": description.get("1.0", tk.END).strip()
                })
            else:
                TASKS.append({
                    "id": str(uuid.uuid4()),
                    "name": task_name,
                    "subject": task_subject,
                    "type": task_type.get().strip() or "Assignment",
                    "date": task_date,
                    "priority": priority.get(),
                    "description": description.get("1.0", tk.END).strip(),
                    "status": "Pending",
                    "created": datetime.now().isoformat(timespec="seconds")
                })

            save_tasks()
            messagebox.showinfo("Success", "Task saved successfully!")
            self.show_page("Manage Tasks")

        self.make_button(
            panel,
            "Update Task" if editing else "Save Task",
            save_form,
            GREEN
        ).pack(anchor="e", pady=15)

    # ======================================
    # TASK TABLE
    # ======================================

    def make_task_table(self, parent):
        columns = (
            "Name", "Subject", "Type",
            "Date", "Priority", "Status"
        )

        table = ttk.Treeview(
            parent,
            columns=columns,
            show="headings",
            height=12
        )

        widths = [180, 130, 110, 110, 90, 100]

        for col, width in zip(columns, widths):
            table.heading(col, text=col)
            table.column(col, width=width, anchor="center")

        table.pack(fill="both", expand=True, pady=10)
        return table

    def insert_task(self, table, task):
        table.insert(
            "",
            tk.END,
            iid=task["id"],
            values=(
                task["name"],
                task.get("subject", ""),
                task.get("type", ""),
                task["date"],
                task.get("priority", "Medium"),
                task_status(task)
            )
        )

    # ======================================
    # MANAGE TASKS
    # ======================================

    def manage_page(self):
        controls = tk.Frame(self.page_area, bg=BG)
        controls.pack(fill="x", pady=10)

        search = tk.Entry(
            controls,
            textvariable=self.search_var,
            bg=CARD,
            fg=WHITE,
            insertbackground=WHITE,
            relief="flat",
            font=("Arial", 11),
            width=25
        )
        search.pack(side="left", ipady=9, padx=5)

        filters = ttk.Combobox(
            controls,
            textvariable=self.filter_var,
            values=["All", "Pending", "Completed", "Overdue"],
            state="readonly",
            width=15
        )
        filters.pack(side="left", padx=8, ipady=5)

        table = self.make_task_table(self.page_area)

        def refresh():
            table.delete(*table.get_children())

            query = self.search_var.get().lower()
            selected_filter = self.filter_var.get()

            for task in TASKS:
                text = (
                    task["name"] + " " +
                    task.get("subject", "") + " " +
                    task.get("type", "")
                ).lower()

                if query not in text:
                    continue

                if selected_filter != "All":
                    if task_status(task) != selected_filter:
                        continue

                self.insert_task(table, task)

        search.bind("<KeyRelease>", lambda event: refresh())
        filters.bind("<<ComboboxSelected>>", lambda event: refresh())

        def selected_task():
            selection = table.selection()

            if not selection:
                messagebox.showwarning(
                    "Select Task",
                    "Please select a task first!"
                )
                return None

            task_id = selection[0]

            for task in TASKS:
                if task["id"] == task_id:
                    return task

            return None

        def edit():
            task = selected_task()
            if task:
                self.clear_page()
                self.current_page = "Add Task"
                self.page_title.config(text="Edit Task")
                self.add_task_page(task)

        def delete():
            task = selected_task()

            if task and messagebox.askyesno(
                "Confirm Delete",
                "Are you sure you want to delete this task?"
            ):
                TASKS.remove(task)
                save_tasks()
                refresh()

        def complete():
            task = selected_task()

            if task:
                task["status"] = "Completed"
                save_tasks()
                refresh()

        buttons = tk.Frame(self.page_area, bg=BG)
        buttons.pack(fill="x", pady=8)

        self.make_button(
            buttons, "Edit Task", edit, BLUE
        ).pack(side="left", padx=5)

        self.make_button(
            buttons, "Delete Task", delete, RED
        ).pack(side="left", padx=5)

        self.make_button(
            buttons, "Mark Completed", complete, GREEN
        ).pack(side="left", padx=5)

        refresh()

    # ======================================
    # CALENDAR
    # ======================================

    def calendar_page(self):
        top = tk.Frame(self.page_area, bg=BG)
        top.pack(fill="x", pady=10)

        def change_month(amount):
            self.calendar_month += amount

            if self.calendar_month > 12:
                self.calendar_month = 1
                self.calendar_year += 1
            elif self.calendar_month < 1:
                self.calendar_month = 12
                self.calendar_year -= 1

            self.show_page("Calendar")

        self.make_button(
            top, "< Previous", lambda: change_month(-1)
        ).pack(side="left")

        title = calendar.month_name[self.calendar_month]

        self.make_label(
            top,
            f"{title} {self.calendar_year}",
            18,
            WHITE,
            True
        ).pack(side="left", padx=25)

        self.make_button(
            top, "Next >", lambda: change_month(1)
        ).pack(side="left")

        grid = tk.Frame(self.page_area, bg=BG)
        grid.pack(fill="both", expand=True, pady=20)

        for col, day_name in enumerate(
            ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        ):
            tk.Label(
                grid,
                text=day_name,
                bg=PANEL,
                fg=CYAN,
                font=("Arial", 11, "bold"),
                pady=12
            ).grid(
                row=0, column=col,
                sticky="nsew", padx=2, pady=2
            )

        month_data = calendar.monthcalendar(
            self.calendar_year,
            self.calendar_month
        )

        for row, week in enumerate(month_data, start=1):
            for col, day in enumerate(week):
                cell = tk.Frame(
                    grid,
                    bg=CARD,
                    height=85,
                    padx=5,
                    pady=5
                )
                cell.grid(
                    row=row, column=col,
                    sticky="nsew", padx=2, pady=2
                )
                cell.grid_propagate(False)

                if day:
                    date_string = (
                        f"{self.calendar_year:04d}-"
                        f"{self.calendar_month:02d}-{day:02d}"
                    )

                    tk.Label(
                        cell,
                        text=str(day),
                        bg=CARD,
                        fg=WHITE,
                        font=("Arial", 12, "bold")
                    ).pack(anchor="nw")

                    daily_tasks = [
                        t for t in TASKS if t["date"] == date_string
                    ]

                    for task in daily_tasks[:2]:
                        tk.Label(
                            cell,
                            text="• " + task["name"][:13],
                            bg=CARD,
                            fg=YELLOW,
                            font=("Arial", 8)
                        ).pack(anchor="w")

                    if len(daily_tasks) > 2:
                        tk.Label(
                            cell,
                            text=f"+{len(daily_tasks)-2} more",
                            bg=CARD,
                            fg=CYAN,
                            font=("Arial", 8)
                        ).pack(anchor="w")

                grid.grid_columnconfigure(col, weight=1)

            grid.grid_rowconfigure(row, weight=1)

    # ======================================
    # CLASH DETECTOR
    # ======================================

    def clash_page(self):
        groups = {}

        for task in TASKS:
            if task_status(task) == "Completed":
                continue

            groups.setdefault(task["date"], []).append(task)

        clashes = {
            d: tasks for d, tasks in groups.items()
            if len(tasks) > 1
        }

        if not clashes:
            tk.Label(
                self.page_area,
                text="NO DEADLINE CLASHES FOUND!",
                bg=BG,
                fg=GREEN,
                font=("Arial", 20, "bold")
            ).pack(pady=60)

            self.make_label(
                self.page_area,
                "Your pending deadlines are on separate dates.",
                11,
                MUTED
            ).pack()
            return

        self.make_label(
            self.page_area,
            f"{len(clashes)} deadline collision(s) detected",
            17,
            RED,
            True
        ).pack(anchor="w", pady=10)

        for due_date, tasks in sorted(clashes.items()):
            panel = tk.Frame(
                self.page_area,
                bg=PANEL,
                padx=20,
                pady=15
            )
            panel.pack(fill="x", pady=8)

            tk.Label(
                panel,
                text=f"DEADLINE ALERT | {due_date}",
                bg=PANEL,
                fg=RED,
                font=("Arial", 12, "bold")
            ).pack(anchor="w")

            for task in tasks:
                tk.Label(
                    panel,
                    text=(
                        f"• {task['name']} "
                        f"({task.get('subject', 'No subject')})"
                    ),
                    bg=PANEL,
                    fg=WHITE,
                    font=("Arial", 11)
                ).pack(anchor="w", pady=4)

    # ======================================
    # PRIORITY TASKS
    # ======================================

    def priority_page(self):
        self.make_label(
            self.page_area,
            "Nearest deadlines and high-priority tasks first",
            12,
            MUTED
        ).pack(anchor="w", pady=10)

        table = self.make_task_table(self.page_area)

        sorted_tasks = sorted(
            [t for t in TASKS if task_status(t) != "Completed"],
            key=lambda t: (
                {"High": 0, "Medium": 1, "Low": 2}.get(
                    t.get("priority", "Medium"), 1
                ),
                t["date"]
            )
        )

        for task in sorted_tasks:
            self.insert_task(table, task)

    # ======================================
    # ANALYTICS
    # ======================================

    def analytics_page(self):
        total = len(TASKS)

        completed = sum(
            1 for t in TASKS if task_status(t) == "Completed"
        )
        pending = sum(
            1 for t in TASKS if task_status(t) == "Pending"
        )
        overdue = sum(
            1 for t in TASKS if task_status(t) == "Overdue"
        )

        self.make_label(
            self.page_area,
            "Task Performance Overview",
            18,
            WHITE,
            True
        ).pack(anchor="w", pady=10)

        canvas = tk.Canvas(
            self.page_area,
            bg=PANEL,
            height=300,
            highlightthickness=0
        )
        canvas.pack(fill="x", pady=20)

        values = [
            ("Completed", completed, GREEN),
            ("Pending", pending, YELLOW),
            ("Overdue", overdue, RED)
        ]

        max_value = max([v[1] for v in values] + [1])

        for i, (label, value, color) in enumerate(values):
            x = 80 + i * 250
            bar_height = (value / max_value) * 170

            canvas.create_rectangle(
                x, 230 - bar_height,
                x + 90, 230,
                fill=color,
                outline=""
            )

            canvas.create_text(
                x + 45, 250,
                text=label,
                fill=WHITE,
                font=("Arial", 11, "bold")
            )

            canvas.create_text(
                x + 45, 210 - bar_height,
                text=str(value),
                fill=WHITE,
                font=("Arial", 14, "bold")
            )

        percentage = completed / total * 100 if total else 0

        self.make_label(
            self.page_area,
            f"Completion Rate: {percentage:.1f}%",
            18,
            GREEN,
            True
        ).pack(anchor="w", pady=15)

        self.make_label(
            self.page_area,
            f"Total: {total} | Completed: {completed} | "
            f"Pending: {pending} | Overdue: {overdue}",
            11,
            MUTED
        ).pack(anchor="w")

    # ======================================
    # REMINDERS
    # ======================================

    def check_reminders(self):
        today = date.today().isoformat()
        alerts = []

        for task in TASKS:
            if task_status(task) == "Completed":
                continue

            if task["date"] <= today:
                task_id = task.get("id", task["name"] + task["date"])

                if task_id not in self.reminded:
                    self.reminded.add(task_id)

                    if task["date"] == today:
                        alerts.append(f"Due today: {task['name']}")
                    else:
                        alerts.append(
                            f"Overdue: {task['name']} ({task['date']})"
                        )

        if alerts:
            messagebox.showwarning(
                "Deadline Reminders",
                "\n".join(alerts)
            )

        self.root.after(60000, self.check_reminders)

    # ======================================
    # REPORTS / CSV EXPORT
    # ======================================

    def reports_page(self):
        panel = tk.Frame(
            self.page_area,
            bg=PANEL,
            padx=30,
            pady=30
        )
        panel.pack(fill="x", pady=20)

        self.make_label(
            panel,
            "Export Your Academic Reports",
            18,
            WHITE,
            True
        ).pack(anchor="w", pady=10)

        self.make_label(
            panel,
            "Download all tasks and their current status as a CSV file.",
            11,
            MUTED
        ).pack(anchor="w", pady=8)

        self.make_button(
            panel,
            "Export Tasks to CSV",
            self.export_csv,
            GREEN
        ).pack(anchor="w", pady=20)

    def export_csv(self):
        if not TASKS:
            messagebox.showinfo("No Data", "No tasks to export!")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="student_deadline_report.csv"
        )

        if not path:
            return

        with open(path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            writer.writerow([
                "Task Name",
                "Subject",
                "Type",
                "Due Date",
                "Priority",
                "Status",
                "Description"
            ])

            for task in TASKS:
                writer.writerow([
                    task["name"],
                    task.get("subject", ""),
                    task.get("type", ""),
                    task["date"],
                    task.get("priority", "Medium"),
                    task_status(task),
                    task.get("description", "")
                ])

        messagebox.showinfo(
            "Export Successful",
            "Your CSV report has been exported!"
        )


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":
    root = tk.Tk()
    app = DeadlineApp(root)
    root.mainloop()
