import sqlite3
import random
from pathlib import Path
from datetime import datetime, timedelta


# ============================================================
# CONFIGURATION
# ============================================================

DB_PATH = Path(__file__).resolve().parent / "caregiver.db"

NUMBER_OF_RECORDS = 50

random.seed(42)


# ============================================================
# DATA
# ============================================================

FIRST_NAMES = [
    "Arun", "Bala", "Kumar", "Ravi", "Suresh",
    "Meena", "Lakshmi", "Anitha", "Priya", "Geetha",
    "Mohan", "Raj", "Selvam", "Vijay", "Devi"
]

LAST_NAMES = [
    "Kumar", "Das", "Singh", "Roy", "Sharma",
    "Borah", "Saikia", "Dutta", "Gogoi", "Nath"
]

REGIONS = [
    "Assam",
    "Arunachal Pradesh",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Tripura",
    "Sikkim"
]

DISTRICTS = [
    "Kamrup",
    "Dibrugarh",
    "Jorhat",
    "Tinsukia",
    "Imphal West",
    "Shillong",
    "Aizawl",
    "Kohima",
    "Agartala",
    "Gangtok"
]

LANGUAGES = [
    "English",
    "Assamese",
    "Bengali",
    "Hindi",
    "Manipuri"
]

RELATIONSHIPS = [
    "Son",
    "Daughter",
    "Spouse",
    "Brother",
    "Sister",
    "Relative"
]


# ============================================================
# CONNECTION
# ============================================================

def get_connection():
    """Create a SQLite connection with a generous timeout so the DB stays usable while the server is running."""
    # Remove stale WAL/SHM files before opening if no server is actively using the DB.
    for suffix in ("-wal", "-shm"):
        stale_file = DB_PATH.with_name(DB_PATH.name + suffix)
        if stale_file.exists():
            try:
                stale_file.unlink()
            except OSError:
                pass

    connection = sqlite3.connect(DB_PATH, timeout=30.0)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 30000")
    connection.execute("PRAGMA journal_mode = WAL")
    return connection


# ============================================================
# RANDOM DATE
# ============================================================

def random_date():

    start = datetime(2024, 1, 1)

    end = datetime.now()

    difference = (end - start).days

    date = start + timedelta(
        days=random.randint(0, difference)
    )

    return date.strftime(
        "%Y-%m-%d"
    )


# ============================================================
# CLEAR DATABASE
# ============================================================

def clear_database():
    """Safely wipe rows while handling SQLite lock contention and WAL state."""
    for attempt in range(3):
        try:
            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute("""
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                AND name NOT LIKE 'sqlite_%'
                ORDER BY name;
            """)

            tables = [row[0] for row in cursor.fetchall()]
            cursor.execute("PRAGMA foreign_keys = OFF")

            for table in reversed(tables):
                cursor.execute(f'DELETE FROM "{table}"')

            cursor.execute("PRAGMA foreign_keys = ON")
            connection.commit()
            connection.close()
            print("✓ Existing data cleared")
            return
        except sqlite3.OperationalError as exc:
            if "locked" not in str(exc).lower():
                raise
            if attempt == 2:
                raise
            print(f"Database busy, retrying clear_database ({attempt + 1}/3)...")

            import time
            time.sleep(2)


# ============================================================
# PATIENTS
# ============================================================

