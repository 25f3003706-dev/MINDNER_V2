"""Schema package exporting all Pydantic models."""

from app.schemas.patient import PatientBase, PatientCreate, PatientUpdate, PatientResponse, PatientSummary
from app.schemas.caregiver import CaregiverBase, CaregiverCreate, CaregiverUpdate, CaregiverResponse, PatientCaregiverLinkCreate, LinkedPatientResponse
from app.schemas.game import CognitiveGameBase, CognitiveGameCreate, CognitiveGameResponse
from app.schemas.session import GameSessionBase, GameSessionCreate, GameSessionResponse
from app.schemas.attempt import GameAttemptBase, GameAttemptCreate, GameAttemptResponse
from app.schemas.progress import PatientProgressSummary, DomainScoreSummary, DailyActivitySummary
from app.schemas.scoring import CognitiveScoreBase, CognitiveScoreCreate, CognitiveScoreResponse, ScoreCalculationRequest, ScoreCalculationResult
from app.schemas.adaptive import AdaptiveDifficultyRequest, AdaptiveDifficultyResponse
from app.schemas.recommendation import AIAssessmentBase, AIAssessmentCreate, AIAssessmentResponse, AIRecommendationBase, AIRecommendationCreate, AIRecommendationResponse
from app.schemas.alert import SymptomBase, SymptomCreate, SymptomResponse, AlertBase, AlertCreate, AlertResponse, ReminderBase, ReminderCreate, ReminderResponse

__all__ = [
    "PatientBase",
    "PatientCreate",
    "PatientUpdate",
    "PatientResponse",
    "PatientSummary",
    "CaregiverBase",
    "CaregiverCreate",
    "CaregiverUpdate",
    "CaregiverResponse",
    "PatientCaregiverLinkCreate",
    "LinkedPatientResponse",
    "CognitiveGameBase",
    "CognitiveGameCreate",
    "CognitiveGameResponse",
    "GameSessionBase",
    "GameSessionCreate",
    "GameSessionResponse",
    "GameAttemptBase",
    "GameAttemptCreate",
    "GameAttemptResponse",
    "PatientProgressSummary",
    "DomainScoreSummary",
    "DailyActivitySummary",
    "CognitiveScoreBase",
    "CognitiveScoreCreate",
    "CognitiveScoreResponse",
    "ScoreCalculationRequest",
    "ScoreCalculationResult",
    "AdaptiveDifficultyRequest",
    "AdaptiveDifficultyResponse",
    "AIAssessmentBase",
    "AIAssessmentCreate",
    "AIAssessmentResponse",
    "AIRecommendationBase",
    "AIRecommendationCreate",
    "AIRecommendationResponse",
    "SymptomBase",
    "SymptomCreate",
    "SymptomResponse",
    "AlertBase",
    "AlertCreate",
    "AlertResponse",
    "ReminderBase",
    "ReminderCreate",
    "ReminderResponse",
]
