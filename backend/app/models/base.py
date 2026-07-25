from app.database.base import TimestampMixin, UUIDPrimaryKeyMixin


class ModelBase(TimestampMixin, UUIDPrimaryKeyMixin):
    pass