def insert_patients():

    connection = get_connection()

    cursor = connection.cursor()

    ids = []

    for i in range(1, NUMBER_OF_RECORDS + 1):

        diagnosis = random.choice([
            "Normal",
            "Mild Cognitive Impairment",
            "Dementia",
            "Alzheimer Disease",
            "Other"
        ])

        if diagnosis == "Normal":

            stage = "None"
            mmse = round(random.uniform(27, 30), 1)
            cdr = 0.0

        elif diagnosis == "Mild Cognitive Impairment":

            stage = "Mild"
            mmse = round(random.uniform(22, 27), 1)
            cdr = 0.5

        elif diagnosis == "Dementia":

            stage = random.choice([
                "Mild",
                "Moderate"
            ])

            if stage == "Mild":
                mmse = round(random.uniform(18, 24), 1)
                cdr = 1.0
            else:
                mmse = round(random.uniform(10, 18), 1)
                cdr = 2.0

        elif diagnosis == "Alzheimer Disease":

            stage = random.choice([
                "Mild",
                "Moderate",
                "Severe"
            ])

            if stage == "Mild":
                mmse = round(random.uniform(18, 24), 1)
                cdr = 1.0

            elif stage == "Moderate":
                mmse = round(random.uniform(10, 18), 1)
                cdr = 2.0

            else:
                mmse = round(random.uniform(3, 10), 1)
                cdr = 3.0

        else:

            stage = "Mild"
            mmse = round(random.uniform(18, 28), 1)
            cdr = 0.5

        cursor.execute("""
            INSERT INTO patients (
                patient_code,
                first_name,
                last_name,
                date_of_birth,
                gender,
                region,
                district,
                preferred_language,
                diagnosis,
                dementia_stage,
                mmse_score,
                cdr_score
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f"PAT{i:04d}",
            random.choice(FIRST_NAMES),
            random.choice(LAST_NAMES),
            f"{random.randint(1940, 1965)}-"
            f"{random.randint(1,12):02d}-"
            f"{random.randint(1,28):02d}",
            random.choice([
                "Male",
                "Female"
            ]),
            random.choice(REGIONS),
            random.choice(DISTRICTS),
            random.choice(LANGUAGES),
            diagnosis,
            stage,
            mmse,
            cdr
        ))

        ids.append(cursor.lastrowid)

    connection.commit()

    connection.close()

    return ids


# ============================================================
# CAREGIVERS
# ============================================================

def insert_caregivers():

    connection = get_connection()

    cursor = connection.cursor()

    ids = []

    for i in range(1, NUMBER_OF_RECORDS + 1):

        cursor.execute("""
            INSERT INTO caregivers (
                caregiver_code,
                first_name,
                last_name,
                phone,
                email,
                relationship,
                preferred_language
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            f"CG{i:04d}",
            random.choice(FIRST_NAMES),
            random.choice(LAST_NAMES),
            f"+91{random.randint(6000000000, 9999999999)}",
            f"caregiver{i}@mindner.com",
            random.choice(RELATIONSHIPS),
            random.choice(LANGUAGES)
        ))

        ids.append(cursor.lastrowid)

    connection.commit()

    connection.close()

    return ids


# ============================================================
# PATIENT CAREGIVER
# ============================================================

def insert_patient_caregivers(
    patient_ids,
    caregiver_ids
):

    connection = get_connection()

    cursor = connection.cursor()

    for i in range(NUMBER_OF_RECORDS):

        patient_id = patient_ids[i]

        caregiver_id = caregiver_ids[i]

        cursor.execute("""
            INSERT INTO patient_caregivers (
                patient_id,
                caregiver_id,
                is_primary
            )
            VALUES (?, ?, ?)
        """, (
            patient_id,
            caregiver_id,
            1
        ))

    connection.commit()

    connection.close()


# ============================================================
# COGNITIVE GAMES
# ============================================================

def insert_games():

    connection = get_connection()

    cursor = connection.cursor()

    ids = []

    games = [
        "Memory Match",
        "Object Recall",
        "Pattern Finder",
        "Number Memory",
        "Daily Routine",
        "Attention Test",
        "Face Recognition",
        "Festival Memory",
        "Color Match",
        "Focus Challenge"
    ]

    categories = [
        "Memory",
        "Attention",
        "Pattern Recognition",
        "Object Recognition",
        "Routine Recall"
    ]

    for i in range(NUMBER_OF_RECORDS):

        cursor.execute("""
            INSERT INTO cognitive_games (
                game_name,
                game_category,
                description,
                difficulty_level,
                language,
                cultural_theme
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            f"{random.choice(games)} {i+1}",
            random.choice(categories),
            "Cognitive training activity",
            random.randint(1, 5),
            random.choice(LANGUAGES),
            random.choice([
                "Traditional Objects",
                "Family",
                "Nature",
                "Local Food",
                "Indian Festivals"
            ])
        ))

        ids.append(cursor.lastrowid)

    connection.commit()

    connection.close()

    return ids


# ============================================================
# GAME SESSIONS
# ============================================================

def insert_game_sessions(
    patient_ids,
    game_ids
):

    connection = get_connection()

    cursor = connection.cursor()

    ids = []

    for i in range(NUMBER_OF_RECORDS):

        attempted = random.randint(5, 20)

        correct = random.randint(
            2,
            attempted
        )

        accuracy = round(
            correct / attempted * 100,
            2
        )

        cursor.execute("""
            INSERT INTO game_sessions (
                patient_id,
                game_id,
                session_date,
                start_time,
                end_time,
                duration_seconds,
                difficulty_level,
                questions_attempted,
                questions_correct,
                accuracy,
                completed
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            patient_ids[i],
            game_ids[i],
            random_date(),
            "10:00:00",
            "10:10:00",
            random.randint(300, 900),
            random.randint(1, 5),
            attempted,
            correct,
            accuracy,
            random.choice([0, 1])
        ))

        ids.append(cursor.lastrowid)

    connection.commit()

    connection.close()

    return ids


