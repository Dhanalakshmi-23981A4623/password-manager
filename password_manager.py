import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
from cryptography.fernet import Fernet

# Encryption key
KEY_FILE = "secret.key"
DB_FILE = "password_manager.db"

if os.path.exists(KEY_FILE):
    with open(KEY_FILE, "rb") as f:
        key = f.read()
else:
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)

cipher = Fernet(key)

# Database
conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS passwords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    website TEXT NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL
)
""")
conn.commit()


def add_password():
    website = website_entry.get().strip()
    username = username_entry.get().strip()
    password = password_entry.get()

    if not website or not username or not password:
        messagebox.showwarning("Warning", "Please fill in all fields")
        return

    encrypted = cipher.encrypt(password.encode()).decode()

    cur.execute(
        "INSERT INTO passwords (website, username, password) VALUES (?, ?, ?)",
        (website, username, encrypted)
    )
    conn.commit()

    website_entry.delete(0, tk.END)
    username_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)

    show_entries()
    messagebox.showinfo("Success", "Password saved securely")


def show_entries():
    for item in table.get_children():
        table.delete(item)

    cur.execute("SELECT id, website, username FROM passwords")
    for row in cur.fetchall():
        table.insert("", tk.END, values=row)


def view_password():
    selected = table.selection()

    if not selected:
        messagebox.showwarning("Warning", "Select an entry first")
        return

    item_id = table.item(selected[0], "values")[0]

    cur.execute(
        "SELECT website, username, password FROM passwords WHERE id=?",
        (item_id,)
    )
    row = cur.fetchone()

    try:
        password = cipher.decrypt(row[2].encode()).decode()
        messagebox.showinfo(
            "Password Details",
            f"Website: {row[0]}\n"
            f"Username: {row[1]}\n"
            f"Password: {password}"
        )
    except Exception:
        messagebox.showerror("Error", "Unable to decrypt password")


def delete_password():
    selected = table.selection()

    if not selected:
        messagebox.showwarning("Warning", "Select an entry first")
        return

    item_id = table.item(selected[0], "values")[0]

    if messagebox.askyesno("Confirm", "Delete selected entry?"):
        cur.execute("DELETE FROM passwords WHERE id=?", (item_id,))
        conn.commit()
        show_entries()
        messagebox.showinfo("Success", "Entry deleted")


def close_app():
    conn.close()
    root.destroy()


# Main window
root = tk.Tk()
root.title("Password Manager")
root.geometry("700x500")

tk.Label(
    root, text="PASSWORD MANAGER",
    font=("Arial", 18, "bold")
).pack(pady=10)

form = tk.Frame(root)
form.pack(pady=10)

tk.Label(form, text="Website / App").grid(row=0, column=0, padx=5, pady=5)
website_entry = tk.Entry(form, width=30)
website_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(form, text="Username / Email").grid(row=1, column=0, padx=5, pady=5)
username_entry = tk.Entry(form, width=30)
username_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(form, text="Password").grid(row=2, column=0, padx=5, pady=5)
password_entry = tk.Entry(form, width=30, show="*")
password_entry.grid(row=2, column=1, padx=5, pady=5)

tk.Button(form, text="Add Password", command=add_password).grid(
    row=3, column=0, columnspan=2, pady=10
)

table = ttk.Treeview(
    root,
    columns=("ID", "Website", "Username"),
    show="headings"
)
table.heading("ID", text="ID")
table.heading("Website", text="Website / App")
table.heading("Username", text="Username / Email")

table.column("ID", width=50)
table.column("Website", width=250)
table.column("Username", width=250)
table.pack(fill="both", expand=True, padx=15, pady=10)

buttons = tk.Frame(root)
buttons.pack(pady=10)

tk.Button(
    buttons, text="View Password", command=view_password
).pack(side="left", padx=5)

tk.Button(
    buttons, text="Delete Password", command=delete_password
).pack(side="left", padx=5)

show_entries()
root.protocol("WM_DELETE_WINDOW", close_app)
root.mainloop()