from app.database.base import Base

import app.models  # noqa: F401
from app.database.session import engine


def create_all_tables() -> None:
    Base.metadata.create_all(bind=engine)
