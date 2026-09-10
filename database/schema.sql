PRAGMA foreign_keys = ON;


-- =========================================================
-- 1. PATIENTS
-- =========================================================

CREATE TABLE IF NOT EXISTS patients (
    patient_id INTEGER PRIMARY KEY AUTOINCREMENT,

    patient_code TEXT NOT NULL UNIQUE,

    first_name TEXT NOT NULL,

    last_name TEXT,

    date_of_birth TEXT,

    gender TEXT
        CHECK (
            gender IN (
                'Male',
                'Female',
                'Other',
                'Unknown'
            )
        ),

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- =========================================================
-- 2. DIAGNOSES
-- =========================================================

CREATE TABLE IF NOT EXISTS diagnoses (
    diagnosis_id INTEGER PRIMARY KEY AUTOINCREMENT,

    patient_id INTEGER NOT NULL,

    diagnosis_type TEXT NOT NULL
        CHECK (
            diagnosis_type IN (
                'Alzheimers Disease',
                'Lewy Body Dementia',
                'Frontotemporal Dementia'
            )
        ),

    diagnosis_date TEXT,

    severity TEXT
        CHECK (
            severity IN (
                'Mild',
                'Moderate',
                'Severe'
            )
        ),

    diagnosed_by TEXT,

    notes TEXT,

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (patient_id)
        REFERENCES patients(patient_id)
        ON DELETE CASCADE
);


-- =========================================================
-- 3. CAREGIVERS
-- =========================================================

CREATE TABLE IF NOT EXISTS caregivers (
    caregiver_id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    email TEXT UNIQUE,

    phone TEXT,

    relationship TEXT,

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- =========================================================
-- 4. PATIENT - CAREGIVER RELATIONSHIP
-- =========================================================

CREATE TABLE IF NOT EXISTS patient_caregivers (
    patient_id INTEGER NOT NULL,

    caregiver_id INTEGER NOT NULL,

    relationship TEXT,

    is_primary INTEGER NOT NULL DEFAULT 0
        CHECK (is_primary IN (0, 1)),

    start_date TEXT,

    end_date TEXT,

    PRIMARY KEY (
        patient_id,
        caregiver_id
    ),

    FOREIGN KEY (patient_id)
        REFERENCES patients(patient_id)
        ON DELETE CASCADE,

    FOREIGN KEY (caregiver_id)
        REFERENCES caregivers(caregiver_id)
        ON DELETE CASCADE
);


-- =========================================================
-- 5. COGNITIVE ASSESSMENTS
-- =========================================================

CREATE TABLE IF NOT EXISTS cognitive_assessments (
    assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,

    patient_id INTEGER NOT NULL,

    assessment_date TEXT NOT NULL,

    memory_score REAL
        CHECK (
            memory_score BETWEEN 0 AND 100
        ),

    attention_score REAL
        CHECK (
            attention_score BETWEEN 0 AND 100
        ),

    language_score REAL
        CHECK (
            language_score BETWEEN 0 AND 100
        ),

    orientation_score REAL
        CHECK (
            orientation_score BETWEEN 0 AND 100
        ),

    executive_function_score REAL
        CHECK (
            executive_function_score BETWEEN 0 AND 100
        ),

    overall_score REAL
        CHECK (
            overall_score BETWEEN 0 AND 100
        ),

    assessment_type TEXT,

    notes TEXT,

    FOREIGN KEY (patient_id)
        REFERENCES patients(patient_id)
        ON DELETE CASCADE
);


-- =========================================================
-- 6. BEHAVIORAL OBSERVATIONS
-- =========================================================

CREATE TABLE IF NOT EXISTS behavioral_observations (
    behavior_id INTEGER PRIMARY KEY AUTOINCREMENT,

    patient_id INTEGER NOT NULL,

    recorded_at TEXT NOT NULL,

    behavior_type TEXT NOT NULL,

    severity TEXT
        CHECK (
            severity IN (
                'LOW',
                'MEDIUM',
                'HIGH',
                'CRITICAL'
            )
        ),

    duration_minutes INTEGER
        CHECK (
            duration_minutes >= 0
        ),

    frequency INTEGER
        CHECK (
            frequency >= 0
        ),

    description TEXT,

    FOREIGN KEY (patient_id)
        REFERENCES patients(patient_id)
        ON DELETE CASCADE
);


-- =========================================================
-- 7. DAILY ACTIVITIES / ADL
-- =========================================================

CREATE TABLE IF NOT EXISTS daily_activities (
    activity_id INTEGER PRIMARY KEY AUTOINCREMENT,

    patient_id INTEGER NOT NULL,

    activity_date TEXT NOT NULL,

    activity_type TEXT NOT NULL,

    difficulty_score INTEGER
        CHECK (
            difficulty_score BETWEEN 1 AND 5
        ),

    completion_status TEXT
        CHECK (
            completion_status IN (
                'COMPLETED',
                'PARTIAL',
                'MISSED',
                'NOT_REQUIRED'
            )
        ),

    assistance_required TEXT
        CHECK (
            assistance_required IN (
                'NONE',
                'MINIMAL',
                'MODERATE',
                'FULL'
            )
        ),

    duration_minutes INTEGER
        CHECK (
            duration_minutes >= 0
        ),

    notes TEXT,

    FOREIGN KEY (patient_id)
        REFERENCES patients(patient_id)
        ON DELETE CASCADE
);


-- =========================================================
-- 8. HEALTH OBSERVATIONS
-- =========================================================

CREATE TABLE IF NOT EXISTS health_observations (
    observation_id INTEGER PRIMARY KEY AUTOINCREMENT,

    patient_id INTEGER NOT NULL,

    observation_time TEXT NOT NULL,

    observation_type TEXT NOT NULL,

    value_numeric REAL,

    value_text TEXT,

    unit TEXT,

    source TEXT,

    FOREIGN KEY (patient_id)
        REFERENCES patients(patient_id)
        ON DELETE CASCADE
);


-- =========================================================
-- 9. MEDICATIONS
-- =========================================================

CREATE TABLE IF NOT EXISTS medications (
    medication_id INTEGER PRIMARY KEY AUTOINCREMENT,

    patient_id INTEGER NOT NULL,

    medication_name TEXT NOT NULL,

    dosage TEXT,

    frequency TEXT,

    start_date TEXT,

    end_date TEXT,

    prescribing_doctor TEXT,

    notes TEXT,

    FOREIGN KEY (patient_id)
        REFERENCES patients(patient_id)
        ON DELETE CASCADE
);


-- =========================================================
-- 10. MEDICATION LOGS
-- =========================================================

CREATE TABLE IF NOT EXISTS medication_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,

    medication_id INTEGER NOT NULL,

    scheduled_time TEXT NOT NULL,

    taken_time TEXT,

    status TEXT NOT NULL
        CHECK (
            status IN (
                'TAKEN',
                'MISSED',
                'LATE',
                'REFUSED'
            )
        ),

    notes TEXT,

    FOREIGN KEY (medication_id)
        REFERENCES medications(medication_id)
        ON DELETE CASCADE
);


-- =========================================================
-- 11. ML PREDICTIONS
-- =========================================================

CREATE TABLE IF NOT EXISTS ml_predictions (
    prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,

    patient_id INTEGER NOT NULL,

    prediction_time TEXT NOT NULL,

    model_name TEXT NOT NULL,

    model_version TEXT,

    prediction_type TEXT NOT NULL,

    prediction TEXT,

    probability REAL
        CHECK (
            probability BETWEEN 0 AND 1
        ),

    risk_score REAL
        CHECK (
            risk_score BETWEEN 0 AND 100
        ),

    explanation TEXT,

    FOREIGN KEY (patient_id)
        REFERENCES patients(patient_id)
        ON DELETE CASCADE
);


-- =========================================================
-- 12. RISK EVENTS
-- =========================================================

CREATE TABLE IF NOT EXISTS risk_events (
    risk_id INTEGER PRIMARY KEY AUTOINCREMENT,

    patient_id INTEGER NOT NULL,

    detected_at TEXT NOT NULL,

    risk_type TEXT NOT NULL,

    risk_score REAL
        CHECK (
            risk_score BETWEEN 0 AND 100
        ),

    severity TEXT
        CHECK (
            severity IN (
                'LOW',
                'MEDIUM',
                'HIGH',
                'CRITICAL'
            )
        ),

    source TEXT,

    description TEXT,

    status TEXT NOT NULL DEFAULT 'OPEN'
        CHECK (
            status IN (
                'OPEN',
                'ACKNOWLEDGED',
                'RESOLVED',
                'DISMISSED'
            )
        ),

    FOREIGN KEY (patient_id)
        REFERENCES patients(patient_id)
        ON DELETE CASCADE
);


-- =========================================================
-- 13. CAREGIVER NOTES
-- =========================================================

CREATE TABLE IF NOT EXISTS caregiver_notes (
    note_id INTEGER PRIMARY KEY AUTOINCREMENT,

    patient_id INTEGER NOT NULL,

    caregiver_id INTEGER NOT NULL,

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    category TEXT,

    note TEXT NOT NULL,

    FOREIGN KEY (patient_id)
        REFERENCES patients(patient_id)
        ON DELETE CASCADE,

    FOREIGN KEY (caregiver_id)
        REFERENCES caregivers(caregiver_id)
        ON DELETE CASCADE
);


-- =========================================================
-- 14. NOTIFICATIONS
-- =========================================================

CREATE TABLE IF NOT EXISTS notifications (
    notification_id INTEGER PRIMARY KEY AUTOINCREMENT,

    patient_id INTEGER NOT NULL,

    caregiver_id INTEGER,

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    notification_type TEXT NOT NULL,

    priority TEXT NOT NULL
        CHECK (
            priority IN (
                'LOW',
                'MEDIUM',
                'HIGH',
                'CRITICAL'
            )
        ),

    message TEXT NOT NULL,

    status TEXT NOT NULL DEFAULT 'UNREAD'
        CHECK (
            status IN (
                'UNREAD',
                'READ',
                'DISMISSED'
            )
        ),

    FOREIGN KEY (patient_id)
        REFERENCES patients(patient_id)
        ON DELETE CASCADE,

    FOREIGN KEY (caregiver_id)
        REFERENCES caregivers(caregiver_id)
        ON DELETE SET NULL
);


-- =========================================================
-- 15. EMERGENCY CONTACTS
-- =========================================================

CREATE TABLE IF NOT EXISTS emergency_contacts (
    contact_id INTEGER PRIMARY KEY AUTOINCREMENT,

    patient_id INTEGER NOT NULL,

    name TEXT NOT NULL,

    relationship TEXT,

    phone TEXT NOT NULL,

    priority INTEGER DEFAULT 1,

    FOREIGN KEY (patient_id)
        REFERENCES patients(patient_id)
        ON DELETE CASCADE
);


-- =========================================================
-- INDEXES
-- =========================================================

CREATE INDEX IF NOT EXISTS idx_diagnoses_patient
ON diagnoses(patient_id);


CREATE INDEX IF NOT EXISTS idx_cognitive_patient_date
ON cognitive_assessments(
    patient_id,
    assessment_date
);


CREATE INDEX IF NOT EXISTS idx_behavior_patient_date
ON behavioral_observations(
    patient_id,
    recorded_at
);


CREATE INDEX IF NOT EXISTS idx_activity_patient_date
ON daily_activities(
    patient_id,
    activity_date
);


CREATE INDEX IF NOT EXISTS idx_health_patient_time
ON health_observations(
    patient_id,
    observation_time
);


CREATE INDEX IF NOT EXISTS idx_medications_patient
ON medications(patient_id);


CREATE INDEX IF NOT EXISTS idx_medication_logs_medication
ON medication_logs(medication_id);


CREATE INDEX IF NOT EXISTS idx_risk_patient_time
ON risk_events(
    patient_id,
    detected_at
);


CREATE INDEX IF NOT EXISTS idx_ml_patient_time
ON ml_predictions(
    patient_id,
    prediction_time
);


CREATE INDEX IF NOT EXISTS idx_notifications_caregiver
ON notifications(
    caregiver_id,
    status
);


CREATE INDEX IF NOT EXISTS idx_emergency_patient
ON emergency_contacts(patient_id);