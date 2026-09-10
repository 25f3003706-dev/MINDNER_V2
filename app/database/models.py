"""Data models representing entities in the Mindner database."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PatientModel:
    id: Optional[int] = None
    first_name: str = ""
    last_name: str = ""
    age: Optional[int] = None
    gender: Optional[str] = None
    stage: str = "Mild"
    baseline_score: float = 70.0
    diagnosis_date: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class CaregiverModel:
    id: Optional[int] = None
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: Optional[str] = None
    relation: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class PatientCaregiverModel:
    id: Optional[int] = None
    patient_id: int = 0
    caregiver_id: int = 0
    relationship_type: str = "Primary Caregiver"
    is_primary: int = 1
    created_at: Optional[str] = None


@dataclass
class CognitiveGameModel:
    id: Optional[int] = None
    game_key: str = ""
    name: str = ""
    category: str = ""
    description: Optional[str] = None
    max_level: int = 10
    is_active: int = 1
    created_at: Optional[str] = None


@dataclass
class GameSessionModel:
    id: Optional[int] = None
    patient_id: int = 0
    game_id: int = 0
    level: int = 1
    duration_seconds: int = 0
    status: str = "completed"
    score: float = 0.0
    accuracy_percentage: float = 0.0
    reaction_time_ms: Optional[float] = None
    device_info: Optional[str] = None
    session_timestamp: Optional[str] = None
    created_at: Optional[str] = None


@dataclass
class CognitiveScoreModel:
    id: Optional[int] = None
    patient_id: int = 0
    session_id: Optional[int] = None
    domain: str = "general"
    score_value: float = 0.0
    baseline_deviation: float = 0.0
    calculation_details: Optional[str] = None
    recorded_at: Optional[str] = None


@dataclass
class AIAssessmentModel:
    id: Optional[int] = None
    patient_id: int = 0
    assessment_date: Optional[str] = None
    summary: str = ""
    risk_level: str = "low"
    cognitive_trend: str = "stable"
    confidence_score: float = 0.85
    raw_insights: Optional[str] = None
    created_at: Optional[str] = None


@dataclass
class AIRecommendationModel:
    id: Optional[int] = None
    patient_id: int = 0
    assessment_id: Optional[int] = None
    title: str = ""
    description: str = ""
    category: str = "game_adjustment"
    priority: str = "medium"
    status: str = "active"
    created_at: Optional[str] = None


@dataclass
class ReminderModel:
    id: Optional[int] = None
    patient_id: int = 0
    caregiver_id: Optional[int] = None
    title: str = ""
    reminder_type: str = "medication"
    scheduled_time: str = ""
    is_completed: int = 0
    recurring_frequency: str = "daily"
    created_at: Optional[str] = None


@dataclass
class SymptomModel:
    id: Optional[int] = None
    patient_id: int = 0
    caregiver_id: Optional[int] = None
    symptom_name: str = ""
    severity: int = 1
    notes: Optional[str] = None
    logged_at: Optional[str] = None
    created_at: Optional[str] = None


@dataclass
class AlertModel:
    id: Optional[int] = None
    patient_id: int = 0
    caregiver_id: Optional[int] = None
    alert_type: str = "info"
    severity: str = "info"
    message: str = ""
    is_read: int = 0
    resolved_at: Optional[str] = None
    created_at: Optional[str] = None


@dataclass
class DailyActivityModel:
    id: Optional[int] = None
    patient_id: int = 0
    activity_date: str = ""
    games_played: int = 0
    total_duration_seconds: int = 0
    avg_score: float = 0.0
    symptoms_count: int = 0
    routine_adherence_percentage: float = 100.0
    notes: Optional[str] = None
    created_at: Optional[str] = None


@dataclass
class SyncLogModel:
    id: Optional[int] = None
    device_id: str = ""
    records_synced: int = 0
    sync_type: str = "batch_sessions"
    status: str = "success"
    sync_timestamp: Optional[str] = None
    details: Optional[str] = None
