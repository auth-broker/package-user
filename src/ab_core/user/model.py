from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel

from ab_core.database.mixins.active import ActiveMixin
from ab_core.database.mixins.created_at import CreatedAtMixin
from ab_core.database.mixins.id import IDMixin
from ab_core.database.mixins.updated_at import UpdatedAtMixin


class User(IDMixin, CreatedAtMixin, UpdatedAtMixin, ActiveMixin, SQLModel, table=True):
    __tablename__ = "users"

    oidc_sub: str = Field(index=True, nullable=False)
    oidc_iss: str = Field(nullable=False)

    email: Optional[str] = Field(default=None, index=True)
    display_name: Optional[str] = Field(default=None)
    preferred_username: Optional[str] = Field(default=None)

    last_seen: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
