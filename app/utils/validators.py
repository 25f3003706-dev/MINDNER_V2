"""Validation helpers for data hygiene and business constraints."""

import re
from typing import Optional


def validate_email_format(email: str) -> bool:
    """Validates if an email string adheres to standard RFC formatting."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email.strip()))


def validate_score_range(score: float, min_val: float = 0.0, max_val: float = 100.0) -> bool:
    """Ensures cognitive score is within normal bounded limits."""
    return min_val <= score <= max_val


def validate_stage(stage: str) -> bool:
    """Validates dementia/cognitive condition stage."""
    allowed_stages = {"Mild", "Moderate", "Severe", "Early", "Undiagnosed"}
    return stage in allowed_stages


def sanitize_string(val: Optional[str]) -> Optional[str]:
    """Trims whitespace and strips dangerous control characters."""
    if val is None:
        return None
    return val.strip()
