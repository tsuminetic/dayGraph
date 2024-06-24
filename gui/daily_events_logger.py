# daily_events_logger.py

import sqlite3
import tkinter as tk
from tkinter import messagebox
import datetime

# Database setup
conn = sqlite3.connect('daily_events.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY,
    date TEXT NOT NULL,
    value INTEGER NOT NULL,
    description TEXT NOT NULL
)
''')
conn.commit()
conn.close()

# Function to add event to the database
def add_event():
    date = entry_date.get()
    value = entry_value.get()
    description = entry_description.get()

    try:
        datetime.datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        messagebox.showerror("Invalid date format", "Please enter the date in YYYY-MM-DD format.")
        return

    try:
        value = int(value)
    except ValueError:
        messagebox.showerror("Invalid value", "Please enter an integer value.")
        return

    conn = sqlite3.connect('daily_events.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO events (date, value, description) VALUES (?, ?, ?)', (date, value, description))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", "Event added successfully!")
    entry_date.delete(0, tk.END)
    entry_value.delete(0, tk.END)
    entry_description.delete(0, tk.END)

# GUI setup
root = tk.Tk()
root.title("Daily Events Logger")

tk.Label(root, text="Date (YYYY-MM-DD):").grid(row=0, column=0)
entry_date = tk.Entry(root)
entry_date.grid(row=0, column=1)

tk.Label(root, text="Value:").grid(row=1, column=0)
entry_value = tk.Entry(root)
entry_value.grid(row=1, column=1)

tk.Label(root, text="Description:").grid(row=2, column=0)
entry_description = tk.Entry(root)
entry_description.grid(row=2, column=1)

submit_button = tk.Button(root, text="Add Event", command=add_event)
submit_button.grid(row=3, columnspan=2)

root.mainloop()
