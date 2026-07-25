from datetime import datetime, timedelta, timezone
from uuid import uuid4
import hashlib
import secrets

import bcrypt
import jwt
from jwt import InvalidTokenError

from app.core.settings import get_settings


def hash_password(password: str) -> str:
    # bcrypt enforces a 72-byte max; keep hashing deterministic for normal passwords.
    secret = password.encode("utf-8")[:72]
    return bcrypt.hashpw(secret, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    secret = password.encode("utf-8")[:72]
    try:
        return bcrypt.checkpw(secret, password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_token(payload: dict, expires_delta: timedelta) -> str:
    settings = get_settings()
    issued_at = datetime.now(timezone.utc)
    token_payload = payload.copy()
    token_payload["exp"] = issued_at + expires_delta
    token_payload["iat"] = issued_at
    token_payload["jti"] = token_payload.get("jti", str(uuid4()))
    return jwt.encode(token_payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    settings = get_settings()
    return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_random_token() -> str:
    return secrets.token_urlsafe(48)


def build_access_token(user_id: str, email: str, role: str) -> str:
    settings = get_settings()
    return create_token(
        {"sub": user_id, "email": email, "role": role, "type": "access"},
        timedelta(minutes=settings.access_token_expire_minutes),
    )


def build_refresh_token(user_id: str, email: str, role: str, jti: str | None = None) -> str:
    settings = get_settings()
    return create_token(
        {"sub": user_id, "email": email, "role": role, "type": "refresh", "jti": jti or str(uuid4())},
        timedelta(days=settings.refresh_token_expire_days),
    )


def build_email_token() -> str:
    return generate_random_token()


def build_password_reset_token() -> str:
    return generate_random_token()


def hash_one_time_token(token: str) -> str:
    return hash_token(token)