# ============================================================
# COGNITIVE SCORES
# ============================================================

def insert_cognitive_scores(session_ids):

    connection = get_connection()

    cursor = connection.cursor()

    for session_id in session_ids:

        scores = [
            round(random.uniform(40, 100), 2)
            for _ in range(7)
        ]

        overall = round(
            sum(scores) / len(scores),
            2
        )

        cursor.execute("""
            INSERT INTO cognitive_scores (
                session_id,
                memory_score,
                attention_score,
                concentration_score,
                pattern_recognition_score,
                object_recognition_score,
                routine_recall_score,
                emotional_engagement_score,
                overall_score
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            *scores,
            overall
        ))

    connection.commit()

    connection.close()


# ============================================================
# AI ASSESSMENTS
# ============================================================

def insert_ai_assessments(patient_ids):

    connection = get_connection()

    cursor = connection.cursor()

    for patient_id in patient_ids:

        cognitive = round(
            random.uniform(40, 95),
            2
        )

        engagement = round(
            random.uniform(40, 100),
            2
        )

        risk = round(
            (100 - cognitive) / 100,
            3
        )

        if risk < 0.25:
            level = "Low"
        elif risk < 0.50:
            level = "Medium"
        elif risk < 0.75:
            level = "High"
        else:
            level = "Critical"

        cursor.execute("""
            INSERT INTO ai_assessments (
                patient_id,
                assessment_date,
                cognitive_score,
                cognitive_change,
                engagement_score,
                predicted_risk,
                risk_level,
                recommendation,
                model_name,
                model_version
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            patient_id,
            random_date(),
            cognitive,
            round(random.uniform(-10, 10), 2),
            engagement,
            risk,
            level,
            "Continue cognitive monitoring and caregiver engagement.",
            "MINDNER-Cognitive-Risk",
            "1.0"
        ))

    connection.commit()

    connection.close()


# ============================================================
# REMINDERS
# ============================================================

def insert_reminders(patient_ids):

    connection = get_connection()

    cursor = connection.cursor()

    types = [
        "Medication",
        "Hydration",
        "Meal",
        "Exercise",
        "Appointment",
        "Cognitive Game"
    ]

    for patient_id in patient_ids:

        status = random.choice([
            "Pending",
            "Completed",
            "Missed"
        ])

        cursor.execute("""
            INSERT INTO reminders (
                patient_id,
                reminder_type,
                title,
                description,
                scheduled_datetime,
                priority,
                status,
                completed_datetime
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            patient_id,
            random.choice(types),
            "Daily Care Reminder",
            "Complete scheduled daily activity.",
            f"{random_date()} 10:00:00",
            random.choice([
                "Low",
                "Medium",
                "High"
            ]),
            status,
            f"{random_date()} 10:30:00"
            if status == "Completed"
            else None
        ))

    connection.commit()

    connection.close()


# ============================================================
# SYMPTOMS
# ============================================================

def insert_symptoms(patient_ids):

    connection = get_connection()

    cursor = connection.cursor()

    symptoms = [
        "Forgetfulness",
        "Confusion",
        "Anxiety",
        "Agitation",
        "Sleep Difficulty",
        "Mood Change",
        "Disorientation"
    ]

    for patient_id in patient_ids:

        cursor.execute("""
            INSERT INTO symptoms (
                patient_id,
                recorded_datetime,
                symptom_name,
                severity,
                notes,
                recorded_by
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            patient_id,
            f"{random_date()} 09:00:00",
            random.choice(symptoms),
            random.randint(1, 5),
            "Routine observation.",
            "Caregiver"
        ))

    connection.commit()

    connection.close()


# ============================================================
# ALERTS
# ============================================================

def insert_alerts(patient_ids):

    connection = get_connection()

    cursor = connection.cursor()

    for patient_id in patient_ids:

        severity = random.choice([
            "Info",
            "Warning",
            "High",
            "Critical"
        ])

        cursor.execute("""
            INSERT INTO alerts (
                patient_id,
                alert_datetime,
                alert_type,
                severity,
                title,
                message,
                source,
                acknowledged,
                acknowledged_datetime
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            patient_id,
            f"{random_date()} 12:00:00",
            "Cognitive Monitoring",
            severity,
            "Patient Activity Alert",
            "Review recent patient activity.",
            "AI Model",
            random.choice([0, 1]),
            None
        ))

    connection.commit()

    connection.close()


# ============================================================
# DAILY ACTIVITY
# ============================================================

def insert_daily_activity(patient_ids):

    connection = get_connection()

    cursor = connection.cursor()

    for patient_id in patient_ids:

        games = random.randint(0, 5)

        completed = random.randint(0, 8)

        missed = random.randint(0, 3)

        engagement = round(
            random.uniform(40, 100),
            2
        )

        cursor.execute("""
            INSERT INTO daily_activity (
                patient_id,
                activity_date,
                games_played,
                total_game_minutes,
                reminders_completed,
                reminders_missed,
                hydration_events,
                social_interactions,
                physical_activity_minutes,
                overall_engagement_score
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            patient_id,
            random_date(),
            games,
            round(random.uniform(5, 60), 2),
            completed,
            missed,
            random.randint(1, 10),
            random.randint(0, 8),
            round(random.uniform(0, 60), 2),
            engagement
        ))

    connection.commit()

    connection.close()


