import pytest

from obo_core.user.model import User
from obo_core.user.service import UserService


@pytest.mark.asyncio
async def test_user_service(tmp_database_async_session):
    service = UserService()
    session = tmp_database_async_session

    # ── create ────────────────────────────────────────────────
    user = await service.me(
        oidc_sub="abc123",
        oidc_iss="https://issuer.example.com",
        email="test@example.com",
        display_name="Tester",
        preferred_username="tester",
        db_session=session,
    )
    await session.commit()
    await session.refresh(user)

    assert isinstance(user, User)
    assert (user.oidc_sub, user.oidc_iss) == ("abc123", "https://issuer.example.com")
    assert (user.email, user.display_name, user.preferred_username) == (
        "test@example.com",
        "Tester",
        "tester",
    )

    created_at = user.created_at
    updated_at = user.updated_at

    # ── update ────────────────────────────────────────────────
    updated_user = await service.me(
        oidc_sub="abc123",
        oidc_iss="https://issuer.example.com",
        email="new@example.com",
        display_name="Updated Tester",
        db_session=session,
    )
    await session.commit()
    await session.refresh(updated_user)

    assert updated_user.id == user.id
    assert updated_user.email == "new@example.com"
    assert updated_user.display_name == "Updated Tester"
    assert updated_user.updated_at >= updated_at
    assert updated_user.created_at == created_at

    # ── fetch by OIDC ─────────────────────────────────────────
    fetched = await service.get_user_by_oidc(
        oidc_sub="abc123",
        oidc_iss="https://issuer.example.com",
        db_session=session,
    )
    assert fetched and fetched.id == user.id

    # ── fetch by id ───────────────────────────────────────────
    by_id = await service.get_user_by_id(
        user_id=user.id,
        db_session=session,
    )
    assert by_id and by_id.oidc_sub == "abc123"

    # ── seen_user updates last_seen ───────────────────────────
    last_seen_before = by_id.last_seen
    await service.seen_user(user=by_id, db_session=session)
    await session.commit()
    await session.refresh(by_id)

    assert by_id.last_seen >= last_seen_before
