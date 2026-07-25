from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_verified_user, require_roles
from app.database import get_db
from app.schemas import ChangePasswordRequest, SimpleMessageResponse, UpdateProfileRequest, UserActionResponse, UserListResponse, UserPublic
from app.services import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserPublic)
def get_profile(current_user=Depends(get_current_verified_user)) -> UserPublic:
    return UserPublic.model_validate(UserService.get_profile(current_user))


@router.patch("/me", response_model=UserActionResponse)
def update_profile(
    payload: UpdateProfileRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_verified_user),
) -> UserActionResponse:
    user, verification_token = UserService.update_profile(
        db=db,
        user=current_user,
        name=payload.name,
        email=payload.email,
    )
    db.commit()
    db.refresh(user)
    return UserActionResponse(
        user=UserPublic.model_validate(user),
        message="Profile updated successfully",
        verification_token=verification_token,
    )


@router.post("/me/change-password", response_model=SimpleMessageResponse)
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_verified_user),
) -> SimpleMessageResponse:
    UserService.change_password(db=db, user=current_user, current_password=payload.current_password, new_password=payload.new_password)
    db.commit()
    return SimpleMessageResponse(message="Password changed successfully")


@router.delete("/me", response_model=SimpleMessageResponse)
def delete_account(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_verified_user),
) -> SimpleMessageResponse:
    UserService.delete_account(db=db, user=current_user)
    db.commit()
    return SimpleMessageResponse(message="Account deleted successfully")


@router.post("/me/avatar", response_model=UserActionResponse)
def upload_avatar(
    avatar: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_verified_user),
) -> UserActionResponse:
    user = UserService.upload_avatar(db=db, user=current_user, avatar=avatar)
    db.commit()
    db.refresh(user)
    return UserActionResponse(user=UserPublic.model_validate(user), message="Avatar uploaded successfully")


@router.get("", response_model=UserListResponse, dependencies=[Depends(require_roles("admin"))])
def list_users(
    db: Session = Depends(get_db),
    search: str | None = Query(default=None, max_length=100),
    role: str | None = Query(default=None, max_length=50),
    is_active: bool | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> UserListResponse:
    users, total = UserService.list_users(
        db=db,
        search=search,
        role=role,
        is_active=is_active,
        limit=limit,
        offset=offset,
    )
    return UserListResponse(
        users=[UserPublic.model_validate(user) for user in users],
        total=total,
        limit=limit,
        offset=offset,
    )
