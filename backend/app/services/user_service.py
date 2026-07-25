from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import build_email_token, hash_one_time_token, hash_password, verify_password
from app.core.settings import get_settings
from app.models import EmailVerificationToken, RefreshToken, User
from app.utils import delete_avatar_file, save_avatar_file


class UserService:
    @staticmethod
    def _normalize_email(email: str) -> str:
        return email.strip().lower()

    @staticmethod
    def _utcnow() -> datetime:
        return datetime.now(timezone.utc)

    @classmethod
    def get_profile(cls, user: User) -> User:
        return user

    @classmethod
    def update_profile(
        cls,
        db: Session,
        user: User,
        name: str | None = None,
        email: str | None = None,
    ) -> tuple[User, str | None]:
        verification_token: str | None = None

        if name is not None:
            user.name = name.strip()

        if email is not None:
            normalized_email = cls._normalize_email(email)
            existing_user = db.scalar(select(User).where(User.email == normalized_email, User.id != user.id))
            if existing_user is not None:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")

            if normalized_email != user.email:
                user.email = normalized_email
                user.email_verified = False
                user.email_verified_at = None
                db.query(EmailVerificationToken).filter(EmailVerificationToken.user_id == user.id).update(
                    {EmailVerificationToken.used_at: cls._utcnow()}, synchronize_session=False
                )
                verification_token = build_email_token()
                db.add(
                    EmailVerificationToken(
                        user_id=user.id,
                        token_hash=hash_one_time_token(verification_token),
                        expires_at=cls._utcnow() + timedelta(minutes=get_settings().email_token_expire_minutes),
                    )
                )

        return user, verification_token

    @classmethod
    def change_password(cls, db: Session, user: User, current_password: str, new_password: str) -> None:
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")

        user.password_hash = hash_password(new_password)
        user.last_login_at = cls._utcnow()

        refresh_tokens = db.scalars(select(RefreshToken).where(RefreshToken.user_id == user.id)).all()
        for refresh_token in refresh_tokens:
            refresh_token.is_revoked = True
            refresh_token.revoked_at = cls._utcnow()

    @classmethod
    def delete_account(cls, db: Session, user: User) -> None:
        user.is_active = False
        user.email_verified = False
        user.email_verified_at = None

        refresh_tokens = db.scalars(select(RefreshToken).where(RefreshToken.user_id == user.id)).all()
        for refresh_token in refresh_tokens:
            refresh_token.is_revoked = True
            refresh_token.revoked_at = cls._utcnow()

    @classmethod
    def upload_avatar(cls, db: Session, user: User, avatar: UploadFile) -> User:
        avatar_url = save_avatar_file(user.id, avatar)
        delete_avatar_file(user.avatar_url)
        user.avatar_url = avatar_url
        return user

    @classmethod
    def list_users(
        cls,
        db: Session,
        search: str | None = None,
        role: str | None = None,
        is_active: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[User], int]:
        statement = select(User)
        count_statement = select(func.count()).select_from(User)

        filters = []
        if search:
            search_term = f"%{search.strip().lower()}%"
            filters.append(func.lower(User.name).like(search_term) | func.lower(User.email).like(search_term))
        if role:
            filters.append(User.role == role)
        if is_active is not None:
            filters.append(User.is_active.is_(is_active))

        if filters:
            for filter_expression in filters:
                statement = statement.where(filter_expression)
                count_statement = count_statement.where(filter_expression)

        total = db.scalar(count_statement) or 0
        users = db.scalars(statement.order_by(User.created_at.desc()).limit(limit).offset(offset)).all()
        return users, total
