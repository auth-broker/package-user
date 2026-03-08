"""User model."""

from datetime import datetime

from sqlalchemy import Column, DateTime, UniqueConstraint, func
from sqlmodel import Field, SQLModel

from ab_core.database.mixins.active import ActiveMixin
from ab_core.database.mixins.created_at import CreatedAtMixin
from ab_core.database.mixins.id import IDMixin
from ab_core.database.mixins.updated_at import UpdatedAtMixin


class User(IDMixin, CreatedAtMixin, UpdatedAtMixin, ActiveMixin, SQLModel, table=True):
    """User model."""

    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("oidc_sub", name="uq_users_oidc_sub"),)

    oidc_sub: str = Field(index=True, nullable=False, unique=True)

    email: str | None = Field(default=None, index=True)
    display_name: str | None = Field(default=None)
    preferred_username: str | None = Field(default=None)

    last_seen: datetime | None = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
    )
