# Sports Tournament & Clothing Store Database System

## Overview

This project is a relational database system designed for managing sports tournaments, matches, teams, players, referees, coaches, and clothing store employees.

The system combines sports tournament management with a clothing store management concept, where:
- Players work for clothing stores
- Coaches work for clothing stores
- Referees work for clothing stores
- Clothing stores organize tournaments

The project was designed and implemented using:
- ERD Plus
- PostgreSQL
- pgAdmin
- SQL
- Python
- CSV / Excel files
- Mockaroo / GenerateData

---

# System Description

The system manages:

- National teams
- Players
- Coaches
- Referees
- Matches
- Stadiums
- Match events
- Player statistics
- Tournaments
- Clothing stores

The database allows:
- Tracking matches and results
- Managing tournaments
- Recording match events
- Storing player statistics
- Managing employee relationships
- Organizing tournaments through clothing stores

---

# ERD Diagram

![ERD](images/erd.png)

---

# DSD Diagram

![DSD](images/dsd.png)

---

# Main Entities

## NationalTeam
Stores information about national sports teams.

## Player
Stores player information including team membership and clothing store employment.

## Coach
Stores coach information and employment details.

## Referee
Stores referee information and certification details.

## Match
Stores match information including scores, attendance, and status.

## MatchEvent
Stores events occurring during matches.

## PlayerStatistics
Stores statistical information about player performance during matches.

## Stadium
Stores stadium information.

## Tournament
Stores tournament information.

## ClothingStore
Stores clothing store information and employee relationships.

---

# Main Relationships

## Team Relationships
- A national team has many players (1:N)
- A national team has one coach (1:1)
- National teams participate in matches (N:N)

## Match Relationships
- A match includes many events (1:N)
- A match contains player statistics (1:N)
- A match is officiated by one referee (N:1)
- A match is played in one stadium (N:1)

## Tournament Relationships
- A tournament includes many matches (1:N)
- A clothing store organizes tournaments (1:N)

## Employment Relationships
- A clothing store employs players (1:N)
- A clothing store employs coaches (1:N)
- A clothing store employs referees (1:N)

---

# Database Schema (DSD)

## NationalTeam
- team_id (PK)
- team_name
- country
- team_rank
- team_colors
- founded_date
- sport_type
- team_details_json

## Player
- player_id (PK)
- first_name
- last_name
- birth_date
- nationality
- position
- height
- jersey_number
- team_id (FK)
- store_id (FK)

## Coach
- coach_id (PK)
- first_name
- last_name
- birth_date
- nationality
- years_of_experience
- contract_start_date
- team_id (FK)
- store_id (FK)

## Referee
- referee_id (PK)
- first_name
- last_name
- birth_date
- nationality
- certification_level
- years_of_experience
- store_id (FK)

## Match
- match_id (PK)
- match_date
- status
- home_score
- away_score
- attendance
- weather_json
- referee_id (FK)
- tournament_id (FK)

## MatchEvent
- event_id (PK)
- event_type
- event_minute
- event_description
- severity_level
- match_id (FK)

## PlayerStatistics
- stat_id (PK)
- stat_date
- minutes_played
- points_or_goals
- assists
- fouls
- yellow_cards
- red_cards
- player_id (FK)
- match_id (FK)

## Stadium
- stadium_id (PK)
- stadium_name
- city
- country
- capacity
- build_date
- stadium_type
- match_id (FK)

## Tournament
- tournament_id (PK)
- tournament_name
- season
- start_date
- end_date
- location
- store_id (FK)

## ClothingStore
- store_id (PK)
- store_name
- brand_name
- website
- city
- phone

---

# Data Types Used

The project uses multiple data types:
- INTEGER
- VARCHAR
- DATE
- JSON

JSON fields:
- weather_json
- team_details_json

Date fields:
- match_date
- birth_date
- founded_date
- contract_start_date
- start_date
- end_date

---

# Functional Dependencies and Normalization

## Example – PLAYER Table

Functional Dependency:

```text
player_id → first_name, last_name, birth_date, nationality,
position, height, jersey_number, team_id, store_id
```

Since all non-key attributes depend only on the primary key,
the table satisfies 3NF.

---

## Example – MATCH Table

```text
match_id → match_date, status, home_score,
away_score, attendance, referee_id, tournament_id
```

All non-key attributes depend only on the primary key.

Therefore, the table satisfies 3NF.

---

## Example – TOURNAMENT Table

```text
tournament_id → tournament_name, season,
start_date, end_date, location, store_id
```

The table satisfies 3NF because there are no transitive dependencies.

---

## Normalization Summary

All tables were normalized to 3NF / BCNF in order to:
- Reduce redundancy
- Prevent update anomalies
- Maintain data consistency
- Improve database integrity

---

# Data Population

Data was inserted using multiple methods:

## 1. Python Scripts
Python scripts were used to generate random data and JSON values.

## 2. Mockaroo / GenerateData
External websites were used to generate realistic data for:
- Players
- Coaches
- Referees
- Matches

## 3. CSV / Excel Files
CSV files were imported into PostgreSQL tables.

---

# Data Population Screenshots

## ERD Creation

![ERD](images/erd.png)

## DSD Creation

![DSD](images/dsd.png)

## Data Insertion Example

![Insert Data](images/insert_data.png)

---

# Backup Documentation

A full PostgreSQL backup was created using pgAdmin.

The backup includes:
- Database schema
- Tables
- Relationships
- Constraints
- Data records

The backup allows complete restoration of the system.

## Backup Screenshot

![Backup](images/backup.png)

---

# Technologies Used

- PostgreSQL
- pgAdmin
- ERD Plus
- Python
- SQL
- GitHub

---

# Project Goals

The main goals of the project were:
- Designing a relational database
- Building a normalized schema
- Managing relationships between entities
- Practicing SQL and PostgreSQL
- Working with ERD and DSD diagrams
- Creating backups and restoring databases

---

# Summary

This project demonstrates the design and implementation of a complete relational database system for sports tournament management integrated with clothing store employee management.

The project includes:
- ERD design
- Relational schema design
- Database implementation
- Data population
- Backup creation
- Documentation
- Normalization analysis