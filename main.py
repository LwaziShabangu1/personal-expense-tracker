import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

DB_FILE = "expenses.db"

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Expense Tracker")
        self.root.geometry("900x600")
        self.root.minsize(760, 500)
        self.root.configure(bg="#f3f6fb")
        self.conn = sqlite3.connect(DB_FILE)
        self.conn.execute("""CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expense_date TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL CHECK(amount > 0)
        )""")
        self.conn.commit()
        self.build_ui()
        self.refresh_expenses()

    def build_ui(self):
        header = tk.Frame(self.root, bg="#17324d", padx=22, pady=18)
        header.pack(fill="x")
        tk.Label(header, text="Personal Expense Tracker", font=("Segoe UI", 20, "bold"),
                 fg="white", bg="#17324d").pack(anchor="w")
        tk.Label(header, text="Record, review, and manage your everyday spending.",
                 font=("Segoe UI", 10), fg="#dce8f5", bg="#17324d").pack(anchor="w", pady=(4, 0))

        content = tk.Frame(self.root, bg="#f3f6fb", padx=18, pady=16)
        content.pack(fill="both", expand=True)
        form = ttk.LabelFrame(content, text="Add an expense", padding=12)
        form.pack(fill="x", pady=(0, 12))

        tk.Label(form, text="Date (YYYY-MM-DD)").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self.date_var = tk.StringVar(value=date.today().isoformat())
        ttk.Entry(form, textvariable=self.date_var, width=18).grid(row=1, column=0, sticky="ew", padx=5)

        tk.Label(form, text="Category").grid(row=0, column=1, sticky="w", padx=5, pady=4)
        self.category_var = tk.StringVar(value="Food")
        ttk.Combobox(form, textvariable=self.category_var,
                     values=["Food", "Transport", "Education", "Bills", "Shopping", "Health", "Entertainment", "Other"],
                     state="readonly", width=18).grid(row=1, column=1, sticky="ew", padx=5)

        tk.Label(form, text="Description").grid(row=0, column=2, sticky="w", padx=5, pady=4)
        self.description_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.description_var, width=28).grid(row=1, column=2, sticky="ew", padx=5)

        tk.Label(form, text="Amount (E)").grid(row=0, column=3, sticky="w", padx=5, pady=4)
        self.amount_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.amount_var, width=14).grid(row=1, column=3, sticky="ew", padx=5)
        ttk.Button(form, text="Add Expense", command=self.add_expense).grid(row=1, column=4, padx=(10, 4))
        for col in range(4):
            form.columnconfigure(col, weight=1)

        summary = tk.Frame(content, bg="#f3f6fb")
        summary.pack(fill="x", pady=(0, 10))
        self.total_label = tk.Label(summary, text="Total expenses: E0.00",
                                    font=("Segoe UI", 12, "bold"), bg="#f3f6fb", fg="#17324d")
        self.total_label.pack(side="left")
        ttk.Button(summary, text="Delete Selected", command=self.delete_selected).pack(side="right")
        ttk.Button(summary, text="Refresh", command=self.refresh_expenses).pack(side="right", padx=8)

        table_frame = ttk.Frame(content)
        table_frame.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(table_frame, columns=("date", "category", "description", "amount"),
                                 show="headings", selectmode="browse")
        for col, label in [("date", "Date"), ("category", "Category"),
                           ("description", "Description"), ("amount", "Amount (E)")]:
            self.tree.heading(col, text=label)
        self.tree.column("date", width=120, anchor="center")
        self.tree.column("category", width=140, anchor="center")
        self.tree.column("description", width=360)
        self.tree.column("amount", width=130, anchor="e")
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        tk.Label(content, text="Your records are saved locally on this computer.",
                 bg="#f3f6fb", fg="#667085", font=("Segoe UI", 9)).pack(anchor="w", pady=(8, 0))

    def add_expense(self):
        expense_date = self.date_var.get().strip()
        category = self.category_var.get().strip()
        description = self.description_var.get().strip()
        amount_text = self.amount_var.get().strip()
        try:
            date.fromisoformat(expense_date)
        except ValueError:
            messagebox.showerror("Invalid date", "Enter a valid date in YYYY-MM-DD format.")
            return
        if not category or not description:
            messagebox.showerror("Missing information", "Please choose a category and enter a description.")
            return
        try:
            amount = float(amount_text)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid amount", "Enter an amount greater than zero, e.g. 25.50.")
            return
        self.conn.execute(
            "INSERT INTO expenses (expense_date, category, description, amount) VALUES (?, ?, ?, ?)",
            (expense_date, category, description, amount))
        self.conn.commit()
        self.description_var.set("")
        self.amount_var.set("")
        self.refresh_expenses()
        messagebox.showinfo("Saved", "Expense added successfully.")

    def refresh_expenses(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        rows = self.conn.execute(
            "SELECT id, expense_date, category, description, amount FROM expenses ORDER BY expense_date DESC, id DESC"
        ).fetchall()
        total = 0.0
        for expense_id, expense_date, category, description, amount in rows:
            total += amount
            self.tree.insert("", "end", iid=str(expense_id),
                             values=(expense_date, category, description, f"{amount:,.2f}"))
        self.total_label.config(text=f"Total expenses: E{total:,.2f}")

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Select an expense to delete.")
            return
        if messagebox.askyesno("Confirm deletion", "Delete the selected expense? This cannot be undone."):
            self.conn.execute("DELETE FROM expenses WHERE id = ?", (int(selected[0]),))
            self.conn.commit()
            self.refresh_expenses()

    def close(self):
        self.conn.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()
