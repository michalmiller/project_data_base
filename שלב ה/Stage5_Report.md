# Project Report - Stage 5: Graphical User Interface

## Introduction

In this stage, we built a graphical user interface (GUI) application using Python and Tkinter
that connects to the integrated PostgreSQL database (`integrated_db_stage3`). The application
provides full CRUD operations for all tables, runs predefined queries from Stage 2, and
executes stored procedures/functions from Stage 4.

---

## Tools and Technologies

| Tool | Purpose |
|------|---------|
| **Python 3.x** | Programming language |
| **Tkinter** | GUI framework (built into Python) |
| **ttk (themed widgets)** | Modern widget styling |
| **psycopg2** | PostgreSQL database adapter for Python |
| **PostgreSQL 18** | Database server |

### Why Python + Tkinter?

- Tkinter is included with Python, no extra installation needed
- Simple to build cross-platform desktop applications
- psycopg2 provides robust PostgreSQL connectivity
- Easy to create forms, tables (Treeview), and navigation

---

## Application Architecture

```
שלב ה/
├── app.py                  # Main application, login, navigation
├── crud_screen.py          # Generic CRUD screen for any table
├── queries_screen.py       # Predefined queries from Stage 2
├── procedures_screen.py    # Procedures & functions from Stage 4
├── db_config.py            # Database connection configuration
├── requirements.txt        # Python dependencies
├── INSTRUCTIONS.md         # Setup and run instructions
└── Stage5_Report.md        # This report
```

---

## How to Run

1. Install dependency: `pip install psycopg2-binary`
2. Ensure PostgreSQL is running with `integrated_db_stage3` database
3. Run: `python app.py`
4. Login with any credentials (demo mode)

---

## Application Screens

### 1. Login Screen

The application opens with a login screen featuring:
- Dark themed modern UI
- Username and password fields
- "Login" button to enter the system
- Database connectivity check on startup

**Screenshot description:** Dark background with centered login card, "Sports & Store Management System" title, username/password inputs, and blue Login button.

---

### 2. Main Navigation (Sidebar)

After login, the main screen shows:
- **Left sidebar** with all tables organized by category:
  - SPORTS: National Teams, Players, Coaches, Referees, Tournaments, Matches, Stadiums, Match Events
  - RETAIL: Clothing Stores, Branches, Customers, Employees, Products, Inventory, Sales, Suppliers, Categories, Cities, Seasons, Payment Methods
  - ADVANCED: Queries (Stage 2), Procedures (Stage 4)
- **Right content area** that changes based on selection

**Scrollable Sidebar:**
The sidebar contains 20+ items and is taller than the window. It was implemented using a `Canvas` widget with a `Scrollbar` so all items are always reachable:
- Scroll with the **mouse wheel** anywhere over the sidebar
- The inner frame stretches to fill the sidebar width automatically
- ADVANCED section (Queries + Procedures) is always accessible by scrolling down

---

### 3. CRUD Screens (All Tables)

Each table has a unified CRUD interface with:

- **Header** with table name and action buttons (Insert, Update, Delete, Refresh)
- **Search bar** to find records by ID
- **Form fields** for all editable columns
- **Data table (Treeview)** showing all records with column headers
- **Foreign key resolution** - instead of showing IDs, displays human-readable names
  (e.g., "Israel Team" instead of team_id=1)

**CRUD Operations:**
- **Create (Insert):** Fill form fields → click "Insert" → record added
- **Read (Select):** Data loads automatically; use Search to find by ID
- **Update:** Select a row (fields auto-fill) → modify → click "Update"
- **Delete:** Select a row → click "Delete" → confirm → record removed

**Screenshot description:** Table view showing Players with columns: ID, First Name, Last Name, Birth Date, Nationality, Position, Height, Jersey #, Score, Team (showing team name instead of ID), Store (showing store name instead of ID). Form fields above for editing. Green Insert, yellow Update, red Delete buttons.

---

### 4. Queries Screen (Stage 2)

