# Setup & Run Instructions

## Prerequisites

- Python 3.8 or higher
- PostgreSQL with the `integrated_db_stage3` database running
- The database should have all tables from stages 1-4 (including procedures/functions from stage 4)

## Installation

1. Open a terminal in this folder (`שלב ה`)

2. Install the required Python package:
```
pip install psycopg2-binary
```

3. If needed, update the database connection settings in `db_config.py`:
```python
DB_CONFIG = {
    "host": "localhost",
    "database": "integrated_db_stage3",
    "user": "postgres",
    "password": "123456",
    "port": "5432"
}
```

## Running the Application

```
python app.py
```

## Login

- Username: `admin`
- Password: `admin`
- (Any credentials are accepted - this is a demo login screen)

## Features

- **Sidebar navigation** - click any table name to manage its data
- **CRUD operations** - Insert, Update, Delete, Search for every table
- **Foreign key display** - IDs are shown as human-readable names
- **Queries (Stage 2)** - Advanced section with predefined SQL queries
- **Procedures (Stage 4)** - Run get_team_statistics and update_player_scores

## File Structure

| File | Description |
|------|-------------|
| `app.py` | Main application, login screen, navigation |
| `crud_screen.py` | Generic CRUD interface for all tables |
| `queries_screen.py` | Predefined queries from Stage 2 |
| `procedures_screen.py` | Procedures & functions from Stage 4 |
| `db_config.py` | Database connection configuration |
| `requirements.txt` | Python dependencies |
