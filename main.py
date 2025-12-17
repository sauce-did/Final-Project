"""
Sprint 2 Starter Code
Volunteer Hours Tracking System
Tech Stack: Python + Tkinter + SQLite

Sprint 2 Goal:
- Volunteer dashboard
- Hour submission
- View submission history
"""

import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import hashlib

# -------------------- DATABASE SETUP --------------------

def connect_db():
    return sqlite3.connect("volunteer_hours.db")


def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS VolunteerHours (
            hour_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            event_name TEXT,
            date TEXT,
            hours_worked REAL,
            description TEXT,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        )
    """)

    conn.commit()
    conn.close()

# -------------------- AUTH LOGIC --------------------

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(name, email, password, role="Volunteer"):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Users (name, email, password, role) VALUES (?, ?, ?, ?)",
            (name, email, hash_password(password), role)
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Account created successfully")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Email already exists")


def login_user(email, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT user_id, role FROM Users WHERE email=? AND password=?",
        (email, hash_password(password))
    )
    user = cursor.fetchone()
    conn.close()

    if user:
        messagebox.showinfo("Login Success", f"Logged in as {user[1]}")
        show_dashboard(user[0])
    else:
        messagebox.showerror("Login Failed", "Invalid credentials")

# -------------------- VOLUNTEER DASHBOARD --------------------

def submit_hours(user_id, event_name, date, hours_worked, description):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO VolunteerHours (user_id, event_name, date, hours_worked, description, status) VALUES (?, ?, ?, ?, ?, 'Pending')",
        (user_id, event_name, date, hours_worked, description)
    )
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Hours submitted successfully!")
    populate_history(user_id)


def get_user_hours(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT event_name, date, hours_worked, status FROM VolunteerHours WHERE user_id=?",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def show_dashboard(user_id):
    login_frame.pack_forget()
    register_frame.pack_forget()
    dashboard_frame.pack(pady=10)

    submit_button.config(command=lambda: submit_hours(
        user_id,
        event_name_entry.get(),
        date_entry.get(),
        hours_entry.get(),
        description_entry.get()
    ))

    populate_history(user_id)


def populate_history(user_id):
    for row in history_tree.get_children():
        history_tree.delete(row)

    for hr in get_user_hours(user_id):
        history_tree.insert('', 'end', values=hr)

# -------------------- UI --------------------

root = tk.Tk()
root.title("Volunteer Hours Tracking System – Sprint 2")
root.geometry("600x500")

# Login Frame
login_frame = tk.Frame(root)
login_frame.pack(pady=10)

email_label = tk.Label(login_frame, text="Email")
email_label.grid(row=0, column=0)
email_entry = tk.Entry(login_frame)
email_entry.grid(row=0, column=1)

password_label = tk.Label(login_frame, text="Password")
password_label.grid(row=1, column=0)
password_entry = tk.Entry(login_frame, show="*")
password_entry.grid(row=1, column=1)

login_button = tk.Button(
    login_frame,
    text="Login",
    command=lambda: login_user(email_entry.get(), password_entry.get())
)
login_button.grid(row=2, columnspan=2, pady=5)

# Registration Frame
register_frame = tk.Frame(root)
register_frame.pack(pady=10)

name_entry = tk.Entry(register_frame)
name_entry.grid(row=0, column=1)
tk.Label(register_frame, text="Name").grid(row=0, column=0)

reg_email_entry = tk.Entry(register_frame)
reg_email_entry.grid(row=1, column=1)
tk.Label(register_frame, text="Email").grid(row=1, column=0)

reg_password_entry = tk.Entry(register_frame, show="*")
reg_password_entry.grid(row=2, column=1)
tk.Label(register_frame, text="Password").grid(row=2, column=0)

register_button = tk.Button(
    register_frame,
    text="Register",
    command=lambda: register_user(
        name_entry.get(),
        reg_email_entry.get(),
        reg_password_entry.get()
    )
)
register_button.grid(row=3, columnspan=2, pady=5)

# Dashboard Frame
dashboard_frame = tk.Frame(root)

tk.Label(dashboard_frame, text="Event Name").grid(row=0, column=0)
event_name_entry = tk.Entry(dashboard_frame)
event_name_entry.grid(row=0, column=1)

tk.Label(dashboard_frame, text="Date (YYYY-MM-DD)").grid(row=1, column=0)
date_entry = tk.Entry(dashboard_frame)
date_entry.grid(row=1, column=1)

tk.Label(dashboard_frame, text="Hours Worked").grid(row=2, column=0)
hours_entry = tk.Entry(dashboard_frame)
hours_entry.grid(row=2, column=1)

tk.Label(dashboard_frame, text="Description").grid(row=3, column=0)
description_entry = tk.Entry(dashboard_frame)
description_entry.grid(row=3, column=1)

submit_button = tk.Button(dashboard_frame, text="Submit Hours")
submit_button.grid(row=4, columnspan=2, pady=5)

# Submission History
history_tree = ttk.Treeview(dashboard_frame, columns=("Event", "Date", "Hours", "Status"), show='headings')
history_tree.heading("Event", text="Event")
history_tree.heading("Date", text="Date")
history_tree.heading("Hours", text="Hours")
history_tree.heading("Status", text="Status")
history_tree.grid(row=5, columnspan=2, pady=10)

# Initialize DB
create_tables()

root.mainloop()
