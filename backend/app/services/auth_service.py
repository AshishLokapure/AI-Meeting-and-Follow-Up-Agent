from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import (
    build_access_token,
    build_email_token,
    build_password_reset_token,
    build_refresh_token,
    decode_token,
    hash_one_time_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.core.settings import get_settings
from app.models import EmailVerificationToken, PasswordResetToken, RefreshToken, User


class AuthService:
    @staticmethod
    def _normalize_email(email: str) -> str:
        return email.strip().lower()

    @staticmethod
    def _utcnow() -> datetime:
        return datetime.now(timezone.utc)

    @classmethod
    def _get_user_by_email(cls, db: Session, email: str) -> User | None:
        normalized_email = cls._normalize_email(email)
        statement = select(User).where(User.email == normalized_email)
        return db.scalar(statement)

    @classmethod
    def _issue_token_pair(cls, db: Session, user: User) -> tuple[str, str]:
        access_token = build_access_token(user.id, user.email, user.role)
        refresh_token = build_refresh_token(user.id, user.email, user.role)
        payload = decode_token(refresh_token)
        refresh_record = RefreshToken(
            user_id=user.id,
            jti=payload["jti"],
            token_hash=hash_token(refresh_token),
            expires_at=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
        )
        db.add(refresh_record)
        return access_token, refresh_token

    @classmethod
    def register(cls, db: Session, name: str, email: str, password: str) -> tuple[User, str | None]:
        normalized_email = cls._normalize_email(email)
        if cls._get_user_by_email(db, normalized_email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        user = User(name=name.strip(), email=normalized_email, password_hash=hash_password(password))
        db.add(user)
        db.flush()

        verification_token = build_email_token()
        verification_record = EmailVerificationToken(
            user_id=user.id,
            token_hash=hash_one_time_token(verification_token),
            expires_at=cls._utcnow() + timedelta(minutes=get_settings().email_token_expire_minutes),
        )
        db.add(verification_record)
        return user, verification_token

    @classmethod
    def login(cls, db: Session, email: str, password: str) -> tuple[User, str, str]:
        user = cls._get_user_by_email(db, email)
        if user is None or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is disabled")
        if not user.email_verified:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email verification required")

        user.last_login_at = cls._utcnow()
        access_token, refresh_token = cls._issue_token_pair(db, user)
        return user, access_token, refresh_token

    @classmethod
    def refresh(cls, db: Session, refresh_token: str) -> tuple[User, str, str]:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        user_id = payload.get("sub")
        jti = payload.get("jti")
        if not user_id or not jti:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh payload")

        user = db.get(User, user_id)
        if user is None or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        stored_token = db.scalar(select(RefreshToken).where(RefreshToken.jti == jti))
        if stored_token is None or stored_token.is_revoked:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked")
        if stored_token.token_hash != hash_token(refresh_token):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token mismatch")
        if stored_token.expires_at <= cls._utcnow():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

        stored_token.is_revoked = True
        stored_token.revoked_at = cls._utcnow()
        new_access_token, new_refresh_token = cls._issue_token_pair(db, user)
        return user, new_access_token, new_refresh_token

    @classmethod
    def logout(cls, db: Session, refresh_token: str) -> None:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        jti = payload.get("jti")
        if not jti:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh payload")

        stored_token = db.scalar(select(RefreshToken).where(RefreshToken.jti == jti))
        if stored_token is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token not found")
        stored_token.is_revoked = True
        stored_token.revoked_at = cls._utcnow()

    @classmethod
    def verify_email(cls, db: Session, token: str) -> User:
        stored = db.scalar(select(EmailVerificationToken).where(EmailVerificationToken.token_hash == hash_one_time_token(token)))
        if stored is None or stored.used_at is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification token is invalid")
        if stored.expires_at <= cls._utcnow():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification token expired")

        user = db.get(User, stored.user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        user.email_verified = True
        user.email_verified_at = cls._utcnow()
        stored.used_at = cls._utcnow()
        return user

    @classmethod
    def forgot_password(cls, db: Session, email: str) -> str | None:
        user = cls._get_user_by_email(db, email)
        if user is None:
            return None

        reset_token = build_password_reset_token()
        record = PasswordResetToken(
            user_id=user.id,
            token_hash=hash_one_time_token(reset_token),
            expires_at=cls._utcnow() + timedelta(minutes=get_settings().password_reset_token_expire_minutes),
        )
        db.add(record)
        return reset_token

    @classmethod
    def reset_password(cls, db: Session, token: str, new_password: str) -> User:
        stored = db.scalar(select(PasswordResetToken).where(PasswordResetToken.token_hash == hash_one_time_token(token)))
        if stored is None or stored.used_at is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset token is invalid")
        if stored.expires_at <= cls._utcnow():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset token expired")

        user = db.get(User, stored.user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        user.password_hash = hash_password(new_password)
        stored.used_at = cls._utcnow()

        refresh_tokens = db.scalars(select(RefreshToken).where(RefreshToken.user_id == user.id)).all()
        for refresh_token in refresh_tokens:
            refresh_token.is_revoked = True
            refresh_token.revoked_at = cls._utcnow()
        return user
