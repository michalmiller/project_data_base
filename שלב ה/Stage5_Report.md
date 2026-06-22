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

Accessible from the ADVANCED section. Features a tabbed interface:

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

**Screenshot description:** Procedures screen with two tabs. Team Statistics tab showing results for team 1: Team Name, Country, Sport Type, Total Players=12, Average Score=58.92, Wins=7, etc.

---

## Design Decisions

### Dark Theme
The application uses a modern dark color scheme for reduced eye strain and professional appearance:
- Background: `#1e1e2e`
- Sidebar: `#181825`
- Cards: `#313244`
- Accent (links/highlights): `#89b4fa`
- Success: `#a6e3a1`, Warning: `#f9e2af`, Danger: `#f38ba8`

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
- ✓ 2 programs from Stage 4 (function + procedure) executable from the Procedures screen
- ✓ User-friendly dark-themed interface
- ✓ Clear setup instructions provided
