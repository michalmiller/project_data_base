# Sports Tournament & Clothing Store Database System

## Overview

This project is a relational database system designed for managing sports tournaments, national teams, players, referees, coaches, stadiums, matches, and clothing store employees.

The system integrates sports tournament management with clothing store management.

The project was developed using:

- ERD Plus
- PostgreSQL
- pgAdmin
- SQL
- GitHub

---

# System Description

The database manages:

- National teams
- Players
- Coaches
- Referees
- Matches
- Stadiums
- Match events
- Tournaments
- Clothing stores

The system allows:

- Tournament management
- Match tracking
- Employee management
- Match event tracking
- Data analysis using SQL queries

---

# ERD Diagram

![DSD](images/dsd.png)

---

# DSD Diagram

![ERD](images/erd.png)

---

# Main Entities

## NationalTeam
Stores information about national sports teams.

## MatchTeam
Associative entity connecting matches and national teams.

Each match includes exactly:
- One HOME team
- One AWAY team

## Player
Stores player information including team membership and player score.

## Coach
Stores coach information.

## HasCoach
Associative entity connecting coaches and teams.

Allows:
- Multiple coaches per team
- One coach to coach multiple teams

## Referee
Stores referee information.

## Match
Stores match information.

## MatchEvent
Stores events that occur during matches.

## Stadium
Stores stadium information.

## Tournament
Stores tournament information.

## ClothingStore
Stores clothing store information.

---

# Main Relationships

## Team Relationships

- NationalTeam → Player (1:N)

- NationalTeam ↔ Match (N:N)
Implemented using MATCH_TEAM.

Each match must contain exactly:
- HOME team
- AWAY team

- Coach ↔ NationalTeam (N:N)
Implemented using HAS_COACH.

---

## Match Relationships

- Match → MatchEvent (1:N)

- Match → Referee (N:1)

- Stadium → Match (1:N)

---

## Tournament Relationships

- Tournament → Match (1:N)

- ClothingStore → Tournament (1:N)

---

## Employment Relationships

- ClothingStore → Player (1:N)

- ClothingStore → Coach (1:N)

- ClothingStore → Referee (1:N)

---

# Database Schema

## NationalTeam

- team_id
- team_name
- country
- team_rank
- team_colors
- founded_date
- sport_type
- team_details_json

---

## MatchTeam

- match_id
- team_id
- team_role

---

## Player

- player_id
- first_name
- last_name
- birth_date
- nationality
- position
- height
- jersey_number
- score
- team_id
- store_id

---

## Coach

- coach_id
- first_name
- last_name
- birth_date
- nationality
- years_of_experience
- contract_start_date
- store_id

---

## HasCoach

- coach_id
- team_id

---

## Referee

- referee_id
- first_name
- last_name
- birth_date
- nationality
- certification_level
- years_of_experience
- store_id

---

## Match

- match_id
- match_date
- status
- home_score
- away_score
- attendance
- weather_json
- referee_id
- tournament_id

---

## MatchEvent

- event_id
- event_type
- event_minute
- event_description
- severity_level
- match_id

---

## Stadium

- stadium_id
- stadium_name
- city
- country
- capacity
- build_date
- stadium_type

---

## Tournament

- tournament_id
- season
- start_date
- end_date
- location
- store_id

---

## ClothingStore

- store_id
- store_name
- brand_name
- website
- city
- phone

---

# Data Types Used

The project uses:

- INTEGER
- VARCHAR
- DATE

Fields containing JSON-like information were stored as VARCHAR.

---

# Functional Dependencies and Normalization

## PLAYER

```text
player_id →
first_name,
last_name,
birth_date,
nationality,
position,
height,
jersey_number,
score,
team_id,
store_id
```

Table satisfies 3NF.

---

## MATCH

```text
match_id →
match_date,
status,
home_score,
away_score,
attendance,
referee_id,
tournament_id
```

Table satisfies 3NF.

---

## TOURNAMENT

```text
tournament_id →
season,
start_date,
end_date,
location,
store_id
```

Table satisfies 3NF.

---

# Normalization Summary

All tables were normalized to 3NF to:

- Reduce redundancy
- Prevent anomalies
- Maintain consistency
- Improve integrity

---

# Data Population

Data was inserted according to project requirements.

The database contains sample data for all entities and relationships.

---

# Screenshots

## DSD Diagram

![ERD](images/erd.png)

---

## ERD Diagram

![DSD](images/dsd.png)

---

## PostgreSQL Tables

![Tables](images/tables.png)

---

## Sample Queries

![Queries](images/queries.png)

---

## Data Population

![Population](images/population.png)

---

## Backup

![Backup](images/backup.png)

---

# Submitted Files

- README.md
- ERD Diagram
- DSD Diagram
- SQL Schema
- SQL Insert File
- PostgreSQL Backup
- Screenshots
- GitHub Repository

---

# Backup Documentation

A full PostgreSQL backup was created.

The backup includes:

- Database schema
- Tables
- Relationships
- Constraints
- Required amount of records

The backup supports complete restoration.

---

# Technologies Used

- PostgreSQL
- pgAdmin
- SQL
- ERD Plus
- GitHub

---

# Project Goals

- Design a relational database
- Build normalized schemas
- Manage relationships
- Work with PostgreSQL
- Practice SQL
- Create backups

---

# Summary

This project demonstrates the design and implementation of a relational database system for sports tournament management integrated with clothing store management.

The project includes:

- ERD
- DSD
- Database implementation
- Data population
- Backup
- Documentation
- Normalization
