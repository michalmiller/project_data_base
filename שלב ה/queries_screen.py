"""
Queries screen - runs predefined queries from Stage 2.
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from db_config import execute_query


QUERIES = {
    "Players per Team": {
        "description": "Count the number of players in each national team, "
                       "ordered by player count descending.",
        "sql": """
            SELECT nt.team_id, nt.team_name,
                   COUNT(p.player_id) AS number_of_players
            FROM nationalteam nt
            LEFT JOIN player p ON nt.team_id = p.team_id
            GROUP BY nt.team_id, nt.team_name
            ORDER BY number_of_players DESC
            LIMIT 20
        """
    },
    "Average Attendance by Status": {
        "description": "Compare audience attendance statistics between "
                       "different match statuses (Scheduled/Finished/Cancelled).",
        "sql": """
            SELECT status,
                   ROUND(AVG(attendance::numeric), 0) AS avg_attendance,
                   MIN(attendance::numeric) AS min_attendance,
                   MAX(attendance::numeric) AS max_attendance,
                   COUNT(*) AS total_matches
            FROM match
            GROUP BY status
            ORDER BY avg_attendance DESC
        """
    },
    "Match Events by Type": {
        "description": "Shows which event types (Goal, Yellow Card, Red Card, "
                       "etc.) are most common across all matches.",
        "sql": """
            SELECT event_type, COUNT(*) AS total_events
            FROM matchevent
            GROUP BY event_type
            ORDER BY total_events DESC
        """
    },
    "Referee Match Count": {
        "description": "Finds how many matches each referee has officiated, "
                       "ordered by most active referees.",
        "sql": """
            SELECT r.referee_id,
                   r.first_name || ' ' || r.last_name AS referee_name,
                   r.certification_level,
                   COUNT(m.match_id) AS matches_officiated
            FROM referee r
            LEFT JOIN match m ON r.referee_id = m.referee_id
            GROUP BY r.referee_id, r.first_name, r.last_name,
                     r.certification_level
            ORDER BY matches_officiated DESC
            LIMIT 20
        """
    }
}


class QueriesScreen:
    """Screen for running predefined queries from Stage 2."""

    def __init__(self, parent, colors):
        self.parent = parent
        self.colors = colors
        self.build_ui()

    def build_ui(self):
        c = self.colors

        # Header
        tk.Label(self.parent, text="Queries (Stage 2)",
                 font=("Segoe UI", 18, "bold"),
                 bg=c["bg"], fg=c["warning"]).pack(
            padx=20, pady=(15, 5), anchor="w")
        tk.Label(self.parent, text="Select a query to execute:",
                 font=("Segoe UI", 11),
                 bg=c["bg"], fg=c["text_dim"]).pack(
            padx=20, anchor="w")

        # Query selection
        select_frame = tk.Frame(self.parent, bg=c["bg"])
        select_frame.pack(fill="x", padx=20, pady=10)

        self.query_var = tk.StringVar()
        query_names = list(QUERIES.keys())
        self.query_combo = ttk.Combobox(select_frame,
                                        textvariable=self.query_var,
                                        values=query_names,
                                        state="readonly",
                                        font=("Segoe UI", 11), width=40)
        self.query_combo.pack(side="left", padx=(0, 10))
        self.query_combo.bind("<<ComboboxSelected>>", self.on_query_select)

        tk.Button(select_frame, text="Run Query",
                  font=("Segoe UI", 11, "bold"),
                  bg=c["warning"], fg="#1e1e2e", relief="flat",
                  cursor="hand2", command=self.run_query).pack(side="left")

        # Description
        self.desc_var = tk.StringVar(value="")
        tk.Label(self.parent, textvariable=self.desc_var,
                 font=("Segoe UI", 10, "italic"),
                 bg=c["bg"], fg=c["text_dim"],
                 wraplength=700, justify="left").pack(
            padx=20, pady=5, anchor="w")

        # SQL display
        sql_frame = tk.LabelFrame(self.parent, text="SQL",
                                  font=("Segoe UI", 9),
                                  bg=c["card"], fg=c["text_dim"])
        sql_frame.pack(fill="x", padx=20, pady=5)

        self.sql_text = scrolledtext.ScrolledText(
            sql_frame, height=4, font=("Consolas", 9),
            bg=c["input_bg"], fg=c["text"],
            insertbackground=c["text"], wrap="word")
        self.sql_text.pack(fill="x", padx=5, pady=5)

        # Results treeview
        result_frame = tk.Frame(self.parent, bg=c["bg"])
        result_frame.pack(fill="both", expand=True, padx=20, pady=10)

        style = ttk.Style()
        style.configure("Query.Treeview",
                        background=c["card"],
                        foreground=c["text"],
                        fieldbackground=c["card"],
                        rowheight=26,
                        font=("Segoe UI", 9))
        style.configure("Query.Treeview.Heading",
                        background=c["sidebar"],
                        foreground=c["warning"],
                        font=("Segoe UI", 9, "bold"))

        self.tree = ttk.Treeview(result_frame, show="headings",
                                 style="Query.Treeview")
        vsb = ttk.Scrollbar(result_frame, orient="vertical",
                            command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # Status
        self.status_var = tk.StringVar(value="Select a query and click Run")
        tk.Label(self.parent, textvariable=self.status_var,
                 font=("Segoe UI", 9), bg=c["bg"],
                 fg=c["text_dim"]).pack(padx=20, anchor="w")

    def on_query_select(self, event=None):
        """Update description when query is selected."""
        name = self.query_var.get()
        if name in QUERIES:
            self.desc_var.set(QUERIES[name]["description"])
            self.sql_text.delete("1.0", tk.END)
            self.sql_text.insert("1.0", QUERIES[name]["sql"].strip())

    def run_query(self):
        """Execute the selected query and display results."""
        name = self.query_var.get()
        if not name or name not in QUERIES:
            messagebox.showwarning("Query", "Please select a query first.")
            return

        sql = QUERIES[name]["sql"]

        # Clear previous results
        self.tree.delete(*self.tree.get_children())
        for col in self.tree["columns"]:
            self.tree.heading(col, text="")
        self.tree["columns"] = []

        try:
            rows = execute_query(sql)
            if not rows:
                self.status_var.set("Query returned 0 rows.")
                return

            # Set up columns from result keys
            columns = list(rows[0].keys())
            self.tree["columns"] = columns
            for col in columns:
                display = col.replace("_", " ").title()
                self.tree.heading(col, text=display)
                self.tree.column(col, width=120, minwidth=60)

            # Insert rows
            for row in rows:
                values = [str(row[col]) if row[col] is not None else ""
                          for col in columns]
                self.tree.insert("", "end", values=values)

            self.status_var.set(
                f"Query executed successfully - {len(rows)} rows returned")

        except Exception as e:
            self.status_var.set(f"Error: {e}")
            messagebox.showerror("Query Error", str(e))
