"""Account namespace derivation must agree for members of the same team."""

import os
from pathlib import Path

import pytest


def test_team_members_share_one_private_namespace_key() -> None:
    from qi_tuna_account_binding import account_digest

    first = {"id": 11, "team_id": 7, "user_id": 31, "role": "member", "is_active": True}
    second = {"id": 12, "team_id": 7, "user_id": 32, "role": "admin", "is_active": True}
    third = {"id": 13, "team_id": 8, "user_id": 33, "role": "member", "is_active": True}
    secret = b"a" * 32
    key = account_digest("https://api.quantum-inspire.com", 11, first, secret)
    if key != account_digest("https://api.quantum-inspire.com", 12, second, secret):
        raise AssertionError("members of one team did not select one namespace")
    if key == account_digest("https://api.quantum-inspire.com", 13, third, secret):
        raise AssertionError("different teams selected one namespace")


def test_inactive_or_mismatched_member_cannot_choose_a_namespace() -> None:
    from qi_tuna_account_binding import account_digest

    for member in (
        {"id": 12, "team_id": 7, "user_id": 31, "role": "member", "is_active": True},
        {"id": 11, "team_id": 7, "user_id": 31, "role": "member", "is_active": False},
    ):
        with pytest.raises(ValueError):
            account_digest("https://api.quantum-inspire.com", 11, member, b"a" * 32)


def test_member_missing_provider_role_cannot_choose_a_namespace() -> None:
    from qi_tuna_account_binding import account_digest

    member = {"id": 11, "team_id": 7, "user_id": 31, "is_active": True}
    with pytest.raises(ValueError):
        account_digest("https://api.quantum-inspire.com", 11, member, b"a" * 32)


@pytest.mark.parametrize(
    "member",
    [
        {"id": True, "team_id": 7, "user_id": 31, "role": "member", "is_active": True},
        {"id": 11, "team_id": True, "user_id": 31, "role": "member", "is_active": True},
        {"id": 11, "team_id": 0, "user_id": 31, "role": "member", "is_active": True},
        {"id": 11, "team_id": 7, "user_id": 31, "role": "member", "is_active": 1},
        {"id": 11, "user_id": 31, "role": "member", "is_active": True},
        {"id": 11, "team_id": 7, "user_id": True, "role": "member", "is_active": True},
        {"id": 11, "team_id": 7, "user_id": 31, "role": "invalid", "is_active": True},
    ],
)
def test_malformed_member_cannot_select_a_namespace(member: dict[str, object]) -> None:
    from qi_tuna_account_binding import account_digest

    with pytest.raises(ValueError):
        account_digest("https://api.quantum-inspire.com", 11, member, b"a" * 32)


def test_host_and_shared_secret_are_required() -> None:
    from qi_tuna_account_binding import account_digest

    member = {"id": 11, "team_id": 7, "user_id": 31, "role": "member", "is_active": True}
    with pytest.raises(ValueError):
        account_digest("https://other.example", 11, member, b"a" * 32)
    with pytest.raises(ValueError):
        account_digest("https://api.quantum-inspire.com", 11, member, b"short")
    if account_digest("https://api.quantum-inspire.com", 11, member, b"a" * 32) == account_digest(
        "https://api.quantum-inspire.com", 11, member, b"b" * 32
    ):
        raise AssertionError("distinct namespace secrets selected the same key")


def test_members_of_same_team_cannot_consume_approval_twice(tmp_path: Path) -> None:
    from qi_tuna_account_binding import account_digest
    from qi_tuna_consumption_marker import consume

    first = account_digest(
        "https://api.quantum-inspire.com",
        11,
        {"id": 11, "team_id": 7, "user_id": 31, "role": "member", "is_active": True},
        b"a" * 32,
    )
    second = account_digest(
        "https://api.quantum-inspire.com",
        12,
        {"id": 12, "team_id": 7, "user_id": 32, "role": "admin", "is_active": True},
        b"a" * 32,
    )
    directory = os.open(tmp_path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        consume(directory, first, b"b" * 32, b"c" * 32)
        with pytest.raises(FileExistsError):
            consume(directory, second, b"b" * 32, b"c" * 32)
    finally:
        os.close(directory)
