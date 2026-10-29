"""An identity mismatch must stop later checks in the same guard instance."""

import json
from dataclasses import replace

import pytest


@pytest.mark.parametrize("field", ["subject_digest", "team_digest", "user_digest", "member_digest"])
def test_each_identity_change_latches_refusal(field: str) -> None:
    from qi_tuna_identity_guard import IdentityContinuity
    from qi_tuna_subject_binding import SubjectBinding

    approved = SubjectBinding(bytes([1]) * 32, bytes([2]) * 32, bytes([3]) * 32, bytes([4]) * 32)
    guard = IdentityContinuity(approved)
    guard.check(approved)
    with pytest.raises(ValueError):
        guard.check(replace(approved, **{field: bytes([9]) * 32}))
    with pytest.raises(ValueError):
        guard.check(approved)


def test_malformed_observation_latches_refusal_and_invalid_approval_is_rejected() -> None:
    from qi_tuna_identity_guard import IdentityContinuity
    from qi_tuna_subject_binding import SubjectBinding

    approved = SubjectBinding(bytes([1]) * 32, bytes([2]) * 32, bytes([3]) * 32, bytes([4]) * 32)
    with pytest.raises(ValueError):
        IdentityContinuity(replace(approved, member_digest=b"short"))
    guard = IdentityContinuity(approved)
    with pytest.raises(ValueError):
        guard.check(replace(approved, subject_digest=b"short"))
    with pytest.raises(ValueError):
        guard.check(approved)


def test_guard_refuses_coherent_member_transition_from_subject_binding() -> None:
    from qi_tuna_identity_guard import IdentityContinuity
    from qi_tuna_subject_binding import bind_subject

    subject = "synthetic-subject"
    secret = bytes(range(32))
    user = {"id": 11, "oidc_sub": subject, "is_active": True}
    member = {"id": 12, "team_id": 13, "user_id": 11, "role": "member", "is_active": True}
    approved = bind_subject(subject, json.dumps(user).encode(), json.dumps(member).encode(), 12, secret)
    changed = bind_subject(subject, json.dumps(user).encode(), json.dumps({**member, "id": 24}).encode(), 24, secret)
    guard = IdentityContinuity(approved)
    guard.check(approved)
    with pytest.raises(ValueError):
        guard.check(changed)
    with pytest.raises(ValueError):
        guard.check(approved)


def test_guard_snapshots_approved_binding_before_caller_mutation() -> None:
    from qi_tuna_identity_guard import IdentityContinuity
    from qi_tuna_subject_binding import SubjectBinding

    approved = SubjectBinding(bytes([1]) * 32, bytes([2]) * 32, bytes([3]) * 32, bytes([4]) * 32)
    guard = IdentityContinuity(approved)
    approved.__dict__["subject_digest"] = bytes([9]) * 32
    with pytest.raises(ValueError):
        guard.check(approved)


def test_missing_observation_field_latches_refusal() -> None:
    from qi_tuna_identity_guard import IdentityContinuity
    from qi_tuna_subject_binding import SubjectBinding

    approved = SubjectBinding(bytes([1]) * 32, bytes([2]) * 32, bytes([3]) * 32, bytes([4]) * 32)
    guard = IdentityContinuity(approved)
    incomplete = object.__new__(SubjectBinding)
    with pytest.raises(ValueError):
        guard.check(incomplete)
    with pytest.raises(ValueError):
        guard.check(approved)
