import requests
import random
from datetime import date, timedelta

BASE_URL = "http://127.0.0.1:8000"

FIRST_NAMES = ["Arjun", "Priya", "Rohan", "Ananya", "Vikram", "Sneha", "Karan", "Isha", "Aditya", "Meera"]
LAST_NAMES = ["Sharma", "Patel", "Reddy", "Nair", "Gupta", "Singh", "Rao", "Iyer", "Das", "Mehta"]
DISCIPLINES = ["pistol", "rifle", "air pistol", "air rifle"]

# ---------- Step A: create target designs ----------
target_design_ids = []
designs_to_create = [
    {"name": "Standard 10-Ring Pistol Target", "diameter_cm": 50, "num_rings": 10},
    {"name": "Precision Rifle Target", "diameter_cm": 60, "num_rings": 10},
]

for d in designs_to_create:
    resp = requests.post(f"{BASE_URL}/target-designs", json=d)
    if resp.status_code == 200:
        target_design_ids.append(resp.json()["id"])
        print(f"Created target design: {d['name']} (id={resp.json()['id']})")
    else:
        print(f"Failed to create target design: {resp.text}")

# ---------- Step B: create shooters ----------
shooter_ids = []
NUM_SHOOTERS = 10

for i in range(NUM_SHOOTERS):
    name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
    email = f"shooter{i}_{random.randint(1000,9999)}@example.com"
    join_date = (date(2025, 1, 1) + timedelta(days=random.randint(0, 500))).isoformat()

    resp = requests.post(f"{BASE_URL}/shooters", json={
        "name": name,
        "email": email,
        "join_date": join_date
    })
    if resp.status_code == 200:
        shooter_ids.append(resp.json()["id"])
        print(f"Created shooter: {name} (id={resp.json()['id']})")
    else:
        print(f"Failed to create shooter: {resp.text}")

# ---------- Step C: create sessions (linked to a target design) ----------
session_ids = []
SESSIONS_PER_SHOOTER = 3

for shooter_id in shooter_ids:
    for _ in range(SESSIONS_PER_SHOOTER):
        session_date = (date(2025, 6, 1) + timedelta(days=random.randint(0, 400))).isoformat()
        resp = requests.post(f"{BASE_URL}/sessions", json={
            "shooter_id": shooter_id,
            "target_design_id": random.choice(target_design_ids),
            "date": session_date,
            "discipline": random.choice(DISCIPLINES),
            "notes": "Auto-generated practice session"
        })
        if resp.status_code == 200:
            session_ids.append(resp.json()["id"])
        else:
            print(f"Failed to create session: {resp.text}")

print(f"Created {len(session_ids)} sessions.")

# ---------- Step D: create scores for each session ----------
SCORES_PER_SESSION = 4
total_scores_created = 0

for session_id in session_ids:
    for target_num in range(1, SCORES_PER_SESSION + 1):
        score = round(random.uniform(60, 100), 1)
        resp = requests.post(f"{BASE_URL}/scores", json={
            "session_id": session_id,
            "target_number": target_num,
            "score": score,
            "max_possible_score": 100
        })
        if resp.status_code == 200:
            total_scores_created += 1

print(f"Created {total_scores_created} scores across {len(session_ids)} sessions.")
print(f"Done. Target designs: {len(target_design_ids)}, Shooters: {len(shooter_ids)}, Sessions: {len(session_ids)}, Scores: {total_scores_created}")