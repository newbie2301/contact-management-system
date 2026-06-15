"""
Contact Management System
Built with Python, Tkinter, and SQLite
Author: Fatin Ahmed — SRM KTR
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import re


# ── Database Setup ────────────────────────────────────────────────────────────

def init_db():
    conn = sqlite3.connect("contacts.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT NOT NULL,
            phone   TEXT NOT NULL,
            email   TEXT,
            address TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect("contacts.db")


# ── CRUD Operations ───────────────────────────────────────────────────────────

def add_contact(name, phone, email, address):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO contacts (name, phone, email, address) VALUES (?, ?, ?, ?)",
            (name, phone, email, address)
        )

def get_all_contacts(search=""):
    with get_connection() as conn:
        if search:
            return conn.execute(
                "SELECT * FROM contacts WHERE name LIKE ? OR phone LIKE ? OR email LIKE ? ORDER BY name",
                (f"%{search}%", f"%{search}%", f"%{search}%")
            ).fetchall()
        return conn.execute("SELECT * FROM contacts ORDER BY name").fetchall()

def update_contact(contact_id, name, phone, email, address):
    with get_connection() as conn:
        conn.execute(
            "UPDATE contacts SET name=?, phone=?, email=?, address=? WHERE id=?",
            (name, phone, email, address, contact_id)
        )

def delete_contact(contact_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM contacts WHERE id=?", (contact_id,))


# ── Validation ────────────────────────────────────────────────────────────────

def validate_phone(phone):
    return re.fullmatch(r"[6-9]\d{9}", phone.strip()) is not None

def validate_email(email):
    if not email:
        return True  # email is optional
    return re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email.strip()) is not None


# ── Main Application ──────────────────────────────────────────────────────────

class ContactApp:

    # ── Colors & Fonts ────────────────────────────────────────────────────────
    BG        = "#f0f4f8"
    SIDEBAR   = "#1a1a2e"
    ACCENT    = "#0f3460"
    WHITE     = "#ffffff"
    TEXT      = "#1a1a2e"
    MUTED     = "#666666"
    SUCCESS   = "#2b8a3e"
    DANGER    = "#c0392b"
    ROW_ODD   = "#ffffff"
    ROW_EVEN  = "#eef2f7"

    FONT      = ("Segoe UI", 10)
    FONT_BOLD = ("Segoe UI", 10, "bold")
    FONT_LG   = ("Segoe UI", 13, "bold")
    FONT_XL   = ("Segoe UI", 18, "bold")

    def __init__(self, root):
        self.root = root
        self.root.title("Contact Management System")
        self.root.geometry("950x620")
        self.root.resizable(False, False)
        self.root.configure(bg=self.BG)

        self.selected_id   = None
        self.search_var    = tk.StringVar()
        self.name_var      = tk.StringVar()
        self.phone_var     = tk.StringVar()
        self.email_var     = tk.StringVar()
        self.address_var   = tk.StringVar()

        init_db()
        self._build_ui()
        self.load_contacts()

    # ── UI Builder ────────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Sidebar ──────────────────────────────────────────────────────────
        sidebar = tk.Frame(self.root, bg=self.SIDEBAR, width=280)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # App title
        tk.Label(sidebar, text="📒", font=("Segoe UI", 30),
                 bg=self.SIDEBAR, fg=self.WHITE).pack(pady=(30, 5))
        tk.Label(sidebar, text="Contact Manager", font=self.FONT_XL,
                 bg=self.SIDEBAR, fg=self.WHITE).pack()
        tk.Label(sidebar, text="Store. Search. Manage.",
                 font=("Segoe UI", 9), bg=self.SIDEBAR,
                 fg="#aaaacc").pack(pady=(2, 25))

        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", padx=20)

        # ── Form ─────────────────────────────────────────────────────────────
        form_frame = tk.Frame(sidebar, bg=self.SIDEBAR)
        form_frame.pack(fill="x", padx=20, pady=15)

        fields = [
            ("👤  Full Name *",  self.name_var,    False),
            ("📱  Phone *",      self.phone_var,    False),
            ("✉   Email",        self.email_var,    False),
            ("🏠  Address",      self.address_var,  False),
        ]

        self.entries = {}
        for label_text, var, is_pass in fields:
            tk.Label(form_frame, text=label_text, font=("Segoe UI", 9),
                     bg=self.SIDEBAR, fg="#aaaacc", anchor="w").pack(fill="x", pady=(8, 2))
            entry = tk.Entry(form_frame, textvariable=var, font=self.FONT,
                             bg="#2a2a4e", fg=self.WHITE, insertbackground=self.WHITE,
                             relief="flat", bd=6,
                             show="*" if is_pass else "")
            entry.pack(fill="x", ipady=5)
            self.entries[label_text] = entry

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_frame = tk.Frame(sidebar, bg=self.SIDEBAR)
        btn_frame.pack(fill="x", padx=20, pady=10)

        self._btn(btn_frame, "➕  Add Contact",    self.SUCCESS,  self.add_contact).pack(fill="x", pady=3, ipady=6)
        self._btn(btn_frame, "✏️   Update Contact", self.ACCENT,   self.update_contact).pack(fill="x", pady=3, ipady=6)
        self._btn(btn_frame, "🗑️   Delete Contact", self.DANGER,   self.delete_contact).pack(fill="x", pady=3, ipady=6)
        self._btn(btn_frame, "🔄  Clear Form",      "#555577",     self.clear_form).pack(fill="x", pady=3, ipady=6)

        # ── Main panel ────────────────────────────────────────────────────────
        main = tk.Frame(self.root, bg=self.BG)
        main.pack(side="right", fill="both", expand=True)

        # Header
        header = tk.Frame(main, bg=self.ACCENT, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="All Contacts", font=self.FONT_LG,
                 bg=self.ACCENT, fg=self.WHITE).pack(side="left", padx=20, pady=15)

        # Search bar
        search_frame = tk.Frame(header, bg=self.ACCENT)
        search_frame.pack(side="right", padx=20, pady=12)

        tk.Label(search_frame, text="🔍", font=self.FONT,
                 bg=self.ACCENT, fg=self.WHITE).pack(side="left")
        search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                font=self.FONT, bg="#1a3a6e", fg=self.WHITE,
                                insertbackground=self.WHITE, relief="flat", bd=4, width=22)
        search_entry.pack(side="left", ipady=4, padx=5)
        search_entry.insert(0, "Search name, phone, email...")
        search_entry.bind("<FocusIn>",  lambda e: search_entry.delete(0, "end") if search_entry.get() == "Search name, phone, email..." else None)
        search_entry.bind("<FocusOut>", lambda e: search_entry.insert(0, "Search name, phone, email...") if not search_entry.get() else None)
        self.search_var.trace("w", lambda *a: self.load_contacts())

        # ── Stats bar ─────────────────────────────────────────────────────────
        self.stats_frame = tk.Frame(main, bg="#dce8f5", height=32)
        self.stats_frame.pack(fill="x")
        self.stats_label = tk.Label(self.stats_frame, text="",
                                    font=("Segoe UI", 9), bg="#dce8f5", fg=self.MUTED)
        self.stats_label.pack(side="left", padx=15, pady=6)

        # ── Table ─────────────────────────────────────────────────────────────
        table_frame = tk.Frame(main, bg=self.BG)
        table_frame.pack(fill="both", expand=True, padx=15, pady=10)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                         font=self.FONT, rowheight=32,
                         background=self.WHITE, fieldbackground=self.WHITE,
                         foreground=self.TEXT, borderwidth=0)
        style.configure("Treeview.Heading",
                         font=self.FONT_BOLD, background=self.ACCENT,
                         foreground=self.WHITE, relief="flat", padding=8)
        style.map("Treeview",
                  background=[("selected", self.ACCENT)],
                  foreground=[("selected", self.WHITE)])

        cols = ("ID", "Name", "Phone", "Email", "Address")
        self.tree = ttk.Treeview(table_frame, columns=cols,
                                  show="headings", selectmode="browse")

        col_widths = {"ID": 45, "Name": 160, "Phone": 115, "Email": 180, "Address": 160}
        for col in cols:
            self.tree.heading(col, text=col,
                              command=lambda c=col: self.sort_by(c))
            self.tree.column(col, width=col_widths[col], anchor="w")

        self.tree.tag_configure("odd",  background=self.ROW_ODD)
        self.tree.tag_configure("even", background=self.ROW_EVEN)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical",
                                   command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # ── Footer ────────────────────────────────────────────────────────────
        footer = tk.Frame(main, bg="#d0dce8", height=28)
        footer.pack(fill="x", side="bottom")
        tk.Label(footer, text="Contact Management System  |  Fatin Ahmed  |  SRM KTR",
                 font=("Segoe UI", 8), bg="#d0dce8", fg=self.MUTED).pack(pady=5)

    def _btn(self, parent, text, color, command):
        return tk.Button(parent, text=text, bg=color, fg=self.WHITE,
                         font=self.FONT_BOLD, relief="flat", cursor="hand2",
                         activebackground=color, activeforeground=self.WHITE,
                         command=command)

    # ── Core Methods ──────────────────────────────────────────────────────────

    def load_contacts(self):
        search = self.search_var.get().strip()
        if search == "Search name, phone, email...":
            search = ""

        for row in self.tree.get_children():
            self.tree.delete(row)

        contacts = get_all_contacts(search)
        for i, contact in enumerate(contacts):
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.insert("", "end", values=contact, tags=(tag,))

        total = len(get_all_contacts())
        shown = len(contacts)
        self.stats_label.config(
            text=f"Showing {shown} of {total} contacts" +
                 (f"  •  Search: '{search}'" if search else "")
        )

    def on_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        self.selected_id = values[0]
        self.name_var.set(values[1])
        self.phone_var.set(values[2])
        self.email_var.set(values[3])
        self.address_var.set(values[4])

    def get_form_data(self):
        return (
            self.name_var.get().strip(),
            self.phone_var.get().strip(),
            self.email_var.get().strip(),
            self.address_var.get().strip(),
        )

    def validate(self, name, phone, email):
        if not name:
            messagebox.showerror("Error", "Name is required.")
            return False
        if not phone:
            messagebox.showerror("Error", "Phone number is required.")
            return False
        if not validate_phone(phone):
            messagebox.showerror("Error", "Enter a valid 10-digit Indian mobile number.")
            return False
        if not validate_email(email):
            messagebox.showerror("Error", "Enter a valid email address.")
            return False
        return True

    def add_contact(self):
        name, phone, email, address = self.get_form_data()
        if not self.validate(name, phone, email):
            return
        add_contact(name, phone, email, address)
        self.clear_form()
        self.load_contacts()
        messagebox.showinfo("Success", f"'{name}' added successfully!")

    def update_contact(self):
        if not self.selected_id:
            messagebox.showwarning("Warning", "Please select a contact to update.")
            return
        name, phone, email, address = self.get_form_data()
        if not self.validate(name, phone, email):
            return
        update_contact(self.selected_id, name, phone, email, address)
        self.clear_form()
        self.load_contacts()
        messagebox.showinfo("Success", f"'{name}' updated successfully!")

    def delete_contact(self):
        if not self.selected_id:
            messagebox.showwarning("Warning", "Please select a contact to delete.")
            return
        name = self.name_var.get()
        confirm = messagebox.askyesno("Confirm Delete",
                                       f"Are you sure you want to delete '{name}'?")
        if confirm:
            delete_contact(self.selected_id)
            self.clear_form()
            self.load_contacts()
            messagebox.showinfo("Deleted", f"'{name}' has been deleted.")

    def clear_form(self):
        self.selected_id = None
        self.name_var.set("")
        self.phone_var.set("")
        self.email_var.set("")
        self.address_var.set("")
        self.tree.selection_remove(self.tree.selection())

    def sort_by(self, col):
        """Click column header to sort."""
        data = [(self.tree.set(child, col), child)
                for child in self.tree.get_children("")]
        data.sort()
        for i, (_, child) in enumerate(data):
            self.tree.move(child, "", i)
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.item(child, tags=(tag,))


# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app = ContactApp(root)
    root.mainloop()
