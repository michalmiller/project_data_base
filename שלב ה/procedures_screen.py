"""
Procedures & Functions screen - runs programs from Stage 4.
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from db_config import get_connection, execute_query
import psycopg2


class ProceduresScreen:
    """Screen for running stored procedures and functions from Stage 4."""

    def __init__(self, parent, colors):
        self.parent = parent
        self.colors = colors
        self.build_ui()

    def build_ui(self):
        c = self.colors

        # Header
        tk.Label(self.parent, text="Procedures & Functions (Stage 4)",
                 font=("Segoe UI", 18, "bold"),
                 bg=c["bg"], fg=c["success"]).pack(
            padx=20, pady=(15, 5), anchor="w")

        # Notebook for tabs
        style = ttk.Style()
        style.configure("TNotebook", background=c["bg"])
        style.configure("TNotebook.Tab", font=("Segoe UI", 10))

        notebook = ttk.Notebook(self.parent)
        notebook.pack(fill="both", expand=True, padx=20, pady=10)

        # Tab 1: get_team_statistics
        tab1 = tk.Frame(notebook, bg=c["bg"])
        notebook.add(tab1, text="  Team Statistics (Function)  ")
        self._build_team_stats_tab(tab1)

        # Tab 2: update_player_scores
        tab2 = tk.Frame(notebook, bg=c["bg"])
        notebook.add(tab2, text="  Update Player Scores (Procedure)  ")
        self._build_update_scores_tab(tab2)

    def _build_team_stats_tab(self, parent):
        """Build the get_team_statistics function tab."""
        c = self.colors

        # Description
        desc = ("Function: get_team_statistics(team_id)\n"
                "Returns comprehensive statistics for a team including "
                "player count, average score, match results, and coaching info.")
        tk.Label(parent, text=desc, font=("Segoe UI", 10),
                 bg=c["bg"], fg=c["text_dim"], justify="left",
                 wraplength=700).pack(padx=15, pady=10, anchor="w")

        # Input frame
        input_frame = tk.Frame(parent, bg=c["card"], padx=15, pady=10)
        input_frame.pack(fill="x", padx=15, pady=5)

        tk.Label(input_frame, text="Team ID:",
                 font=("Segoe UI", 11), bg=c["card"],
                 fg=c["text"]).pack(side="left", padx=5)
        self.team_id_entry = tk.Entry(input_frame, font=("Segoe UI", 11),
                                      bg=c["input_bg"], fg=c["text"],
                                      insertbackground=c["text"],
                                      relief="flat", width=10)
        self.team_id_entry.pack(side="left", padx=5, ipady=3)
        self.team_id_entry.insert(0, "1")

        tk.Button(input_frame, text="Run Function",
                  font=("Segoe UI", 11, "bold"),
                  bg=c["success"], fg="#1e1e2e", relief="flat",
                  cursor="hand2",
                  command=self.run_team_stats).pack(side="left", padx=15)

        # Available teams hint
        try:
            teams = execute_query(
                "SELECT team_id, team_name FROM nationalteam "
                "ORDER BY team_id LIMIT 10")
            hint = "Available teams: " + ", ".join(
                [f"{t['team_id']}-{t['team_name']}" for t in teams[:5]])
            tk.Label(input_frame, text=hint, font=("Segoe UI", 8),
                     bg=c["card"], fg=c["text_dim"]).pack(
                side="left", padx=10)
        except Exception:
            pass

        # Results
        result_frame = tk.Frame(parent, bg=c["bg"])
        result_frame.pack(fill="both", expand=True, padx=15, pady=5)

        style = ttk.Style()
        style.configure("Proc.Treeview",
                        background=c["card"],
                        foreground=c["text"],
                        fieldbackground=c["card"],
                        rowheight=26,
                        font=("Segoe UI", 10))
        style.configure("Proc.Treeview.Heading",
                        background=c["sidebar"],
                        foreground=c["success"],
                        font=("Segoe UI", 10, "bold"))

        cols = ("stat_category", "stat_name", "stat_value")
        self.stats_tree = ttk.Treeview(result_frame, columns=cols,
                                       show="headings",
                                       style="Proc.Treeview")
        self.stats_tree.heading("stat_category", text="Category")
        self.stats_tree.heading("stat_name", text="Statistic")
        self.stats_tree.heading("stat_value", text="Value")
        self.stats_tree.column("stat_category", width=120)
        self.stats_tree.column("stat_name", width=180)
        self.stats_tree.column("stat_value", width=250)
        self.stats_tree.pack(fill="both", expand=True)

    def _build_update_scores_tab(self, parent):
        """Build the update_player_scores procedure tab."""
        c = self.colors

        # Description
        desc = ("Procedure: update_player_scores(team_id, bonus_points)\n"
                "Updates player scores based on match events and position. "
                "Applies bonus points: Forward 2x, Midfielder 1x, "
                "Defender 0.5x, Goalkeeper 0.3x.")
        tk.Label(parent, text=desc, font=("Segoe UI", 10),
                 bg=c["bg"], fg=c["text_dim"], justify="left",
                 wraplength=700).pack(padx=15, pady=10, anchor="w")

        # Input frame
        input_frame = tk.Frame(parent, bg=c["card"], padx=15, pady=10)
        input_frame.pack(fill="x", padx=15, pady=5)

        tk.Label(input_frame, text="Team ID:",
                 font=("Segoe UI", 11), bg=c["card"],
                 fg=c["text"]).pack(side="left", padx=5)
        self.proc_team_entry = tk.Entry(input_frame, font=("Segoe UI", 11),
                                        bg=c["input_bg"], fg=c["text"],
                                        insertbackground=c["text"],
                                        relief="flat", width=8)
        self.proc_team_entry.pack(side="left", padx=5, ipady=3)
        self.proc_team_entry.insert(0, "1")

        tk.Label(input_frame, text="Bonus Points:",
                 font=("Segoe UI", 11), bg=c["card"],
                 fg=c["text"]).pack(side="left", padx=5)
        self.bonus_entry = tk.Entry(input_frame, font=("Segoe UI", 11),
                                    bg=c["input_bg"], fg=c["text"],
                                    insertbackground=c["text"],
                                    relief="flat", width=5)
        self.bonus_entry.pack(side="left", padx=5, ipady=3)
        self.bonus_entry.insert(0, "5")

        tk.Button(input_frame, text="Run Procedure",
                  font=("Segoe UI", 11, "bold"),
                  bg=c["success"], fg="#1e1e2e", relief="flat",
                  cursor="hand2",
                  command=self.run_update_scores).pack(side="left", padx=15)

        # Output area
        output_frame = tk.Frame(parent, bg=c["bg"])
        output_frame.pack(fill="both", expand=True, padx=15, pady=5)

        tk.Label(output_frame, text="Execution Output:",
                 font=("Segoe UI", 10, "bold"),
                 bg=c["bg"], fg=c["text"]).pack(anchor="w", pady=(0, 5))

        self.proc_output = scrolledtext.ScrolledText(
            output_frame, height=12, font=("Consolas", 9),
            bg=c["card"], fg=c["success"],
            insertbackground=c["text"], wrap="word")
        self.proc_output.pack(fill="both", expand=True)

        # Before/After comparison
        compare_frame = tk.Frame(parent, bg=c["bg"])
        compare_frame.pack(fill="x", padx=15, pady=5)

        tk.Button(compare_frame, text="Show Players (Before/After)",
                  font=("Segoe UI", 10),
                  bg=c["accent"], fg="#1e1e2e", relief="flat",
                  cursor="hand2",
                  command=self.show_players_comparison).pack(side="left")

        self.compare_label = tk.Label(compare_frame, text="",
                                      font=("Segoe UI", 9),
                                      bg=c["bg"], fg=c["text_dim"])
        self.compare_label.pack(side="left", padx=10)

    def run_team_stats(self):
        """Execute get_team_statistics function."""
        team_id = self.team_id_entry.get().strip()
        if not team_id:
            messagebox.showwarning("Input", "Please enter a Team ID.")
            return

        self.stats_tree.delete(*self.stats_tree.get_children())

        try:
            results = execute_query(
                "SELECT * FROM get_team_statistics(%s)", (int(team_id),))

            for row in results:
                self.stats_tree.insert("", "end", values=(
                    row.get("stat_category", ""),
                    row.get("stat_name", ""),
                    row.get("stat_value", "")
                ))

            if not results:
                messagebox.showinfo("Result",
                                    "No statistics returned for this team.")

        except Exception as e:
            messagebox.showerror("Function Error", str(e))

    def run_update_scores(self):
        """Execute update_player_scores procedure."""
        team_id = self.proc_team_entry.get().strip()
        bonus = self.bonus_entry.get().strip()

        if not team_id or not bonus:
            messagebox.showwarning("Input",
                                   "Please enter Team ID and Bonus Points.")
            return

        self.proc_output.delete("1.0", tk.END)

        conn = get_connection()
        conn.autocommit = True
        try:
            cur = conn.cursor()
            cur.execute("CALL update_player_scores(%s, %s)",
                        (int(team_id), int(bonus)))

            # Get notices
            notices = conn.notices
            if notices:
                for notice in notices:
                    clean = notice.replace("NOTICE:  ", "").strip()
                    self.proc_output.insert(tk.END, clean + "\n")
            else:
                self.proc_output.insert(tk.END,
                                        "Procedure executed successfully.\n")
                self.proc_output.insert(tk.END,
                                        "(No NOTICE output captured)\n")

            self.proc_output.insert(tk.END,
                                    "\n--- Execution Complete ---\n")
            self.compare_label.config(
                text=f"Scores updated for team {team_id}")

        except Exception as e:
            self.proc_output.insert(tk.END, f"ERROR: {e}\n")
            messagebox.showerror("Procedure Error", str(e))
        finally:
            conn.close()

    def show_players_comparison(self):
        """Show players from the selected team with current scores."""
        team_id = self.proc_team_entry.get().strip()
        if not team_id:
            messagebox.showwarning("Input", "Please enter a Team ID.")
            return

        try:
            rows = execute_query(
                "SELECT player_id, first_name, last_name, position, score "
                "FROM player WHERE team_id = %s ORDER BY score DESC LIMIT 15",
                (int(team_id),))

            self.proc_output.delete("1.0", tk.END)
            self.proc_output.insert(tk.END,
                                    f"Players for Team {team_id}:\n")
            self.proc_output.insert(tk.END, "-" * 60 + "\n")
            self.proc_output.insert(tk.END,
                                    f"{'ID':<6}{'Name':<25}{'Position':<15}"
                                    f"{'Score':<8}\n")
            self.proc_output.insert(tk.END, "-" * 60 + "\n")

            for row in rows:
                name = f"{row['first_name']} {row['last_name']}"
                self.proc_output.insert(
                    tk.END,
                    f"{row['player_id']:<6}{name:<25}"
                    f"{row['position']:<15}{row['score']:<8}\n")

            self.proc_output.insert(tk.END, "-" * 60 + "\n")
            self.proc_output.insert(tk.END,
                                    f"Total: {len(rows)} players shown\n")

        except Exception as e:
            messagebox.showerror("Error", str(e))