# ============================================================
# SYNC LOG
# ============================================================

def insert_sync_logs(patient_ids):

    connection = get_connection()

    cursor = connection.cursor()

    for i, patient_id in enumerate(patient_ids):

        cursor.execute("""
            INSERT INTO sync_log (
                device_id,
                patient_id,
                data_type,
                local_timestamp,
                server_timestamp,
                sync_status,
                records_synced
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            f"DEVICE-{i+1:04d}",
            patient_id,
            "Patient Activity",
            f"{random_date()} 10:00:00",
            f"{random_date()} 10:05:00",
            random.choice([
                "Success",
                "Pending",
                "Failed"
            ]),
            random.randint(1, 50)
        ))

    connection.commit()

    connection.close()


# ============================================================
# AI RECOMMENDATIONS
# ============================================================

def insert_recommendations(patient_ids):

    connection = get_connection()

    cursor = connection.cursor()

    recommendations = [
        "Increase memory game difficulty.",
        "Continue current cognitive activity.",
        "Encourage hydration.",
        "Monitor missed reminders.",
        "Encourage social interaction.",
        "Caregiver review recommended."
    ]

    for patient_id in patient_ids:

        cursor.execute("""
            INSERT INTO ai_recommendations (
                patient_id,
                generated_datetime,
                recommendation_type,
                recommendation,
                priority,
                model_name,
                confidence,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            patient_id,
            f"{random_date()} 15:00:00",
            "Cognitive Activity",
            random.choice(recommendations),
            random.choice([
                "Low",
                "Medium",
                "High"
            ]),
            "MINDNER-AI",
            round(random.uniform(0.70, 0.99), 3),
            random.choice([
                "New",
                "Reviewed",
                "Accepted"
            ])
        ))

    connection.commit()

    connection.close()


# ============================================================
# VERIFY DATABASE
# ============================================================

def verify_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name NOT LIKE 'sqlite_%'
        ORDER BY name;
    """)

    tables = [
        row[0]
        for row in cursor.fetchall()
    ]

    print("\n")
    print("=" * 70)
    print("FINAL DATABASE")
    print("=" * 70)

    total = 0

    for table in tables:

        cursor.execute(
            f'SELECT COUNT(*) FROM "{table}"'
        )

        count = cursor.fetchone()[0]

        total += count

        print(
            f"{table:<30} {count:>8}"
        )

    print("-" * 70)

    print(
        f"{'TOTAL RECORDS':<30} {total:>8}"
    )

    print("=" * 70)

    connection.close()


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n")
    print("=" * 70)
    print("MINDNER - DATABASE SEEDING")
    print("=" * 70)

    clear_database()

    patient_ids = insert_patients()

    print("✓ Patients inserted")

    caregiver_ids = insert_caregivers()

    print("✓ Caregivers inserted")

    insert_patient_caregivers(
        patient_ids,
        caregiver_ids
    )

    print("✓ Patient-caregiver relationships inserted")

    game_ids = insert_games()

    print("✓ Cognitive games inserted")

    session_ids = insert_game_sessions(
        patient_ids,
        game_ids
    )

    print("✓ Game sessions inserted")

    insert_cognitive_scores(
        session_ids
    )

    print("✓ Cognitive scores inserted")

    insert_ai_assessments(
        patient_ids
    )

    print("✓ AI assessments inserted")

    insert_reminders(
        patient_ids
    )

    print("✓ Reminders inserted")

    insert_symptoms(
        patient_ids
    )

    print("✓ Symptoms inserted")

    insert_alerts(
        patient_ids
    )

    print("✓ Alerts inserted")

    insert_daily_activity(
        patient_ids
    )

    print("✓ Daily activity inserted")

    insert_sync_logs(
        patient_ids
    )

    print("✓ Sync logs inserted")

    insert_recommendations(
        patient_ids
    )

    print("✓ AI recommendations inserted")

    verify_database()

    print("\n✓ DATABASE READY FOR POWER BI / FASTAPI / FRONTEND")


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()