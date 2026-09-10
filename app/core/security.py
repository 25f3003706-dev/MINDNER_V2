"""Security and authentication utilities for future production auth.

Provides clean interfaces and placeholders for password hashing, API tokens,
and permission checks without introducing fake or brittle authentication logic.
"""

import hashlib
import hmac
import secrets
from typing import Optional
from app.core.config import settings


def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """Hashes a password with a cryptographic salt using PBKDF2-HMAC-SHA256.

    Returns:
        (hash_hex, salt_hex)
    """
    if salt is None:
        salt_bytes = secrets.token_bytes(16)
    else:
        salt_bytes = bytes.fromhex(salt)

    pwd_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt_bytes,
        iterations=100_000,
    )
    return pwd_hash.hex(), salt_bytes.hex()


def verify_password(password: str, hash_hex: str, salt_hex: str) -> bool:
    """Verifies a plaintext password against a stored hash and salt."""
    computed_hash, _ = hash_password(password, salt=salt_hex)
    return hmac.compare_digest(computed_hash, hash_hex)


def generate_api_key(prefix: str = "mnd_") -> str:
    """Generates a secure API key for device synchronization or caregiver access."""
    random_part = secrets.token_urlsafe(32)
    return f"{prefix}{random_part}"


# TODO: Integrate OAuth2 with JWTBearer when multi-tenant user authentication is required.
# TODO: Implement Role-Based Access Control (RBAC) for Patient vs Caregiver vs Physician roles.