Accessible from the ADVANCED section in the sidebar. Features:
- Dropdown to select from 4 predefined queries
- Description of each query
- SQL code display
- "Run Query" button
- Results displayed in a sortable table

**Available Queries:**

| # | Query | Description |
|---|-------|-------------|
| 1 | Players per Team | Count players in each national team |
| 2 | Average Attendance by Status | Compare attendance stats by match status |
| 3 | Match Events by Type | Most common event types |
| 4 | Referee Match Count | How many matches each referee officiated |

**Screenshot description:** Query screen with dropdown showing "Players per Team" selected, SQL displayed below, and results table showing team names with player counts sorted descending.

---

### 5. Procedures & Functions Screen (Stage 4)

Accessible from the ADVANCED section. Features a **4-tab interface**, one tab per program from Stage 4:

**Tab 1 - Team Statistics (Function):**
- Input: Team ID
- Runs `get_team_statistics(team_id)` function
- Displays results in a 3-column table: Category, Statistic, Value
- Shows hints for available team IDs

**Tab 2 - Update Player Scores (Procedure):**
- Input: Team ID + Bonus Points
- Runs `update_player_scores(team_id, bonus)` procedure
- Displays NOTICE output from the procedure in a console-style text area
- "Show Players" button to view current scores before/after

**Tab 3 - Store Revenue (Function):**
- Input: Store ID
- Runs `calculate_store_revenue(store_id)` function
- Displays the total revenue amount and revenue category (PLATINUM / GOLD / SILVER / BRONZE / NO REVENUE) with color-coded label
- Execution log shows per-branch breakdown (branch name, sale count, revenue, multiplier)
- "View Revenue Log History" button shows the last 10 entries from `store_revenue_log`
- Shows hints for available store IDs

**Tab 4 - Inventory Restock (Procedure):**
- Input: Branch ID + Restock Multiplier (default 1.5)
- Runs `manage_inventory_restock(branch_id, multiplier)` procedure
- Displays full NOTICE output: priority level, product name, deficit, units added, new quantity
- "Preview Low-Stock Items" button shows all items currently below minimum stock before running
- "View Restock Log" button shows the last 15 entries from `restock_log` for the selected branch
- Shows hints for available branch IDs

**Screenshot description:** Procedures screen with four tabs. Store Revenue tab showing Total Revenue: $41,650.50, Category: SILVER, and execution log with branch-level breakdown.

---

## Design Decisions

### Dark Theme
The application was updated to use a modern **light color scheme** for a clean, professional look:
- Background: `#f0f4f8` (light blue-gray)
- Sidebar: `#1e3a5f` (deep navy blue) with white text
- Cards: `#ffffff` (white) with subtle border
- Accent: `#2563eb` (vivid blue)
- Success: `#16a34a` (green), Warning: `#d97706` (amber), Danger: `#dc2626` (red)
- Input fields: `#f8fafc` (near-white) with border highlight

The sidebar uses its own text palette (`sidebar_text`, `sidebar_text_dim`, `sidebar_accent`) so white/light text is readable against the dark navy background, while the content area uses dark text on the light background.

### Generic CRUD Architecture
Instead of writing a separate screen for each of the 20 tables, we built a single `CRUDScreen` class that:
- Receives a table definition (columns, labels, editable fields, foreign keys)
- Dynamically generates the form and table view
- Handles all CRUD operations generically
- Resolves foreign keys to display names automatically

This approach:
- Reduces code duplication (~200 lines handles all 20 tables)
- Makes it easy to add new tables
- Ensures consistent UI across all screens

### Foreign Key Resolution
When displaying data, the application performs JOINs to show human-readable values:
- `team_id = 1` → displays "Israel Team"
- `store_id = 5` → displays "Sport World"
- `branch_id = 3` → displays "Mall Branch"

Results are cached per session for performance.

---

## Tables Accessible from the Application

### Sports System (8 tables)
| Table | Operations |
|-------|-----------|
| nationalteam | Full CRUD |
| player | Full CRUD + FK to team, store |
| coach | Full CRUD + FK to store |
| referee | Full CRUD + FK to store |
| tournament | Full CRUD + FK to store |
| match | Full CRUD + FK to referee, tournament |
| stadium | Full CRUD |
| matchevent | Full CRUD |

