"""
Sprint 1 Starter Code
Volunteer Hours Tracking System
Tech Stack: Python + Tkinter + SQLite

Sprint 1 Goal:
- User registration
- User login
- Database setup
"""

import sqlite3
import tkinter as tk
from tkinter import messagebox
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
        "SELECT role FROM Users WHERE email=? AND password=?",
        (email, hash_password(password))
    )
    user = cursor.fetchone()
    conn.close()

    if user:
        messagebox.showinfo("Login Success", f"Logged in as {user[0]}")
    else:
        messagebox.showerror("Login Failed", "Invalid credentials")

# -------------------- UI --------------------
root = tk.Tk()
root.title("Volunteer Hours Tracking System – Sprint 1")
root.geometry("400x300")

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

# Initialize DB
create_tables()

root.mainloop()

