"""Centralized parameterized SQL queries for Mindner Caregiver Platform."""

# =====================================================================
# PATIENTS
# =====================================================================

GET_ALL_PATIENTS = """
SELECT id, first_name, last_name, age, gender, stage, baseline_score, diagnosis_date, notes, created_at, updated_at
FROM patients
ORDER BY id ASC;
"""

GET_PATIENT_BY_ID = """
SELECT id, first_name, last_name, age, gender, stage, baseline_score, diagnosis_date, notes, created_at, updated_at
FROM patients
WHERE id = ?;
"""

INSERT_PATIENT = """
INSERT INTO patients (first_name, last_name, age, gender, stage, baseline_score, diagnosis_date, notes)
VALUES (?, ?, ?, ?, ?, ?, ?, ?);
"""

UPDATE_PATIENT = """
UPDATE patients
SET first_name = ?, last_name = ?, age = ?, gender = ?, stage = ?, baseline_score = ?, diagnosis_date = ?, notes = ?, updated_at = datetime('now', 'utc')
WHERE id = ?;
"""

DELETE_PATIENT = """
DELETE FROM patients
WHERE id = ?;
"""

# =====================================================================
# CAREGIVERS & RELATIONSHIPS
# =====================================================================

GET_ALL_CAREGIVERS = """
SELECT id, first_name, last_name, email, phone, relation, created_at, updated_at
FROM caregivers
ORDER BY id ASC;
"""

GET_CAREGIVER_BY_ID = """
SELECT id, first_name, last_name, email, phone, relation, created_at, updated_at
FROM caregivers
WHERE id = ?;
"""

INSERT_CAREGIVER = """
INSERT INTO caregivers (first_name, last_name, email, phone, relation)
VALUES (?, ?, ?, ?, ?);
"""

UPDATE_CAREGIVER = """
UPDATE caregivers
SET first_name = ?, last_name = ?, email = ?, phone = ?, relation = ?, updated_at = datetime('now', 'utc')
WHERE id = ?;
"""

LINK_PATIENT_CAREGIVER = """
INSERT OR REPLACE INTO patient_caregivers (patient_id, caregiver_id, relationship_type, is_primary)
VALUES (?, ?, ?, ?);
"""

GET_PATIENT_CAREGIVERS = """
SELECT c.id, c.first_name, c.last_name, c.email, c.phone, c.relation, pc.relationship_type, pc.is_primary
FROM caregivers c
JOIN patient_caregivers pc ON c.id = pc.caregiver_id
WHERE pc.patient_id = ?;
"""

GET_CAREGIVER_PATIENTS = """
SELECT p.id, p.first_name, p.last_name, p.age, p.gender, p.stage, p.baseline_score, pc.relationship_type, pc.is_primary
FROM patients p
JOIN patient_caregivers pc ON p.id = pc.patient_id
WHERE pc.caregiver_id = ?;
"""

# =====================================================================
# COGNITIVE GAMES & SESSIONS
# =====================================================================

GET_ALL_GAMES = """
SELECT id, game_key, name, category, description, max_level, is_active, created_at
FROM cognitive_games
WHERE is_active = 1
ORDER BY id ASC;
"""

GET_GAME_BY_KEY = """
SELECT id, game_key, name, category, description, max_level, is_active, created_at
FROM cognitive_games
WHERE game_key = ?;
"""

GET_GAME_BY_ID = """
SELECT id, game_key, name, category, description, max_level, is_active, created_at
FROM cognitive_games
WHERE id = ?;
"""

INSERT_GAME = """
INSERT INTO cognitive_games (game_key, name, category, description, max_level, is_active)
VALUES (?, ?, ?, ?, ?, ?);
"""

