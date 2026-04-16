import psycopg2
import random

conn = psycopg2.connect(
    host="localhost",
    database="sports_tournament",
    user="postgres",
    password="123456"
)

cur = conn.cursor()

event_types = ["Goal", "Foul", "Yellow Card", "Red Card", "Substitution"]

for i in range(300):  # 300 events
    event_id = i + 1
    match_id = random.randint(1, 100)

    cur.execute("""
        INSERT INTO match_event (
            event_id,
            event_type,
            event_minute,
            event_description,
            match_id
        )
        VALUES (%s, %s, %s, %s, %s)
    """, (
        event_id,
        random.choice(event_types),
        random.randint(1, 90),
        "Random event",
        match_id
    ))

conn.commit()
cur.close()
conn.close()

print("Match events inserted!")