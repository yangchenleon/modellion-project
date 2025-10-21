from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import base64
import hashlib
import hmac
import os
import jwt

from .config import get_settings


def _pbkdf2_hash(password: str, salt: bytes, iterations: int = 260000) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)


def hash_password(password: str) -> str:
    iterations = 260000
    salt = os.urandom(16)
    dk = _pbkdf2_hash(password, salt, iterations)
    # store as: pbkdf2_sha256$iterations$salt_b64$hash_b64
    return "pbkdf2_sha256${}${}${}".format(
        iterations,
        base64.b64encode(salt).decode("ascii"),
        base64.b64encode(dk).decode("ascii"),
    )


def verify_password(password: str, stored: str) -> bool:
    try:
        algo, iterations_str, salt_b64, hash_b64 = stored.split("$")
        if algo != "pbkdf2_sha256":
            return False
        iterations = int(iterations_str)
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(hash_b64)
    except Exception:
        return False
    computed = _pbkdf2_hash(password, salt, iterations)
    return hmac.compare_digest(computed, expected)


def create_access_token(subject: str, role: str) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(seconds=settings.JWT_EXPIRES_IN)
    payload: Dict[str, Any] = {"sub": subject, "role": role, "exp": expire}
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    return token


def decode_token(token: str) -> Dict[str, Any]:
    settings = get_settings()
    return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])  # type: ignore[no-any-return]
