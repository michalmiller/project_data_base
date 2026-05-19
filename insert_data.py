import random
import json
from datetime import date, timedelta

import psycopg2
from faker import Faker

fake = Faker()

conn = psycopg2.connect(
    host="localhost",
    database="sports_tournament",
    user="postgres",
    password="123456",
    port="5432"
)

cur = conn.cursor()


def random_date(start_year, end_year):
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))


def maybe_null(value, chance=0.15):
    return None if random.random() < chance else value


# 1. ClothingStore
for i in range(1, 21):
    cur.execute("""
        INSERT INTO clothingstore
        (store_id, store_name, brand_name, website, city, phone)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (store_id) DO NOTHING;
    """, (
        i,
        fake.company(),
        fake.company_suffix(),
        fake.url(),
        fake.city(),
        fake.phone_number()
    ))


# 2. NationalTeam
for i in range(1, 31):
    details = {
        "level": random.choice(["professional", "semi-professional"]),
        "active": True,
        "sponsor": fake.company()
    }

    cur.execute("""
        INSERT INTO nationalteam
        (team_id, team_name, country, team_rank, team_colors,
         founded_date, sport_type, team_details_json)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (team_id) DO NOTHING;
    """, (
        i,
        f"{fake.country()} Team",
        fake.country(),
        random.randint(1, 100),
        random.choice(["Red-White", "Blue-White", "Green-Yellow", "Black-Red"]),
        random_date(1950, 2020),
        random.choice(["Football", "Basketball", "Volleyball"]),
        json.dumps(details)
    ))


# 3. Player
for i in range(1, 601):
    cur.execute("""
        INSERT INTO player
        (player_id, first_name, last_name, birth_date, nationality,
         position, height, jersey_number, team_id, store_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (player_id) DO NOTHING;
    """, (
        i,
        fake.first_name(),
        fake.last_name(),
        random_date(1980, 2008),
        maybe_null(fake.country()),
        random.choice(["Forward", "Midfielder", "Defender", "Goalkeeper"]),
        random.randint(160, 210),
        random.randint(1, 99),
        random.randint(1, 30),
        random.randint(1, 20)
    ))


# 4. Coach
for i in range(1, 31):
    cur.execute("""
    INSERT INTO coach
    ("coach_id_", "first_name", "last_name", "birth_date", "nationality",
     "years_of_experience", "contract_start_date", "team_id", "store_id")
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT ("coach_id_") DO NOTHING;
""", (
    i,
    fake.first_name(),
    fake.last_name(),
    random_date(1960, 1990),
    fake.country(),
    random.randint(1, 35),
    random_date(2018, 2025),
    i,
    random.randint(1, 20)
))


# 5. Referee
for i in range(1, 101):
    cur.execute("""
        INSERT INTO referee
        (referee_id, first_name, last_name, birth_date, nationality,
         certification_level, years_of_experience, store_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (referee_id) DO NOTHING;
    """, (
        i,
        fake.first_name(),
        fake.last_name(),
        random_date(1970, 2000),
        fake.country(),
        random.choice(["Local", "National", "International"]),
        random.randint(1, 25),
        random.randint(1, 20)
    ))


# 6. Tournament
for i in range(1, 21):
    start = random_date(2020, 2025)
    end = start + timedelta(days=random.randint(7, 60))

    cur.execute("""
        INSERT INTO tournament
        (tournament_id, tournament_name, season, start_date, end_date, location, store_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (tournament_id) DO NOTHING;
    """, (
        i,
        f"{fake.city()} Cup",
        random.choice(["Winter", "Spring", "Summer", "Autumn"]),
        start,
        end,
        fake.city(),
        random.randint(1, 20)
    ))


# 7. Match
for i in range(1, 201):
    weather = {
        "weather": random.choice(["sunny", "rainy", "cloudy", "windy"]),
        "temperature": random.randint(10, 35)
    }

    cur.execute("""
        INSERT INTO match
        (match_id, match_date, status, home_score, away_score,
         attendance, weather_json, referee_id, tournament_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (match_id) DO NOTHING;
    """, (
        i,
        random_date(2020, 2025),
        random.choice(["Scheduled", "Finished", "Cancelled"]),
        random.randint(0, 5),
        random.randint(0, 5),
        random.randint(1000, 60000),  # בלי NULL
        json.dumps(weather),
        random.randint(1, 100),
        random.randint(1, 20)
    ))

# 8. Stadium
for i in range(1, 51):
    cur.execute("""
        INSERT INTO stadium
        (stadium_id, stadium_name, city, country, capacity,
         stadium_type, match_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (stadium_id) DO NOTHING;
    """, (
        i,
        f"{fake.city()} Stadium",
        fake.city(),
        fake.country(),
        random.randint(5000, 90000),
        random.choice(["Open", "Closed", "Olympic"]),
        random.randint(1, 200)
    ))

# 9. MatchEvent
event_types = ["Goal", "Yellow Card", "Red Card", "Substitution", "Foul"]

for i in range(1, 701):
    cur.execute("""
        INSERT INTO matchevent
        (event_id, event_type, event_minute, event_description,
         severity_level, Attribute, match_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (event_id) DO NOTHING;
    """, (
        i,
        random.choice(event_types),
        random.randint(1, 90),
        fake.sentence(), 
        random.choice(["Low", "Medium", "High"]),
        random.randint(1, 10),
        random.randint(1, 200)
    ))

# 10. PlayerStatistics
for i in range(1, 701):
    cur.execute("""
        INSERT INTO playerstatistics
        (stat_id_, stat_date, minutes_played, points_or_goals,
         assists, fouls, yellow_cards, red_cards, player_id, match_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (stat_id_) DO NOTHING;
    """, (
        i,
        random_date(2020, 2025),
        random.randint(0, 90),
        random.randint(0, 5),
        random.randint(0, 4),
        random.randint(0, 8),
        random.randint(0, 2),
        random.randint(0, 1),
        random.randint(1, 600),
        random.randint(1, 200)
    ))

# 11. Plays_In_Match
used_pairs = set()

while len(used_pairs) < 400:
    match_id = random.randint(1, 200)
    team_id = random.randint(1, 30)

    if (match_id, team_id) in used_pairs:
        continue

    used_pairs.add((match_id, team_id))

    cur.execute("""
        INSERT INTO plays_in_match
        (match_id, team_id)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING;
    """, (
        match_id,
        team_id
    ))


conn.commit()
cur.close()
conn.close()

print("Data inserted successfully!")