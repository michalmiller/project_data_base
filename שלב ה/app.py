"""
Sports Tournament & Clothing Store Management System
Main Application - Stage 5
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db_config import get_connection, execute_query, execute_modify
from crud_screen import CRUDScreen
from queries_screen import QueriesScreen
from procedures_screen import ProceduresScreen

# Color scheme - light, clean, modern
COLORS = {
    "bg": "#f0f4f8",
    "sidebar": "#1e3a5f",
    "card": "#ffffff",
    "accent": "#2563eb",
    "accent_hover": "#1d4ed8",
    "text": "#1e293b",
    "text_dim": "#64748b",
    "success": "#16a34a",
    "danger": "#dc2626",
    "warning": "#d97706",
    "input_bg": "#f8fafc",
    "border": "#cbd5e1",
    # sidebar-specific (white text on dark blue background)
    "sidebar_text": "#e2e8f0",
    "sidebar_text_dim": "#94a3b8",
    "sidebar_accent": "#60a5fa",
    "sidebar_hover": "#2d5a8e",
}

# Table definitions with display names and columns
TABLES = {
    "nationalteam": {
        "display": "National Teams",
        "pk": "team_id",
        "columns": ["team_id", "team_name", "country", "team_rank",
                    "team_colors", "founded_date", "sport_type"],
        "labels": ["ID", "Team Name", "Country", "Rank",
                   "Colors", "Founded Date", "Sport Type"],
        "editable": ["team_name", "country", "team_rank",
                     "team_colors", "founded_date", "sport_type"]
    },
    "player": {
        "display": "Players",
        "pk": "player_id",
        "columns": ["player_id", "first_name", "last_name", "birth_date",
                    "nationality", "position", "height", "jersey_number",
                    "score", "team_id", "store_id"],
        "labels": ["ID", "First Name", "Last Name", "Birth Date",
                   "Nationality", "Position", "Height", "Jersey #",
                   "Score", "Team", "Store"],
        "editable": ["first_name", "last_name", "birth_date", "nationality",
                     "position", "height", "jersey_number", "score",
                     "team_id", "store_id"],
        "fk": {"team_id": ("nationalteam", "team_id", "team_name"),
                "store_id": ("clothingstore", "store_id", "store_name")}
    },
    "coach": {
        "display": "Coaches",
        "pk": "coach_id_",
        "columns": ["coach_id_", "first_name", "last_name", "birth_date",
                    "nationality", "years_of_experience", "contract_start_date",
                    "store_id"],
        "labels": ["ID", "First Name", "Last Name", "Birth Date",
                   "Nationality", "Experience (yrs)", "Contract Start",
                   "Store"],
        "editable": ["first_name", "last_name", "birth_date", "nationality",
                     "years_of_experience", "contract_start_date", "store_id"],
        "fk": {"store_id": ("clothingstore", "store_id", "store_name")}
    },
    "referee": {
        "display": "Referees",
        "pk": "referee_id",
        "columns": ["referee_id", "first_name", "last_name", "birth_date",
                    "nationality", "certification_level",
                    "years_of_experience", "store_id"],
        "labels": ["ID", "First Name", "Last Name", "Birth Date",
                   "Nationality", "Certification", "Experience (yrs)",
                   "Store"],
        "editable": ["first_name", "last_name", "birth_date", "nationality",
                     "certification_level", "years_of_experience", "store_id"],
        "fk": {"store_id": ("clothingstore", "store_id", "store_name")}
    },
    "tournament": {
        "display": "Tournaments",
        "pk": "tournament_id",
        "columns": ["tournament_id", "season", "start_date", "end_date",
                    "location", "store_id"],
        "labels": ["ID", "Season", "Start Date", "End Date",
                   "Location", "Store"],
        "editable": ["season", "start_date", "end_date", "location", "store_id"],
        "fk": {"store_id": ("clothingstore", "store_id", "store_name")}
    },
    "match": {
        "display": "Matches",
        "pk": "match_id",
        "columns": ["match_id", "match_date", "status", "home_score",
                    "away_score", "attendance", "referee_id", "tournament_id"],
        "labels": ["ID", "Date", "Status", "Home Score",
                   "Away Score", "Attendance", "Referee", "Tournament"],
        "editable": ["match_date", "status", "home_score", "away_score",
                     "attendance", "referee_id", "tournament_id"],
        "fk": {"referee_id": ("referee", "referee_id", "first_name"),
                "tournament_id": ("tournament", "tournament_id", "location")}
    },
    "stadium": {
        "display": "Stadiums",
        "pk": "stadium_id",
        "columns": ["stadium_id", "stadium_name", "city", "country",
                    "capacity", "build_date", "stadium_type", "match_id"],
        "labels": ["ID", "Name", "City", "Country",
                   "Capacity", "Build Date", "Type", "Match"],
        "editable": ["stadium_name", "city", "country", "capacity",
                     "build_date", "stadium_type", "match_id"]
    },
    "matchevent": {
        "display": "Match Events",
        "pk": "event_id",
        "columns": ["event_id", "event_type", "event_minute",
                    "event_description", "severity_level", "match_id"],
        "labels": ["ID", "Type", "Minute", "Description",
                   "Severity", "Match"],
        "editable": ["event_type", "event_minute", "event_description",
                     "severity_level", "match_id"]
    },
    "clothingstore": {
        "display": "Clothing Stores",
        "pk": "store_id",
        "columns": ["store_id", "store_name", "brand_name", "website",
                    "city", "phone"],
        "labels": ["ID", "Store Name", "Brand", "Website", "City", "Phone"],
        "editable": ["store_name", "brand_name", "website", "city", "phone"]
    },
    "branch": {
        "display": "Branches",
        "pk": "branch_id",
        "columns": ["branch_id", "branch_name", "branch_status",
                    "phone_number", "opening_date", "city_id", "store_id"],
        "labels": ["ID", "Name", "Status", "Phone",
                   "Opening Date", "City", "Store"],
        "editable": ["branch_name", "branch_status", "phone_number",
                     "opening_date", "city_id", "store_id"],
        "fk": {"city_id": ("city", "city_id", "city_name"),
                "store_id": ("clothingstore", "store_id", "store_name")}
    },
    "customer": {
        "display": "Customers",
        "pk": "customer_id",
        "columns": ["customer_id", "first_name", "last_name", "phone_number",
                    "email", "join_date", "customer_status", "city_id"],
        "labels": ["ID", "First Name", "Last Name", "Phone",
                   "Email", "Join Date", "Status", "City"],
        "editable": ["first_name", "last_name", "phone_number", "email",
                     "join_date", "customer_status", "city_id"],
        "fk": {"city_id": ("city", "city_id", "city_name")}
    },
    "employee": {
        "display": "Employees",
        "pk": "employee_id",
        "columns": ["employee_id", "first_name", "last_name", "phone_number",
                    "email", "salary", "role", "hire_date", "branch_id"],
        "labels": ["ID", "First Name", "Last Name", "Phone",
                   "Email", "Salary", "Role", "Hire Date", "Branch"],
        "editable": ["first_name", "last_name", "phone_number", "email",
                     "salary", "role", "hire_date", "branch_id"],
        "fk": {"branch_id": ("branch", "branch_id", "branch_name")}
    },
    "product": {
        "display": "Products",
        "pk": "product_id",
        "columns": ["product_id", "product_name", "brand", "target_audience",
                    "base_price", "product_status", "supplier_id",
                    "season_id", "category_id"],
        "labels": ["ID", "Name", "Brand", "Audience", "Price",
                   "Status", "Supplier", "Season", "Category"],
        "editable": ["product_name", "brand", "target_audience", "base_price",
                     "product_status", "supplier_id", "season_id", "category_id"],
        "fk": {"supplier_id": ("supplier", "supplier_id", "supplier_name"),
                "season_id": ("season", "season_id", "season_name"),
                "category_id": ("category", "category_id", "category_name")}
    },
    "inventory": {
        "display": "Inventory",
        "pk": "inventory_id",
        "columns": ["inventory_id", "quantity_in_stock", "color", "size",
                    "shelf_location", "min_stock_level", "last_restock_date",
                    "branch_id", "product_id"],
        "labels": ["ID", "Quantity", "Color", "Size", "Shelf",
                   "Min Stock", "Last Restock", "Branch", "Product"],
        "editable": ["quantity_in_stock", "color", "size", "shelf_location",
                     "min_stock_level", "last_restock_date", "branch_id",
                     "product_id"],
        "fk": {"branch_id": ("branch", "branch_id", "branch_name"),
                "product_id": ("product", "product_id", "product_name")}
    },
    "sale": {
        "display": "Sales",
        "pk": "sale_id",
        "columns": ["sale_id", "sale_date", "total_amount", "sale_status",
                    "receipt_number", "customer_id", "employee_id",
                    "branch_id", "payment_method_id"],
        "labels": ["ID", "Date", "Amount", "Status", "Receipt",
                   "Customer", "Employee", "Branch", "Payment Method"],
        "editable": ["sale_date", "total_amount", "sale_status",
                     "receipt_number", "customer_id", "employee_id",
                     "branch_id", "payment_method_id"],
        "fk": {"customer_id": ("customer", "customer_id", "first_name"),
                "employee_id": ("employee", "employee_id", "first_name"),
                "branch_id": ("branch", "branch_id", "branch_name"),
                "payment_method_id": ("paymentmethod", "payment_method_id",
                                      "payment_method_name")}
    },
    "supplier": {
        "display": "Suppliers",
        "pk": "supplier_id",
        "columns": ["supplier_id", "supplier_name", "contact_person",
                    "phone_number", "email", "supplier_status",
                    "contract_start_date", "city_id"],
        "labels": ["ID", "Name", "Contact", "Phone", "Email",
                   "Status", "Contract Start", "City"],
        "editable": ["supplier_name", "contact_person", "phone_number",
                     "email", "supplier_status", "contract_start_date", "city_id"],
        "fk": {"city_id": ("city", "city_id", "city_name")}
    },
    "category": {
        "display": "Categories",
        "pk": "category_id",
        "columns": ["category_id", "category_name"],
        "labels": ["ID", "Category Name"],
        "editable": ["category_name"]
    },
    "city": {
        "display": "Cities",
        "pk": "city_id",
        "columns": ["city_id", "city_name"],
        "labels": ["ID", "City Name"],
        "editable": ["city_name"]
    },
    "season": {
        "display": "Seasons",
        "pk": "season_id",
        "columns": ["season_id", "season_name"],
        "labels": ["ID", "Season Name"],
        "editable": ["season_name"]
    },
    "paymentmethod": {
        "display": "Payment Methods",
        "pk": "payment_method_id",
        "columns": ["payment_method_id", "payment_method_name"],
        "labels": ["ID", "Method Name"],
        "editable": ["payment_method_name"]
    }
}


class MainApplication(tk.Tk):
    """Main application window with sidebar navigation."""

    def __init__(self):
        super().__init__()
        self.title("Sports & Store Management System")
        self.geometry("1200x750")
        self.configure(bg=COLORS["bg"])
        self.minsize(1000, 600)

        # Try to connect to DB on startup
        try:
            conn = get_connection()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error",
                                 f"Cannot connect to database:\n{e}\n\n"
                                 "Please check db_config.py settings.")
            self.destroy()
            return

        self.show_login()

    def show_login(self):
        """Show login/welcome screen."""
        self.login_frame = tk.Frame(self, bg=COLORS["bg"])
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Title
        tk.Label(self.login_frame, text="Sports & Store",
                 font=("Segoe UI", 30, "bold"),
                 bg=COLORS["bg"], fg=COLORS["accent"]).pack(pady=(0, 4))
        tk.Label(self.login_frame, text="Management System",
                 font=("Segoe UI", 16),
                 bg=COLORS["bg"], fg=COLORS["text_dim"]).pack(pady=(0, 28))

        # Login card with border
        card = tk.Frame(self.login_frame, bg=COLORS["card"],
                        padx=45, pady=35,
                        highlightbackground=COLORS["border"],
                        highlightthickness=1)
        card.pack()

        tk.Label(card, text="Sign In", font=("Segoe UI", 17, "bold"),
                 bg=COLORS["card"], fg=COLORS["text"]).pack(pady=(0, 22))

        tk.Label(card, text="Username:", font=("Segoe UI", 10),
                 bg=COLORS["card"], fg=COLORS["text_dim"]).pack(anchor="w")
        self.user_entry = tk.Entry(card, font=("Segoe UI", 12),
                                   bg=COLORS["input_bg"], fg=COLORS["text"],
                                   insertbackground=COLORS["text"],
                                   relief="flat", width=25,
                                   highlightbackground=COLORS["border"],
                                   highlightthickness=1)
        self.user_entry.pack(pady=(2, 12), ipady=6)
        self.user_entry.insert(0, "admin")

        tk.Label(card, text="Password:", font=("Segoe UI", 10),
                 bg=COLORS["card"], fg=COLORS["text_dim"]).pack(anchor="w")
        self.pass_entry = tk.Entry(card, font=("Segoe UI", 12), show="*",
                                   bg=COLORS["input_bg"], fg=COLORS["text"],
                                   insertbackground=COLORS["text"],
                                   relief="flat", width=25,
                                   highlightbackground=COLORS["border"],
                                   highlightthickness=1)
        self.pass_entry.pack(pady=(2, 22), ipady=6)
        self.pass_entry.insert(0, "admin")

        btn = tk.Button(card, text="Login", font=("Segoe UI", 12, "bold"),
                        bg=COLORS["accent"], fg="#ffffff",
                        activebackground=COLORS["accent_hover"],
                        activeforeground="#ffffff",
                        relief="flat", cursor="hand2", width=20,
                        command=self.do_login)
        btn.pack(ipady=7)

        self.pass_entry.bind("<Return>", lambda e: self.do_login())

    def do_login(self):
        """Handle login - accepts any credentials (demo)."""
        self.login_frame.destroy()
        self.build_main_ui()

    def build_main_ui(self):
        """Build the main UI with scrollable sidebar and content area."""
        # Sidebar outer container (fixed width)
        sidebar_outer = tk.Frame(self, bg=COLORS["sidebar"], width=220)
        sidebar_outer.pack(side="left", fill="y")
        sidebar_outer.pack_propagate(False)

        # Canvas inside sidebar for scrolling
        self._sidebar_canvas = tk.Canvas(
            sidebar_outer, bg=COLORS["sidebar"],
            highlightthickness=0, width=220)
        sidebar_scroll = ttk.Scrollbar(
            sidebar_outer, orient="vertical",
            command=self._sidebar_canvas.yview)
        self._sidebar_canvas.configure(
            yscrollcommand=sidebar_scroll.set)

        sidebar_scroll.pack(side="right", fill="y")
        self._sidebar_canvas.pack(side="left", fill="both", expand=True)

        # Inner frame that holds all sidebar widgets
        self.sidebar = tk.Frame(self._sidebar_canvas, bg=COLORS["sidebar"])
        self._sidebar_window = self._sidebar_canvas.create_window(
            (0, 0), window=self.sidebar, anchor="nw")

        # Update scroll region when inner frame changes size
        self.sidebar.bind("<Configure>", self._on_sidebar_configure)
        self._sidebar_canvas.bind("<Configure>", self._on_canvas_configure)

        # Mouse-wheel scrolling
        self._sidebar_canvas.bind_all(
            "<MouseWheel>",
            lambda e: self._sidebar_canvas.yview_scroll(
                int(-1 * (e.delta / 120)), "units"))

        # Sidebar header
        tk.Label(self.sidebar, text="Navigation",
                 font=("Segoe UI", 13, "bold"),
                 bg=COLORS["sidebar"], fg=COLORS["sidebar_accent"]).pack(
            pady=(15, 10), padx=15, anchor="w")

        ttk.Separator(self.sidebar, orient="horizontal").pack(
            fill="x", padx=10, pady=5)

        # Sports section
        tk.Label(self.sidebar, text="SPORTS", font=("Segoe UI", 9, "bold"),
                 bg=COLORS["sidebar"], fg=COLORS["sidebar_text_dim"]).pack(
            padx=15, pady=(10, 2), anchor="w")

        sports_tables = ["nationalteam", "player", "coach", "referee",
                         "tournament", "match", "stadium", "matchevent"]
        for tbl in sports_tables:
            self._add_sidebar_btn(tbl)

        ttk.Separator(self.sidebar, orient="horizontal").pack(
            fill="x", padx=10, pady=5)

        # Retail section
        tk.Label(self.sidebar, text="RETAIL", font=("Segoe UI", 9, "bold"),
                 bg=COLORS["sidebar"], fg=COLORS["sidebar_text_dim"]).pack(
            padx=15, pady=(5, 2), anchor="w")

        retail_tables = ["clothingstore", "branch", "customer", "employee",
                         "product", "inventory", "sale", "supplier",
                         "category", "city", "season", "paymentmethod"]
        for tbl in retail_tables:
            self._add_sidebar_btn(tbl)

        ttk.Separator(self.sidebar, orient="horizontal").pack(
            fill="x", padx=10, pady=5)

        # Advanced section
        tk.Label(self.sidebar, text="ADVANCED", font=("Segoe UI", 9, "bold"),
                 bg=COLORS["sidebar"], fg=COLORS["sidebar_text_dim"]).pack(
            padx=15, pady=(5, 2), anchor="w")

        btn_q = tk.Button(self.sidebar, text="Queries (Stage 2)",
                          font=("Segoe UI", 10),
                          bg=COLORS["sidebar"], fg="#fbbf24",
                          activebackground=COLORS["sidebar_hover"],
                          activeforeground="#fbbf24",
                          relief="flat", anchor="w", cursor="hand2",
                          command=self.show_queries)
        btn_q.pack(fill="x", padx=10, pady=1)

        btn_p = tk.Button(self.sidebar, text="Procedures (Stage 4)",
                          font=("Segoe UI", 10),
                          bg=COLORS["sidebar"], fg="#4ade80",
                          activebackground=COLORS["sidebar_hover"],
                          activeforeground="#4ade80",
                          relief="flat", anchor="w", cursor="hand2",
                          command=self.show_procedures)
        btn_p.pack(fill="x", padx=10, pady=(1, 15))

        # Content area
        self.content = tk.Frame(self, bg=COLORS["bg"])
        self.content.pack(side="left", fill="both", expand=True)

        # Show welcome
        self._show_welcome()

    def _on_sidebar_configure(self, event):
        """Update canvas scroll region when sidebar content changes."""
        self._sidebar_canvas.configure(
            scrollregion=self._sidebar_canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Stretch inner frame to fill canvas width."""
        self._sidebar_canvas.itemconfig(
            self._sidebar_window, width=event.width)

    def _add_sidebar_btn(self, table_name):
        """Add a sidebar navigation button for a table."""
        display = TABLES[table_name]["display"]
        btn = tk.Button(self.sidebar, text=f"  {display}",
                        font=("Segoe UI", 10),
                        bg=COLORS["sidebar"], fg=COLORS["sidebar_text"],
                        activebackground=COLORS["sidebar_hover"],
                        activeforeground="#ffffff",
                        relief="flat", anchor="w", cursor="hand2",
                        command=lambda t=table_name: self.show_table(t))
        btn.pack(fill="x", padx=10, pady=1)

    def _clear_content(self):
        """Clear the content area."""
        for widget in self.content.winfo_children():
            widget.destroy()

    def _show_welcome(self):
        """Show welcome screen in content area."""
        self._clear_content()
        frame = tk.Frame(self.content, bg=COLORS["bg"])
        frame.place(relx=0.5, rely=0.4, anchor="center")

        # Icon-like circle placeholder
        tk.Label(frame, text="⚽  🏪",
                 font=("Segoe UI", 36),
                 bg=COLORS["bg"], fg=COLORS["accent"]).pack(pady=(0, 15))

        tk.Label(frame, text="Welcome to the Management System",
                 font=("Segoe UI", 22, "bold"),
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(pady=(0, 8))

        tk.Label(frame,
                 text="Select a table from the sidebar to manage data,\n"
                      "or use the Advanced section for queries and procedures.",
                 font=("Segoe UI", 12),
                 bg=COLORS["bg"], fg=COLORS["text_dim"],
                 justify="center").pack()

        # Quick-access cards row
        cards_frame = tk.Frame(frame, bg=COLORS["bg"])
        cards_frame.pack(pady=25)

        for label, color, cmd in [
            ("Queries", COLORS["warning"], self.show_queries),
            ("Procedures", COLORS["success"], self.show_procedures),
        ]:
            card = tk.Frame(cards_frame, bg=COLORS["card"],
                            padx=20, pady=12,
                            highlightbackground=COLORS["border"],
                            highlightthickness=1)
            card.pack(side="left", padx=10)
            tk.Label(card, text=label, font=("Segoe UI", 11, "bold"),
                     bg=COLORS["card"], fg=color).pack()
            tk.Button(card, text="Open", font=("Segoe UI", 9),
                      bg=color, fg="#ffffff", relief="flat",
                      cursor="hand2", command=cmd,
                      padx=10).pack(pady=(6, 0))

    def show_table(self, table_name):
        """Show CRUD screen for a table."""
        self._clear_content()
        table_def = TABLES[table_name]
        CRUDScreen(self.content, table_name, table_def, COLORS)

    def show_queries(self):
        """Show queries screen."""
        self._clear_content()
        QueriesScreen(self.content, COLORS)

    def show_procedures(self):
        """Show procedures/functions screen."""
        self._clear_content()
        ProceduresScreen(self.content, COLORS)


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
