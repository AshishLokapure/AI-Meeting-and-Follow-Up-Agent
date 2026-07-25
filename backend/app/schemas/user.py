from pydantic import BaseModel, EmailStr, Field

from app.schemas.auth import UserPublic


class UpdateProfileRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    email: EmailStr | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class UserListResponse(BaseModel):
    users: list[UserPublic]
    total: int
    limit: int
    offset: int


class UserActionResponse(BaseModel):
    user: UserPublic
    message: str
    verification_token: str | None = None
