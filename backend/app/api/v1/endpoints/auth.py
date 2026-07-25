from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_verified_user, require_roles
from app.core.settings import get_settings
from app.database import get_db
from app.schemas import (
    AuthResponse,
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    SimpleMessageResponse,
    TokenPair,
    UserPublic,
    VerifyEmailRequest,
)
from app.services import AuthService
from app.workers.email_tasks import (
    send_password_changed_email,
    send_password_reset_email,
    send_verification_email,
    send_welcome_email,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _build_auth_response(user, access_token: str | None, refresh_token: str | None, verification_token: str | None = None) -> AuthResponse:
    settings = get_settings()
    tokens = None
    if access_token and refresh_token:
        tokens = TokenPair(access_token=access_token, refresh_token=refresh_token)
    return AuthResponse(
        user=UserPublic.model_validate(user),
        tokens=tokens,
        message="Registration successful. Verify your email to continue." if not user.email_verified else "Authentication successful",
        verification_token=verification_token if settings.environment != "production" else None,
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    settings = get_settings()
    user, verification_token = AuthService.register(
        db=db,
        name=payload.name,
        email=payload.email,
        password=payload.password,
    )
    db.commit()
    db.refresh(user)

    # Queue welcome + verification emails asynchronously
    send_welcome_email.delay(user.email, user.name, user.id)
    if verification_token:
        verification_url = f"{settings.frontend_url}/verify-email?token={verification_token}"
        send_verification_email.delay(user.email, user.name, verification_url, user.id)

    return _build_auth_response(user, None, None, verification_token)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    user, access_token, refresh_token = AuthService.login(db=db, email=payload.email, password=payload.password)
    db.commit()
    db.refresh(user)
    return _build_auth_response(user, access_token, refresh_token)


@router.post("/refresh", response_model=AuthResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> AuthResponse:
    user, access_token, refresh_token = AuthService.refresh(db=db, refresh_token=payload.refresh_token)
    db.commit()
    db.refresh(user)
    return _build_auth_response(user, access_token, refresh_token)


@router.post("/logout", response_model=SimpleMessageResponse)
def logout(payload: LogoutRequest, db: Session = Depends(get_db)) -> SimpleMessageResponse:
    AuthService.logout(db=db, refresh_token=payload.refresh_token)
    db.commit()
    return SimpleMessageResponse(message="Logged out successfully")


@router.post("/forgot-password", response_model=SimpleMessageResponse)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)) -> SimpleMessageResponse:
    settings = get_settings()
    token = AuthService.forgot_password(db=db, email=payload.email)
    db.commit()

    if token:
        from sqlalchemy import select
        from app.models import User
        user = db.scalar(select(User).where(User.email == payload.email.strip().lower()))
        if user:
            reset_url = f"{settings.frontend_url}/reset-password?token={token}"
            send_password_reset_email.delay(user.email, user.name, reset_url, user.id)

    return SimpleMessageResponse(
        message="If the account exists, a password reset link has been sent.",
        token=token if settings.environment != "production" else None,
    )


@router.post("/reset-password", response_model=SimpleMessageResponse)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)) -> SimpleMessageResponse:
    user = AuthService.reset_password(db=db, token=payload.token, new_password=payload.new_password)
    db.commit()
    # Notify user that password was changed
    send_password_changed_email.delay(user.email, user.name, user.id)
    return SimpleMessageResponse(message="Password updated successfully")


@router.post("/verify-email", response_model=SimpleMessageResponse)
def verify_email(payload: VerifyEmailRequest, db: Session = Depends(get_db)) -> SimpleMessageResponse:
    AuthService.verify_email(db=db, token=payload.token)
    db.commit()
    return SimpleMessageResponse(message="Email verified successfully")


@router.get("/me", response_model=UserPublic)
def me(current_user=Depends(get_current_verified_user)) -> UserPublic:
    return UserPublic.model_validate(current_user)


@router.get("/admin-only", response_model=SimpleMessageResponse, dependencies=[Depends(require_roles("admin"))])
def admin_only() -> SimpleMessageResponse:
    return SimpleMessageResponse(message="Admin access granted")
