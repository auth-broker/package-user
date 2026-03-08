"""Service for managing users."""

from datetime import UTC, datetime
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .model import User


class UserService(BaseModel):
    """Service for managing users."""

    async def get_user_by_oidc(
        self,
        *,
        oidc_sub: str,
        db_session: AsyncSession,
    ) -> User | None:
        """Fetch a user by their OIDC subject and issuer."""
        result = await db_session.execute(
            select(User).where(
                User.oidc_sub == oidc_sub,
            )
        )
        return result.scalar_one_or_none()

    async def get_user_by_id(
        self,
        *,
        user_id: UUID,
        db_session: AsyncSession,
    ) -> User | None:
        """Fetch a user by their ID."""
        return await db_session.get(User, user_id)

    async def seen_user(
        self,
        *,
        user: User,
        db_session: AsyncSession,
    ) -> None:
        """Update the user's last seen timestamp."""
        user.last_seen = datetime.now(UTC)
        db_session.add(user)
        await db_session.flush()

    async def upsert_user_by_oidc(
        self,
        *,
        oidc_sub: str,
        email: str | None = None,
        display_name: str | None = None,
        preferred_username: str | None = None,
        db_session: AsyncSession,
    ) -> User:
        """Insert or update a user based on OIDC subject and issuer."""
        user = await self.get_user_by_oidc(
            oidc_sub=oidc_sub,
            db_session=db_session,
        )

        if user:
            if email is not None:
                user.email = email
            if display_name is not None:
                user.display_name = display_name
            if preferred_username is not None:
                user.preferred_username = preferred_username
        else:
            user = User(
                oidc_sub=oidc_sub,
                email=email,
                display_name=display_name,
                preferred_username=preferred_username,
            )
            db_session.add(user)

        await db_session.flush()
        return user
