from datetime import timedelta

from sqlalchemy import Float, TypeDecorator
from sqlalchemy.dialects import postgresql


class DurationType(TypeDecorator):
    """Duration type that works with both PostgreSQL and SQLite."""

    impl = Float
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(postgresql.INTERVAL())
        else:
            return dialect.type_descriptor(Float())

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if not isinstance(value, timedelta):
            value = timedelta(seconds=float(value))
        if dialect.name == "postgresql":
            return value
        return value.total_seconds()

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            if isinstance(value, timedelta):
                return value
        return timedelta(seconds=float(value))
