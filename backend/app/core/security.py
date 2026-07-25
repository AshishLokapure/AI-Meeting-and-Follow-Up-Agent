from datetime import datetime, timedelta, timezone
from uuid import uuid4
import hashlib
import secrets

import jwt
from jwt import InvalidTokenError
from passlib.context import CryptContext

from app.core.settings import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


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
