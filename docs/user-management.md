# Phase 4 - User Management

This phase adds user-facing APIs on top of authentication.

## APIs
- `GET /api/v1/users/me`
- `PATCH /api/v1/users/me`
- `POST /api/v1/users/me/change-password`
- `DELETE /api/v1/users/me`
- `POST /api/v1/users/me/avatar`
- `GET /api/v1/users`

## Notes
- Account deletion is implemented as deactivation so meeting history and task history remain intact.
- Avatar uploads are stored locally under `uploads/avatars` and served through FastAPI static files.
- Listing users is restricted to admin roles.
