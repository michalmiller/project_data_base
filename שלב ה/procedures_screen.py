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

        tk.Label(self.parent, text="Procedures & Functions (Stage 4)",
                 font=("Segoe UI", 18, "bold"),
                 bg=c["bg"], fg=c["success"]).pack(
            padx=20, pady=(15, 5), anchor="w")

        style = ttk.Style()
        style.configure("TNotebook", background=c["bg"])
        style.configure("TNotebook.Tab", font=("Segoe UI", 10))

        notebook = ttk.Notebook(self.parent)
        notebook.pack(fill="both", expand=True, padx=20, pady=10)

        tab1 = tk.Frame(notebook, bg=c["bg"])
        notebook.add(tab1, text="  Team Statistics (Function)  ")
        self._build_team_stats_tab(tab1)

        tab2 = tk.Frame(notebook, bg=c["bg"])
        notebook.add(tab2, text="  Update Player Scores (Procedure)  ")
        self._build_update_scores_tab(tab2)

        tab3 = tk.Frame(notebook, bg=c["bg"])
        notebook.add(tab3, text="  Store Revenue (Function)  ")
        self._build_store_revenue_tab(tab3)

        tab4 = tk.Frame(notebook, bg=c["bg"])
        notebook.add(tab4, text="  Inventory Restock (Procedure)  ")
        self._build_inventory_restock_tab(tab4)

    # ------------------------------------------------------------------
    # Tab 1 – get_team_statistics
    # ------------------------------------------------------------------

    def _build_team_stats_tab(self, parent):
        c = self.colors
        desc = ("Function: get_team_statistics(team_id)\n"
                "Returns comprehensive statistics for a team including "
                "player count, average score, match results, and coaching info.")
        tk.Label(parent, text=desc, font=("Segoe UI", 10),
                 bg=c["bg"], fg=c["text_dim"], justify="left",
                 wraplength=700).pack(padx=15, pady=10, anchor="w")

        input_frame = tk.Frame(parent, bg=c["card"], padx=15, pady=10)
        input_frame.pack(fill="x", padx=15, pady=5)

        tk.Label(input_frame, text="Team ID:", font=("Segoe UI", 11),
                 bg=c["card"], fg=c["text"]).pack(side="left", padx=5)
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

        try:
            teams = execute_query(
                "SELECT team_id, team_name FROM nationalteam ORDER BY team_id LIMIT 10")
            hint = "Available teams: " + ", ".join(
                [f"{t['team_id']}-{t['team_name']}" for t in teams[:5]])
            tk.Label(input_frame, text=hint, font=("Segoe UI", 8),
                     bg=c["card"], fg=c["text_dim"]).pack(side="left", padx=10)
        except Exception:
            pass

        result_frame = tk.Frame(parent, bg=c["bg"])
        result_frame.pack(fill="both", expand=True, padx=15, pady=5)

        style = ttk.Style()
        style.configure("Proc.Treeview", background=c["card"],
                        foreground=c["text"], fieldbackground=c["card"],
                        rowheight=26, font=("Segoe UI", 10))
        style.configure("Proc.Treeview.Heading", background=c["sidebar"],
                        foreground=c["success"], font=("Segoe UI", 10, "bold"))

        cols = ("stat_category", "stat_name", "stat_value")
        self.stats_tree = ttk.Treeview(result_frame, columns=cols,
                                       show="headings", style="Proc.Treeview")
        self.stats_tree.heading("stat_category", text="Category")
        self.stats_tree.heading("stat_name", text="Statistic")
        self.stats_tree.heading("stat_value", text="Value")
        self.stats_tree.column("stat_category", width=120)
        self.stats_tree.column("stat_name", width=180)
        self.stats_tree.column("stat_value", width=250)
        self.stats_tree.pack(fill="both", expand=True)

    # ------------------------------------------------------------------
    # Tab 2 – update_player_scores
    # ------------------------------------------------------------------

    def _build_update_scores_tab(self, parent):
        c = self.colors
        desc = ("Procedure: update_player_scores(team_id, bonus_points)\n"
                "Updates player scores based on match events and position. "
                "Applies bonus points: Forward 2x, Midfielder 1x, "
                "Defender 0.5x, Goalkeeper 0.3x.")
        tk.Label(parent, text=desc, font=("Segoe UI", 10),
                 bg=c["bg"], fg=c["text_dim"], justify="left",
                 wraplength=700).pack(padx=15, pady=10, anchor="w")

        input_frame = tk.Frame(parent, bg=c["card"], padx=15, pady=10)
        input_frame.pack(fill="x", padx=15, pady=5)

        tk.Label(input_frame, text="Team ID:", font=("Segoe UI", 11),
                 bg=c["card"], fg=c["text"]).pack(side="left", padx=5)
        self.proc_team_entry = tk.Entry(input_frame, font=("Segoe UI", 11),
                                        bg=c["input_bg"], fg=c["text"],
                                        insertbackground=c["text"],
                                        relief="flat", width=8)
        self.proc_team_entry.pack(side="left", padx=5, ipady=3)
        self.proc_team_entry.insert(0, "1")

        tk.Label(input_frame, text="Bonus Points:", font=("Segoe UI", 11),
                 bg=c["card"], fg=c["text"]).pack(side="left", padx=5)
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

    # ------------------------------------------------------------------
    # Tab 3 – calculate_store_revenue
    # ------------------------------------------------------------------

    def _build_store_revenue_tab(self, parent):
        c = self.colors
        desc = ("Function: calculate_store_revenue(store_id)\n"
                "Calculates total revenue for a clothing store across all its "
                "branches. Applies sale-status weights (completed / returned / "
                "pending) and branch-status multipliers (active / new / closing). "
                "Logs each calculation to store_revenue_log and returns a revenue "
                "category: PLATINUM / GOLD / SILVER / BRONZE / NO REVENUE.")
        tk.Label(parent, text=desc, font=("Segoe UI", 10),
                 bg=c["bg"], fg=c["text_dim"], justify="left",
                 wraplength=750).pack(padx=15, pady=10, anchor="w")

        input_frame = tk.Frame(parent, bg=c["card"], padx=15, pady=10)
        input_frame.pack(fill="x", padx=15, pady=5)

        tk.Label(input_frame, text="Store ID:", font=("Segoe UI", 11),
                 bg=c["card"], fg=c["text"]).pack(side="left", padx=5)
        self.revenue_store_entry = tk.Entry(
            input_frame, font=("Segoe UI", 11),
            bg=c["input_bg"], fg=c["text"],
            insertbackground=c["text"], relief="flat", width=8)
        self.revenue_store_entry.pack(side="left", padx=5, ipady=3)
        self.revenue_store_entry.insert(0, "1")

        tk.Button(input_frame, text="Run Function",
                  font=("Segoe UI", 11, "bold"),
                  bg=c["success"], fg="#1e1e2e", relief="flat",
                  cursor="hand2",
                  command=self.run_store_revenue).pack(side="left", padx=15)

        try:
            stores = execute_query(
                "SELECT store_id, store_name FROM clothingstore ORDER BY store_id LIMIT 10")
            hint = "Available stores: " + ", ".join(
                [f"{s['store_id']}-{s['store_name']}" for s in stores[:5]])
            tk.Label(input_frame, text=hint, font=("Segoe UI", 8),
                     bg=c["card"], fg=c["text_dim"]).pack(side="left", padx=10)
        except Exception:
            pass

        result_frame = tk.Frame(parent, bg=c["bg"])
        result_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self.revenue_summary = tk.Label(result_frame, text="",
                                        font=("Segoe UI", 14, "bold"),
                                        bg=c["bg"], fg=c["accent"])
        self.revenue_summary.pack(pady=(5, 2), anchor="w")

        self.revenue_category_label = tk.Label(result_frame, text="",
                                               font=("Segoe UI", 11),
                                               bg=c["bg"], fg=c["warning"])
        self.revenue_category_label.pack(anchor="w")

        tk.Label(result_frame, text="Execution Log (Branch Details):",
                 font=("Segoe UI", 10, "bold"),
                 bg=c["bg"], fg=c["text"]).pack(anchor="w", pady=(10, 3))

        self.revenue_output = scrolledtext.ScrolledText(
            result_frame, height=10, font=("Consolas", 9),
            bg=c["card"], fg=c["success"],
            insertbackground=c["text"], wrap="word")
        self.revenue_output.pack(fill="both", expand=True)

        btn_row = tk.Frame(parent, bg=c["bg"])
        btn_row.pack(fill="x", padx=15, pady=5)
        tk.Button(btn_row, text="View Revenue Log History",
                  font=("Segoe UI", 10),
                  bg=c["accent"], fg="#1e1e2e", relief="flat",
                  cursor="hand2",
                  command=self.show_revenue_log).pack(side="left")

    # ------------------------------------------------------------------
    # Tab 4 – manage_inventory_restock
    # ------------------------------------------------------------------

    def _build_inventory_restock_tab(self, parent):
        c = self.colors
        desc = ("Procedure: manage_inventory_restock(branch_id, restock_multiplier)\n"
                "Scans all inventory items for a branch that are below their minimum "
                "stock level and restocks them automatically. Priority levels: "
                "CRITICAL (deficit ≥50), HIGH (≥20), MEDIUM (≥10), LOW. "
                "Premium categories get smaller restocks; Basic/Essentials get larger ones. "
                "Every action is logged to restock_log.")
        tk.Label(parent, text=desc, font=("Segoe UI", 10),
                 bg=c["bg"], fg=c["text_dim"], justify="left",
                 wraplength=750).pack(padx=15, pady=10, anchor="w")

        input_frame = tk.Frame(parent, bg=c["card"], padx=15, pady=10)
        input_frame.pack(fill="x", padx=15, pady=5)

        tk.Label(input_frame, text="Branch ID:", font=("Segoe UI", 11),
                 bg=c["card"], fg=c["text"]).pack(side="left", padx=5)
        self.restock_branch_entry = tk.Entry(
            input_frame, font=("Segoe UI", 11),
            bg=c["input_bg"], fg=c["text"],
            insertbackground=c["text"], relief="flat", width=8)
        self.restock_branch_entry.pack(side="left", padx=5, ipady=3)
        self.restock_branch_entry.insert(0, "1")

        tk.Label(input_frame, text="Multiplier:", font=("Segoe UI", 11),
                 bg=c["card"], fg=c["text"]).pack(side="left", padx=5)
        self.restock_multiplier_entry = tk.Entry(
            input_frame, font=("Segoe UI", 11),
            bg=c["input_bg"], fg=c["text"],
            insertbackground=c["text"], relief="flat", width=6)
        self.restock_multiplier_entry.pack(side="left", padx=5, ipady=3)
        self.restock_multiplier_entry.insert(0, "1.5")

        tk.Button(input_frame, text="Run Procedure",
                  font=("Segoe UI", 11, "bold"),
                  bg=c["success"], fg="#1e1e2e", relief="flat",
                  cursor="hand2",
                  command=self.run_inventory_restock).pack(side="left", padx=15)

        try:
            branches = execute_query(
                "SELECT branch_id, branch_name FROM branch ORDER BY branch_id LIMIT 10")
            hint = "Available branches: " + ", ".join(
                [f"{b['branch_id']}-{b['branch_name']}" for b in branches[:5]])
            tk.Label(input_frame, text=hint, font=("Segoe UI", 8),
                     bg=c["card"], fg=c["text_dim"]).pack(side="left", padx=10)
        except Exception:
            pass

        output_frame = tk.Frame(parent, bg=c["bg"])
        output_frame.pack(fill="both", expand=True, padx=15, pady=5)

        tk.Label(output_frame, text="Execution Output:",
                 font=("Segoe UI", 10, "bold"),
                 bg=c["bg"], fg=c["text"]).pack(anchor="w", pady=(0, 3))

        self.restock_output = scrolledtext.ScrolledText(
            output_frame, height=12, font=("Consolas", 9),
            bg=c["card"], fg=c["success"],
            insertbackground=c["text"], wrap="word")
        self.restock_output.pack(fill="both", expand=True)

        btn_row = tk.Frame(parent, bg=c["bg"])
        btn_row.pack(fill="x", padx=15, pady=5)

        tk.Button(btn_row, text="Preview Low-Stock Items",
                  font=("Segoe UI", 10),
                  bg=c["accent"], fg="#1e1e2e", relief="flat",
                  cursor="hand2",
                  command=self.preview_low_stock).pack(side="left", padx=(0, 8))

        tk.Button(btn_row, text="View Restock Log",
                  font=("Segoe UI", 10),
                  bg=c["card"], fg=c["text"], relief="flat",
                  cursor="hand2",
                  command=self.show_restock_log).pack(side="left")

        self.restock_status = tk.Label(btn_row, text="",
                                       font=("Segoe UI", 9),
                                       bg=c["bg"], fg=c["text_dim"])
        self.restock_status.pack(side="left", padx=10)

    # ------------------------------------------------------------------
    # Action methods – Tab 1
    # ------------------------------------------------------------------

    def run_team_stats(self):
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
                    row.get("stat_value", "")))
            if not results:
                messagebox.showinfo("Result", "No statistics returned for this team.")
        except Exception as e:
            messagebox.showerror("Function Error", str(e))

    # ------------------------------------------------------------------
    # Action methods – Tab 2
    # ------------------------------------------------------------------

    def run_update_scores(self):
        team_id = self.proc_team_entry.get().strip()
        bonus = self.bonus_entry.get().strip()
        if not team_id or not bonus:
            messagebox.showwarning("Input", "Please enter Team ID and Bonus Points.")
            return
        self.proc_output.delete("1.0", tk.END)
        conn = get_connection()
        conn.autocommit = True
        try:
            cur = conn.cursor()
            cur.execute("CALL update_player_scores(%s, %s)", (int(team_id), int(bonus)))
            notices = conn.notices
            if notices:
                for notice in notices:
                    self.proc_output.insert(tk.END, notice.replace("NOTICE:  ", "").strip() + "\n")
            else:
                self.proc_output.insert(tk.END, "Procedure executed successfully.\n(No NOTICE output captured)\n")
            self.proc_output.insert(tk.END, "\n--- Execution Complete ---\n")
            self.compare_label.config(text=f"Scores updated for team {team_id}")
        except Exception as e:
            self.proc_output.insert(tk.END, f"ERROR: {e}\n")
            messagebox.showerror("Procedure Error", str(e))
        finally:
            conn.close()

    def show_players_comparison(self):
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
            self.proc_output.insert(tk.END, f"Players for Team {team_id}:\n")
            self.proc_output.insert(tk.END, "-" * 60 + "\n")
            self.proc_output.insert(tk.END,
                f"{'ID':<6}{'Name':<25}{'Position':<15}{'Score':<8}\n")
            self.proc_output.insert(tk.END, "-" * 60 + "\n")
            for row in rows:
                name = f"{row['first_name']} {row['last_name']}"
                self.proc_output.insert(
                    tk.END,
                    f"{row['player_id']:<6}{name:<25}{row['position']:<15}{row['score']:<8}\n")
            self.proc_output.insert(tk.END, "-" * 60 + "\n")
            self.proc_output.insert(tk.END, f"Total: {len(rows)} players shown\n")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ------------------------------------------------------------------
    # Action methods – Tab 3
    # ------------------------------------------------------------------

    def run_store_revenue(self):
        store_id = self.revenue_store_entry.get().strip()
        if not store_id:
            messagebox.showwarning("Input", "Please enter a Store ID.")
            return
        self.revenue_output.delete("1.0", tk.END)
        self.revenue_summary.config(text="")
        self.revenue_category_label.config(text="")
        conn = get_connection()
        conn.autocommit = True
        try:
            cur = conn.cursor()
            cur.execute("SELECT calculate_store_revenue(%s)", (int(store_id),))
            result = cur.fetchone()
            total_revenue = result[0] if result else None
            notices = conn.notices
            if notices:
                for notice in notices:
                    self.revenue_output.insert(
                        tk.END, notice.replace("NOTICE:  ", "").strip() + "\n")
            else:
                self.revenue_output.insert(
                    tk.END, "Function executed successfully.\n(No NOTICE output captured)\n")
            self.revenue_output.insert(tk.END, "\n--- Execution Complete ---\n")
            if total_revenue is not None and float(total_revenue) >= 0:
                self.revenue_summary.config(
                    text=f"Total Revenue: ${float(total_revenue):,.2f}")
                rev = float(total_revenue)
                if rev > 100000:
                    cat, color = "PLATINUM", "#b4d0fb"
                elif rev > 50000:
                    cat, color = "GOLD", "#f9e2af"
                elif rev > 20000:
                    cat, color = "SILVER", "#cdd6f4"
                elif rev > 0:
                    cat, color = "BRONZE", "#fab387"
                else:
                    cat, color = "NO REVENUE", "#f38ba8"
                self.revenue_category_label.config(
                    text=f"Revenue Category: {cat}", fg=color)
            else:
                self.revenue_summary.config(
                    text=f"Result: {total_revenue} (check error above)")
        except Exception as e:
            self.revenue_output.insert(tk.END, f"ERROR: {e}\n")
            messagebox.showerror("Function Error", str(e))
        finally:
            conn.close()

    def show_revenue_log(self):
        self.revenue_output.delete("1.0", tk.END)
        try:
            rows = execute_query(
                "SELECT log_id, store_name, total_revenue, branch_count, "
                "revenue_category, calculated_at "
                "FROM store_revenue_log ORDER BY calculated_at DESC LIMIT 10")
            self.revenue_output.insert(tk.END, "Last 10 Revenue Log Entries:\n")
            self.revenue_output.insert(tk.END, "-" * 75 + "\n")
            self.revenue_output.insert(
                tk.END,
                f"{'ID':<6}{'Store':<20}{'Revenue':>14}  "
                f"{'Branches':<10}{'Category':<14}{'Calculated At'}\n")
            self.revenue_output.insert(tk.END, "-" * 75 + "\n")
            for row in rows:
                self.revenue_output.insert(
                    tk.END,
                    f"{row['log_id']:<6}{str(row['store_name']):<20}"
                    f"${float(row['total_revenue']):>13,.2f}  "
                    f"{row['branch_count']:<10}{str(row['revenue_category']):<14}"
                    f"{str(row['calculated_at'])}\n")
            if not rows:
                self.revenue_output.insert(
                    tk.END, "No log entries found. Run the function first.\n")
        except Exception as e:
            self.revenue_output.insert(tk.END, f"ERROR loading log: {e}\n")

    # ------------------------------------------------------------------
    # Action methods – Tab 4
    # ------------------------------------------------------------------

    def run_inventory_restock(self):
        branch_id = self.restock_branch_entry.get().strip()
        multiplier = self.restock_multiplier_entry.get().strip()
        if not branch_id or not multiplier:
            messagebox.showwarning("Input", "Please enter Branch ID and Multiplier.")
            return
        try:
            multiplier_val = float(multiplier)
        except ValueError:
            messagebox.showwarning("Input", "Multiplier must be a number (e.g. 1.5).")
            return
        self.restock_output.delete("1.0", tk.END)
        self.restock_status.config(text="Running...")
        conn = get_connection()
        conn.autocommit = True
        try:
            cur = conn.cursor()
            cur.execute("CALL manage_inventory_restock(%s, %s)",
                        (int(branch_id), multiplier_val))
            notices = conn.notices
            if notices:
                for notice in notices:
                    self.restock_output.insert(
                        tk.END, notice.replace("NOTICE:  ", "").strip() + "\n")
            else:
                self.restock_output.insert(
                    tk.END, "Procedure executed successfully.\n(No NOTICE output captured)\n")
            self.restock_output.insert(tk.END, "\n--- Execution Complete ---\n")
            self.restock_status.config(text=f"Restock completed for branch {branch_id}")
        except Exception as e:
            self.restock_output.insert(tk.END, f"ERROR: {e}\n")
            self.restock_status.config(text="Error occurred")
            messagebox.showerror("Procedure Error", str(e))
        finally:
            conn.close()

    def preview_low_stock(self):
        branch_id = self.restock_branch_entry.get().strip()
        if not branch_id:
            messagebox.showwarning("Input", "Please enter a Branch ID.")
            return
        self.restock_output.delete("1.0", tk.END)
        try:
            rows = execute_query(
                "SELECT i.inventory_id, p.product_name, "
                "i.quantity_in_stock, i.min_stock_level, "
                "(i.min_stock_level - i.quantity_in_stock) AS deficit, "
                "i.color, i.size "
                "FROM inventory i "
                "JOIN product p ON i.product_id = p.product_id "
                "WHERE i.branch_id = %s "
                "  AND i.quantity_in_stock < i.min_stock_level "
                "ORDER BY deficit DESC LIMIT 20",
                (int(branch_id),))
            self.restock_output.insert(
                tk.END, f"Low-stock items for Branch {branch_id} (up to 20):\n")
            self.restock_output.insert(tk.END, "-" * 72 + "\n")
            self.restock_output.insert(
                tk.END,
                f"{'ID':<6}{'Product':<25}{'In Stock':>9}  "
                f"{'Min':>6}  {'Deficit':>8}  {'Color':<12}{'Size'}\n")
            self.restock_output.insert(tk.END, "-" * 72 + "\n")
            for row in rows:
                self.restock_output.insert(
                    tk.END,
                    f"{row['inventory_id']:<6}"
                    f"{str(row['product_name'])[:24]:<25}"
                    f"{row['quantity_in_stock']:>9}  "
                    f"{row['min_stock_level']:>6}  "
                    f"{row['deficit']:>8}  "
                    f"{str(row['color'] or ''):<12}"
                    f"{str(row['size'] or '')}\n")
            if not rows:
                self.restock_output.insert(
                    tk.END, "All items are adequately stocked in this branch.\n")
            else:
                self.restock_output.insert(
                    tk.END, f"\nTotal items needing restock: {len(rows)}\n")
        except Exception as e:
            self.restock_output.insert(tk.END, f"ERROR: {e}\n")

    def show_restock_log(self):
        branch_id = self.restock_branch_entry.get().strip()
        if not branch_id:
            messagebox.showwarning("Input", "Please enter a Branch ID.")
            return
        self.restock_output.delete("1.0", tk.END)
        try:
            rows = execute_query(
                "SELECT log_id, product_name, old_quantity, restock_amount, "
                "new_quantity, restock_priority, restocked_at "
                "FROM restock_log "
                "WHERE branch_id = %s "
                "ORDER BY restocked_at DESC LIMIT 15",
                (int(branch_id),))
            self.restock_output.insert(
                tk.END, f"Restock Log for Branch {branch_id} (last 15):\n")
            self.restock_output.insert(tk.END, "-" * 80 + "\n")
            self.restock_output.insert(
                tk.END,
                f"{'ID':<6}{'Product':<22}{'Old':>6}  {'Added':>6}  "
                f"{'New':>6}  {'Priority':<10}{'Date'}\n")
            self.restock_output.insert(tk.END, "-" * 80 + "\n")
            for row in rows:
                self.restock_output.insert(
                    tk.END,
                    f"{row['log_id']:<6}"
                    f"{str(row['product_name'])[:21]:<22}"
                    f"{row['old_quantity']:>6}  "
                    f"{row['restock_amount']:>6}  "
                    f"{row['new_quantity']:>6}  "
                    f"{str(row['restock_priority']):<10}"
                    f"{str(row['restocked_at'])}\n")
            if not rows:
                self.restock_output.insert(
                    tk.END, "No restock log entries for this branch yet.\n")
        except Exception as e:
            self.restock_output.insert(tk.END, f"ERROR loading log: {e}\n")
