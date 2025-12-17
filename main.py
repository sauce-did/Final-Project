"""
Sprint 3 Final MVP Code
Volunteer Hours Tracking System
Tech Stack: Python + Tkinter + SQLite

Sprint 3 Goal:
- Admin approval of hours
- Role-based access (Volunteer vs Admin)
- Final MVP polish
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
        if user[1] == "Admin":
            show_admin_dashboard()
        else:
            show_volunteer_dashboard(user[0])
    else:
        messagebox.showerror("Login Failed", "Invalid credentials")

# -------------------- VOLUNTEER FUNCTIONS --------------------

def submit_hours(user_id, event_name, date, hours_worked, description):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO VolunteerHours (user_id, event_name, date, hours_worked, description) VALUES (?, ?, ?, ?, ?)",
        (user_id, event_name, date, hours_worked, description)
    )
    conn.commit()
    conn.close()
    messagebox.showinfo("Submitted", "Hours submitted for approval")
    populate_volunteer_history(user_id)


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

# -------------------- ADMIN FUNCTIONS --------------------

def get_pending_hours():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT hour_id, event_name, date, hours_worked FROM VolunteerHours WHERE status='Pending'"
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def update_status(hour_id, status):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE VolunteerHours SET status=? WHERE hour_id=?",
        (status, hour_id)
    )
    conn.commit()
    conn.close()
    populate_admin_table()

# -------------------- DASHBOARDS --------------------

def show_volunteer_dashboard(user_id):
    login_frame.pack_forget()
    register_frame.pack_forget()
    volunteer_frame.pack(pady=10)

    submit_btn.config(command=lambda: submit_hours(
        user_id,
        event_entry.get(),
        date_entry.get(),
        hours_entry.get(),
        desc_entry.get()
    ))

    populate_volunteer_history(user_id)


def show_admin_dashboard():
    login_frame.pack_forget()
    register_frame.pack_forget()
    admin_frame.pack(pady=10)
    populate_admin_table()


def populate_volunteer_history(user_id):
    for row in volunteer_tree.get_children():
        volunteer_tree.delete(row)
    for hr in get_user_hours(user_id):
        volunteer_tree.insert('', 'end', values=hr)


def populate_admin_table():
    for row in admin_tree.get_children():
        admin_tree.delete(row)
    for hr in get_pending_hours():
        admin_tree.insert('', 'end', values=hr)

# -------------------- UI --------------------

root = tk.Tk()
root.title("Volunteer Hours Tracking System – Final MVP")
root.geometry("700x500")

# Login Frame
login_frame = tk.Frame(root)
login_frame.pack(pady=10)

tk.Label(login_frame, text="Email").grid(row=0, column=0)
email_entry = tk.Entry(login_frame)
email_entry.grid(row=0, column=1)

tk.Label(login_frame, text="Password").grid(row=1, column=0)
password_entry = tk.Entry(login_frame, show="*")
password_entry.grid(row=1, column=1)

login_btn = tk.Button(login_frame, text="Login", command=lambda: login_user(email_entry.get(), password_entry.get()))
login_btn.grid(row=2, columnspan=2, pady=5)

# Register Frame
register_frame = tk.Frame(root)
register_frame.pack(pady=10)

tk.Label(register_frame, text="Name").grid(row=0, column=0)
name_entry = tk.Entry(register_frame)
name_entry.grid(row=0, column=1)

tk.Label(register_frame, text="Email").grid(row=1, column=0)
reg_email_entry = tk.Entry(register_frame)
reg_email_entry.grid(row=1, column=1)

tk.Label(register_frame, text="Password").grid(row=2, column=0)
reg_password_entry = tk.Entry(register_frame, show="*")
reg_password_entry.grid(row=2, column=1)

register_btn = tk.Button(register_frame, text="Register", command=lambda: register_user(name_entry.get(), reg_email_entry.get(), reg_password_entry.get()))
register_btn.grid(row=3, columnspan=2, pady=5)

# Volunteer Dashboard
volunteer_frame = tk.Frame(root)

tk.Label(volunteer_frame, text="Event").grid(row=0, column=0)
event_entry = tk.Entry(volunteer_frame)
event_entry.grid(row=0, column=1)

tk.Label(volunteer_frame, text="Date").grid(row=1, column=0)
date_entry = tk.Entry(volunteer_frame)
date_entry.grid(row=1, column=1)

tk.Label(volunteer_frame, text="Hours").grid(row=2, column=0)
hours_entry = tk.Entry(volunteer_frame)
hours_entry.grid(row=2, column=1)

tk.Label(volunteer_frame, text="Description").grid(row=3, column=0)
desc_entry = tk.Entry(volunteer_frame)
desc_entry.grid(row=3, column=1)

submit_btn = tk.Button(volunteer_frame, text="Submit Hours")
submit_btn.grid(row=4, columnspan=2, pady=5)

volunteer_tree = ttk.Treeview(volunteer_frame, columns=("Event", "Date", "Hours", "Status"), show='headings')
for col in ("Event", "Date", "Hours", "Status"):
    volunteer_tree.heading(col, text=col)
volunteer_tree.grid(row=5, columnspan=2, pady=10)

# Admin Dashboard
admin_frame = tk.Frame(root)

admin_tree = ttk.Treeview(admin_frame, columns=("ID", "Event", "Date", "Hours"), show='headings')
for col in ("ID", "Event", "Date", "Hours"):
    admin_tree.heading(col, text=col)
admin_tree.pack()

approve_btn = tk.Button(admin_frame, text="Approve", command=lambda: update_status(admin_tree.item(admin_tree.selection())['values'][0], 'Approved'))
approve_btn.pack(pady=5)

reject_btn = tk.Button(admin_frame, text="Reject", command=lambda: update_status(admin_tree.item(admin_tree.selection())['values'][0], 'Rejected'))
reject_btn.pack(pady=5)

# Init DB
create_tables()

root.mainloop()
