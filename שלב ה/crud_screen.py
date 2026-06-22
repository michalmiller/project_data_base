"""
Generic CRUD screen for any table.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from db_config import execute_query, execute_modify


class CRUDScreen:
    """A reusable CRUD interface for any database table."""

    def __init__(self, parent, table_name, table_def, colors):
        self.parent = parent
        self.table_name = table_name
        self.table_def = table_def
        self.colors = colors
        self.entries = {}
        self.fk_cache = {}

        self.build_ui()
        self.load_data()

    def build_ui(self):
        """Build the CRUD interface."""
        c = self.colors

        # Header
        header = tk.Frame(self.parent, bg=c["bg"])
        header.pack(fill="x", padx=20, pady=(15, 5))

        tk.Label(header, text=self.table_def["display"],
                 font=("Segoe UI", 18, "bold"),
                 bg=c["bg"], fg=c["accent"]).pack(side="left")

        # Buttons frame
        btn_frame = tk.Frame(header, bg=c["bg"])
        btn_frame.pack(side="right")

        tk.Button(btn_frame, text="+ Insert", font=("Segoe UI", 10),
                  bg=c["success"], fg="#1e1e2e", relief="flat",
                  cursor="hand2", command=self.insert_record).pack(
            side="left", padx=3)
        tk.Button(btn_frame, text="Update", font=("Segoe UI", 10),
                  bg=c["warning"], fg="#1e1e2e", relief="flat",
                  cursor="hand2", command=self.update_record).pack(
            side="left", padx=3)
        tk.Button(btn_frame, text="Delete", font=("Segoe UI", 10),
                  bg=c["danger"], fg="#1e1e2e", relief="flat",
                  cursor="hand2", command=self.delete_record).pack(
            side="left", padx=3)
        tk.Button(btn_frame, text="Refresh", font=("Segoe UI", 10),
                  bg=c["card"], fg=c["text"], relief="flat",
                  cursor="hand2", command=self.load_data).pack(
            side="left", padx=3)

        # Search frame
        search_frame = tk.Frame(self.parent, bg=c["bg"])
        search_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(search_frame, text="Search by ID:",
                 font=("Segoe UI", 10), bg=c["bg"],
                 fg=c["text_dim"]).pack(side="left")
        self.search_entry = tk.Entry(search_frame, font=("Segoe UI", 10),
                                     bg=c["input_bg"], fg=c["text"],
                                     insertbackground=c["text"],
                                     relief="flat", width=15)
        self.search_entry.pack(side="left", padx=5, ipady=3)
        tk.Button(search_frame, text="Find", font=("Segoe UI", 9),
                  bg=c["accent"], fg="#1e1e2e", relief="flat",
                  cursor="hand2", command=self.search_by_id).pack(
            side="left", padx=3)
        tk.Button(search_frame, text="Show All", font=("Segoe UI", 9),
                  bg=c["card"], fg=c["text"], relief="flat",
                  cursor="hand2", command=self.load_data).pack(
            side="left", padx=3)

        # Form frame for input fields
        form_frame = tk.Frame(self.parent, bg=c["card"], padx=15, pady=10)
        form_frame.pack(fill="x", padx=20, pady=5)

        editable = self.table_def.get("editable", [])
        col_count = min(4, len(editable))
        for i, col in enumerate(editable):
            row = i // col_count
            col_idx = i % col_count
            label_text = self._get_label(col)

            tk.Label(form_frame, text=label_text + ":",
                     font=("Segoe UI", 9), bg=c["card"],
                     fg=c["text_dim"]).grid(
                row=row, column=col_idx * 2, padx=5, pady=3, sticky="e")

            entry = tk.Entry(form_frame, font=("Segoe UI", 10),
                             bg=c["input_bg"], fg=c["text"],
                             insertbackground=c["text"],
                             relief="flat", width=18)
            entry.grid(row=row, column=col_idx * 2 + 1,
                       padx=5, pady=3, sticky="w", ipady=2)
            self.entries[col] = entry

        # Treeview for data display
        tree_frame = tk.Frame(self.parent, bg=c["bg"])
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Configure style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview",
                        background=c["card"],
                        foreground=c["text"],
                        fieldbackground=c["card"],
                        rowheight=28,
                        font=("Segoe UI", 9))
        style.configure("Custom.Treeview.Heading",
                        background=c["sidebar"],
                        foreground=c["accent"],
                        font=("Segoe UI", 9, "bold"))
        style.map("Custom.Treeview",
                  background=[("selected", c["accent"])],
                  foreground=[("selected", "#1e1e2e")])

        columns = self.table_def["columns"]
        labels = self.table_def["labels"]

        self.tree = ttk.Treeview(tree_frame, columns=columns,
                                 show="headings", style="Custom.Treeview")

        for col, lbl in zip(columns, labels):
            self.tree.heading(col, text=lbl)
            width = 60 if "id" in col.lower() else 120
            self.tree.column(col, width=width, minwidth=50)

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical",
                            command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal",
                            command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set,
                            xscrollcommand=hsb.set)

        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")

        # Bind selection
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(self.parent, textvariable=self.status_var,
                 font=("Segoe UI", 9), bg=c["bg"],
                 fg=c["text_dim"]).pack(padx=20, anchor="w")

    def _get_label(self, col_name):
        """Get display label for a column."""
        columns = self.table_def["columns"]
        labels = self.table_def["labels"]
        if col_name in columns:
            idx = columns.index(col_name)
            return labels[idx]
        return col_name.replace("_", " ").title()

    def _resolve_fk(self, col_name, value):
        """Resolve foreign key value to display name."""
        fk_map = self.table_def.get("fk", {})
        if col_name in fk_map and value is not None:
            ref_table, ref_pk, ref_display = fk_map[col_name]
            cache_key = f"{ref_table}_{value}"
            if cache_key in self.fk_cache:
                return self.fk_cache[cache_key]
            try:
                result = execute_query(
                    f"SELECT {ref_display} FROM {ref_table} "
                    f"WHERE {ref_pk} = %s", (value,))
                if result:
                    display_val = str(result[0][ref_display])
                    self.fk_cache[cache_key] = display_val
                    return display_val
            except Exception:
                pass
        return str(value) if value is not None else ""

    def load_data(self):
        """Load all records from the table."""
        self.tree.delete(*self.tree.get_children())
        self.fk_cache = {}
        try:
            columns = self.table_def["columns"]
            query = f"SELECT {', '.join(columns)} FROM {self.table_name} ORDER BY {self.table_def['pk']} LIMIT 200"
            rows = execute_query(query)

            fk_map = self.table_def.get("fk", {})
            for row in rows:
                values = []
                for col in columns:
                    val = row[col]
                    if col in fk_map:
                        display = self._resolve_fk(col, val)
                        values.append(display)
                    else:
                        values.append(str(val) if val is not None else "")
                self.tree.insert("", "end", values=values,
                                 tags=(str(row[self.table_def["pk"]]),))

            self.status_var.set(f"Loaded {len(rows)} records")
        except Exception as e:
            self.status_var.set(f"Error: {e}")
            messagebox.showerror("Load Error", str(e))

    def on_select(self, event):
        """Fill form fields when a row is selected."""
        sel = self.tree.selection()
        if not sel:
            return
        item = self.tree.item(sel[0])
        values = item["values"]
        columns = self.table_def["columns"]

        # We need to get the raw data (with IDs, not FK names)
        pk_col = self.table_def["pk"]
        pk_idx = columns.index(pk_col)
        pk_val = item["tags"][0] if item["tags"] else values[pk_idx]

        try:
            row = execute_query(
                f"SELECT * FROM {self.table_name} WHERE {pk_col} = %s",
                (pk_val,))
            if row:
                row = row[0]
                for col, entry in self.entries.items():
                    entry.delete(0, tk.END)
                    val = row.get(col, "")
                    entry.insert(0, str(val) if val is not None else "")
        except Exception:
            # Fallback: use displayed values
            editable = self.table_def.get("editable", [])
            for col in editable:
                if col in columns:
                    idx = columns.index(col)
                    if idx < len(values):
                        self.entries[col].delete(0, tk.END)
                        self.entries[col].insert(0, str(values[idx]))

    def search_by_id(self):
        """Search for a record by primary key."""
        pk_val = self.search_entry.get().strip()
        if not pk_val:
            messagebox.showwarning("Search", "Please enter an ID to search.")
            return

        self.tree.delete(*self.tree.get_children())
        pk_col = self.table_def["pk"]
        columns = self.table_def["columns"]

        try:
            query = f"SELECT {', '.join(columns)} FROM {self.table_name} WHERE {pk_col} = %s"
            rows = execute_query(query, (pk_val,))
            fk_map = self.table_def.get("fk", {})

            for row in rows:
                values = []
                for col in columns:
                    val = row[col]
                    if col in fk_map:
                        values.append(self._resolve_fk(col, val))
                    else:
                        values.append(str(val) if val is not None else "")
                self.tree.insert("", "end", values=values,
                                 tags=(str(row[pk_col]),))

            if rows:
                self.status_var.set(f"Found {len(rows)} record(s)")
                # Auto-fill form
                row = rows[0]
                for col, entry in self.entries.items():
                    entry.delete(0, tk.END)
                    val = row.get(col, "")
                    entry.insert(0, str(val) if val is not None else "")
            else:
                self.status_var.set("No record found with that ID")
        except Exception as e:
            messagebox.showerror("Search Error", str(e))

    def _get_form_values(self):
        """Get values from form entries."""
        values = {}
        for col, entry in self.entries.items():
            val = entry.get().strip()
            if val == "" or val.lower() == "none":
                values[col] = None
            else:
                values[col] = val
        return values

    def insert_record(self):
        """Insert a new record."""
        values = self._get_form_values()
        editable = self.table_def.get("editable", [])

        # Check required fields (at least first field)
        if not any(values.get(col) for col in editable[:2]):
            messagebox.showwarning("Insert",
                                   "Please fill in at least the main fields.")
            return

        cols = [col for col in editable if values.get(col) is not None]
        placeholders = ["%s"] * len(cols)
        vals = [values[col] for col in cols]

        query = (f"INSERT INTO {self.table_name} ({', '.join(cols)}) "
                 f"VALUES ({', '.join(placeholders)})")
        try:
            execute_modify(query, vals)
            self.status_var.set("Record inserted successfully!")
            messagebox.showinfo("Success", "Record inserted successfully!")
            self.load_data()
        except Exception as e:
            messagebox.showerror("Insert Error", str(e))

    def update_record(self):
        """Update the selected record."""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Update",
                                   "Please select a record to update,\n"
                                   "or search by ID first.")
            return

        item = self.tree.item(sel[0])
        pk_val = item["tags"][0] if item["tags"] else None
        if not pk_val:
            messagebox.showwarning("Update", "Cannot determine record ID.")
            return

        values = self._get_form_values()
        editable = self.table_def.get("editable", [])
        pk_col = self.table_def["pk"]

        set_clauses = []
        params = []
        for col in editable:
            set_clauses.append(f"{col} = %s")
            params.append(values.get(col))
        params.append(pk_val)

        query = (f"UPDATE {self.table_name} "
                 f"SET {', '.join(set_clauses)} "
                 f"WHERE {pk_col} = %s")
        try:
            execute_modify(query, params)
            self.status_var.set("Record updated successfully!")
            messagebox.showinfo("Success", "Record updated successfully!")
            self.load_data()
        except Exception as e:
            messagebox.showerror("Update Error", str(e))

    def delete_record(self):
        """Delete the selected record."""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Delete",
                                   "Please select a record to delete.")
            return

        item = self.tree.item(sel[0])
        pk_val = item["tags"][0] if item["tags"] else None
        if not pk_val:
            messagebox.showwarning("Delete", "Cannot determine record ID.")
            return

        pk_col = self.table_def["pk"]
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete record with "
            f"{pk_col} = {pk_val}?")

        if not confirm:
            return

        query = f"DELETE FROM {self.table_name} WHERE {pk_col} = %s"
        try:
            execute_modify(query, (pk_val,))
            self.status_var.set("Record deleted successfully!")
            messagebox.showinfo("Success", "Record deleted!")
            self.load_data()
        except Exception as e:
            messagebox.showerror("Delete Error",
                                 f"Cannot delete: {e}\n\n"
                                 "This may be due to foreign key constraints.")