### Retail System (12 tables)
| Table | Operations |
|-------|-----------|
| clothingstore | Full CRUD |
| branch | Full CRUD + FK to city, store |
| customer | Full CRUD + FK to city |
| employee | Full CRUD + FK to branch |
| product | Full CRUD + FK to supplier, season, category |
| inventory | Full CRUD + FK to branch, product |
| sale | Full CRUD + FK to customer, employee, branch, payment |
| supplier | Full CRUD + FK to city |
| category | Full CRUD |
| city | Full CRUD |
| season | Full CRUD |
| paymentmethod | Full CRUD |

---

## Summary

The GUI application meets all Stage 5 requirements:
- ✓ Login screen with navigation to all system screens
- ✓ CRUD operations (Create, Read, Update, Delete) for all tables
- ✓ Foreign keys displayed as human-readable names (not IDs)
- ✓ Update by primary key with auto-fill of existing fields
- ✓ 4 queries from Stage 2 accessible from the Queries screen
- ✓ All 4 programs from Stage 4 executable from the Procedures screen:
  - `get_team_statistics` (Function) — Tab 1
  - `update_player_scores` (Procedure) — Tab 2
  - `calculate_store_revenue` (Function) — Tab 3
  - `manage_inventory_restock` (Procedure) — Tab 4
- ✓ Revenue log history and restock log viewable inside the app
- ✓ Low-stock preview before running the restock procedure
- ✓ User-friendly dark-themed interface
- ✓ Clear setup instructions provided

---

## Procedures & Functions – Detailed Reference

### Tab 3: calculate_store_revenue (Function)

| Field | Details |
|-------|---------|
| **Type** | PL/pgSQL Function |
| **Signature** | `calculate_store_revenue(p_store_id INT) RETURNS NUMERIC` |
| **Input** | Store ID |
| **Output** | Total revenue (NUMERIC), revenue category label, per-branch NOTICE log |
| **Side effects** | Inserts a row into `store_revenue_log` |

**Logic summary:**
- Iterates over all branches of the store with an explicit cursor
- For each branch, uses a FOR..IN implicit cursor over its sales
- Applies sale-status weights: completed = 100%, returned = −50%, pending = 30%
- Applies branch-status multiplier: active = 1.1×, new = 1.2×, closing = 0.8×
- Classifies result: PLATINUM (>100 000), GOLD (>50 000), SILVER (>20 000), BRONZE (>0), NO REVENUE

**UI features:**
- "Run Function" → displays total revenue + category with color coding
- Execution log area shows per-branch breakdown from NOTICE messages
- "View Revenue Log History" → reads `store_revenue_log`, shows last 10 runs

---

### Tab 4: manage_inventory_restock (Procedure)

| Field | Details |
|-------|---------|
| **Type** | PL/pgSQL Procedure |
| **Signature** | `manage_inventory_restock(p_branch_id INT, p_restock_multiplier NUMERIC DEFAULT 1.5)` |
| **Input** | Branch ID, restock multiplier |
| **Output** | NOTICE log per item; summary of items restocked and units added |
| **Side effects** | UPDATEs `inventory.quantity_in_stock`, INSERTs rows into `restock_log` |

**Logic summary:**
- Opens an explicit cursor ordered by deficit (most critical first)
- Priority levels: CRITICAL (deficit ≥ 50), HIGH (≥ 20), MEDIUM (≥ 10), LOW
- Restock formula: `deficit × multiplier × priority_factor`
- Category adjustment: Premium/Luxury → 0.6× ; Basic/Essentials → 1.3×
- Safety cap: stops after 500 iterations

**UI features:**
- "Preview Low-Stock Items" → shows current under-stocked items before running
- "Run Procedure" → calls the procedure and displays full NOTICE output
- "View Restock Log" → reads `restock_log` for the branch, shows last 15 entries