INSERT_GAME_SESSION = """
INSERT INTO game_sessions (patient_id, game_id, level, duration_seconds, status, score, accuracy_percentage, reaction_time_ms, device_info, session_timestamp)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

GET_PATIENT_SESSIONS = """
SELECT s.id, s.patient_id, s.game_id, g.game_key, g.name as game_name, g.category, s.level, s.duration_seconds, s.status, s.score, s.accuracy_percentage, s.reaction_time_ms, s.device_info, s.session_timestamp, s.created_at
FROM game_sessions s
JOIN cognitive_games g ON s.game_id = g.id
WHERE s.patient_id = ?
ORDER BY s.session_timestamp DESC
LIMIT ? OFFSET ?;
"""

# =====================================================================
# COGNITIVE SCORES & ANALYTICS
# =====================================================================

INSERT_COGNITIVE_SCORE = """
INSERT INTO cognitive_scores (patient_id, session_id, domain, score_value, baseline_deviation, calculation_details)
VALUES (?, ?, ?, ?, ?, ?);
"""

GET_PATIENT_SCORES = """
SELECT id, patient_id, session_id, domain, score_value, baseline_deviation, calculation_details, recorded_at
FROM cognitive_scores
WHERE patient_id = ?
ORDER BY recorded_at DESC;
"""

GET_DOMAIN_AVERAGES_BY_PATIENT = """
SELECT domain, AVG(score_value) as avg_score, COUNT(*) as score_count, MIN(score_value) as min_score, MAX(score_value) as max_score
FROM cognitive_scores
WHERE patient_id = ?
GROUP BY domain;
"""

# =====================================================================
# AI ASSESSMENTS & RECOMMENDATIONS
# =====================================================================

INSERT_AI_ASSESSMENT = """
INSERT INTO ai_assessments (patient_id, assessment_date, summary, risk_level, cognitive_trend, confidence_score, raw_insights)
VALUES (?, ?, ?, ?, ?, ?, ?);
"""

GET_PATIENT_ASSESSMENTS = """
SELECT id, patient_id, assessment_date, summary, risk_level, cognitive_trend, confidence_score, raw_insights, created_at
FROM ai_assessments
WHERE patient_id = ?
ORDER BY assessment_date DESC;
"""

INSERT_AI_RECOMMENDATION = """
INSERT INTO ai_recommendations (patient_id, assessment_id, title, description, category, priority, status)
VALUES (?, ?, ?, ?, ?, ?, ?);
"""

GET_PATIENT_RECOMMENDATIONS = """
SELECT id, patient_id, assessment_id, title, description, category, priority, status, created_at
FROM ai_recommendations
WHERE patient_id = ? AND (status = ? OR ? IS NULL)
ORDER BY created_at DESC;
"""

UPDATE_RECOMMENDATION_STATUS = """
UPDATE ai_recommendations
SET status = ?
WHERE id = ?;
"""

# =====================================================================
# REMINDERS, SYMPTOMS, ALERTS, DAILY ACTIVITY, SYNC
# =====================================================================

INSERT_REMINDER = """
INSERT INTO reminders (patient_id, caregiver_id, title, reminder_type, scheduled_time, is_completed, recurring_frequency)
VALUES (?, ?, ?, ?, ?, ?, ?);
"""

GET_PATIENT_REMINDERS = """
SELECT id, patient_id, caregiver_id, title, reminder_type, scheduled_time, is_completed, recurring_frequency, created_at
FROM reminders
WHERE patient_id = ?
ORDER BY scheduled_time ASC;
"""

INSERT_SYMPTOM = """
INSERT INTO symptoms (patient_id, caregiver_id, symptom_name, severity, notes, logged_at)
VALUES (?, ?, ?, ?, ?, ?);
"""

GET_PATIENT_SYMPTOMS = """
SELECT id, patient_id, caregiver_id, symptom_name, severity, notes, logged_at, created_at
FROM symptoms
WHERE patient_id = ?
ORDER BY logged_at DESC;
"""

INSERT_ALERT = """
INSERT INTO alerts (patient_id, caregiver_id, alert_type, severity, message, is_read)
VALUES (?, ?, ?, ?, ?, ?);
"""

GET_PATIENT_ALERTS = """
SELECT id, patient_id, caregiver_id, alert_type, severity, message, is_read, resolved_at, created_at
FROM alerts
WHERE patient_id = ?
ORDER BY created_at DESC;
"""

MARK_ALERT_READ = """
UPDATE alerts
SET is_read = 1, resolved_at = datetime('now', 'utc')
WHERE id = ?;
"""

UPSERT_DAILY_ACTIVITY = """
INSERT INTO daily_activity (patient_id, activity_date, games_played, total_duration_seconds, avg_score, symptoms_count, routine_adherence_percentage, notes)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(patient_id, activity_date) DO UPDATE SET
    games_played = excluded.games_played,
    total_duration_seconds = excluded.total_duration_seconds,
    avg_score = excluded.avg_score,
    symptoms_count = excluded.symptoms_count,
    routine_adherence_percentage = excluded.routine_adherence_percentage,
    notes = excluded.notes;
"""

GET_DAILY_ACTIVITIES = """
SELECT id, patient_id, activity_date, games_played, total_duration_seconds, avg_score, symptoms_count, routine_adherence_percentage, notes, created_at
FROM daily_activity
WHERE patient_id = ?
ORDER BY activity_date DESC
LIMIT ?;
"""

INSERT_SYNC_LOG = """
INSERT INTO sync_log (device_id, records_synced, sync_type, status, details)
VALUES (?, ?, ?, ?, ?);
"""

GET_SYNC_LOGS = """
SELECT id, device_id, records_synced, sync_type, status, sync_timestamp, details
FROM sync_log
ORDER BY sync_timestamp DESC
LIMIT ?;
"""
