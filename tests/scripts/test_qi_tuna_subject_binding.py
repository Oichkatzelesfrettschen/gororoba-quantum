"""Bind a verified subject to supplied user and member records without provider I/O."""

import hmac
import json

import pytest


def test_subject_snapshot_consistency_and_digest_separation() -> None:
    from qi_tuna_account_binding import account_digest
    from qi_tuna_subject_binding import bind_subject

    secret = bytes(range(32))
    subject = "synthetic-subject"
    user = {"id": 11, "oidc_sub": subject, "is_active": True}
    member = {"id": 12, "team_id": 13, "user_id": 11, "role": "member", "is_active": True}
    user_bytes = json.dumps(user).encode()
    member_bytes = json.dumps(member).encode()
    binding = bind_subject(subject, user_bytes, member_bytes, 12, secret)
    if binding.team_digest != account_digest("https://api.quantum-inspire.com", 12, member, secret):
        raise AssertionError("verified subject binding changed the team namespace")
    expected_subject = hmac.digest(
        secret, b"gororoba-qi-subject-v1\0https://api.quantum-inspire.com\0" + subject.encode(), "sha256"
    )
    if binding.subject_digest != expected_subject:
        raise AssertionError("subject digest differs from the independently specified HMAC")
    expected_user = hmac.digest(secret, b"gororoba-qi-user-v1\0https://api.quantum-inspire.com\0" + b"11", "sha256")
    expected_member = hmac.digest(
        secret, b"gororoba-qi-member-v1\0https://api.quantum-inspire.com\0" + b"12\0member", "sha256"
    )
    if binding.user_digest != expected_user or binding.member_digest != expected_member:
        raise AssertionError("user or member digest differs from the independently specified HMAC")
    other_user = {**user, "oidc_sub": "other-subject"}
    other_binding = bind_subject("other-subject", json.dumps(other_user).encode(), member_bytes, 12, secret)
    if other_binding.team_digest != binding.team_digest or other_binding.subject_digest == binding.subject_digest:
        raise AssertionError("a changed subject in the same team did not change its keyed identity")
    for changed_subject, changed_user, changed_member, changed_id in (
        ("other-subject", user, member, 12),
        (subject, {**user, "id": 99}, member, 12),
        (subject, {**user, "oidc_sub": "other-subject"}, member, 12),
        (subject, {**user, "is_active": False}, member, 12),
        (subject, user, {**member, "user_id": True}, 12),
        (subject, user, {**member, "is_active": False}, 12),
        (subject, user, member, 99),
    ):
        with pytest.raises(ValueError):
            bind_subject(
                changed_subject,
                json.dumps(changed_user).encode(),
                json.dumps(changed_member).encode(),
                changed_id,
                secret,
            )


def test_subject_binding_rejects_duplicate_keys_and_boolean_user_ids() -> None:
    from qi_tuna_subject_binding import bind_subject

    member = b'{"id":12,"team_id":13,"user_id":1,"role":"member","is_active":true}'
    for user in (
        b'{"id":true,"oidc_sub":"subject","is_active":true}',
        b'{"id":1,"id":1,"oidc_sub":"subject","is_active":true}',
        b'{"id":1,"oidc_sub":"subject","is_active":1}',
        b'{"id":1,"oidc_sub":"subject","is_active":true,"extra":NaN}',
    ):
        with pytest.raises(ValueError):
            bind_subject("subject", user, member, 12, bytes(32))
    good_user = b'{"id":1,"oidc_sub":"subject","is_active":true}'
    for bad_subject in ("", "x" * 257, "\ud800"):
        with pytest.raises(ValueError):
            bind_subject(bad_subject, good_user, member, 12, bytes(32))
    with pytest.raises(ValueError):
        bind_subject("subject", good_user, member, 12, b"short")
    with pytest.raises(ValueError):
        bind_subject("subject", good_user, member.replace(b'"id":12', b'"id":12,"id":12'), 12, bytes(32))


def test_binding_detects_user_and_member_changes_with_same_subject_and_team() -> None:
    from qi_tuna_subject_binding import SubjectBinding, bind_subject

    subject = "synthetic-subject"
    secret = bytes(range(32))
    user = {"id": 11, "oidc_sub": subject, "is_active": True}
    member = {"id": 12, "team_id": 13, "user_id": 11, "role": "member", "is_active": True}

    def bind(user_record: dict[str, object], member_record: dict[str, object], member_id: int) -> SubjectBinding:
        return bind_subject(
            subject, json.dumps(user_record).encode(), json.dumps(member_record).encode(), member_id, secret
        )

    original = bind(user, member, 12)
    changed_user = bind({**user, "id": 22}, {**member, "user_id": 22}, 12)
    changed_member = bind(user, {**member, "id": 24}, 24)
    changed_role = bind(user, {**member, "role": "admin"}, 12)
    if any(
        (item.subject_digest, item.team_digest) != (original.subject_digest, original.team_digest)
        for item in (changed_user, changed_member, changed_role)
    ):
        raise AssertionError("a same-subject, same-team transition changed those identities")
    if changed_user.user_digest == original.user_digest or changed_user.member_digest != original.member_digest:
        raise AssertionError("user transition changed the wrong identity fields")
    if any(
        item.user_digest != original.user_digest or item.member_digest == original.member_digest
        for item in (changed_member, changed_role)
    ):
        raise AssertionError("member or role transition changed the wrong identity fields")


def test_unicode_subject_encodings_and_escaped_duplicate_keys() -> None:
    from qi_tuna_subject_binding import bind_subject

    subject = "synthetic-é"
    user = {"id": 11, "oidc_sub": subject, "is_active": True}
    member = b'{"id":12,"team_id":13,"user_id":11,"role":"member","is_active":true}'
    literal = json.dumps(user, ensure_ascii=False).encode("utf-8")
    escaped = json.dumps(user, ensure_ascii=True).encode("ascii")
    if bind_subject(subject, literal, member, 12, bytes(32)) != bind_subject(subject, escaped, member, 12, bytes(32)):
        raise AssertionError("equivalent JSON encodings changed the subject binding")
    for invalid in (
        b'{"id":11,"oidc_sub":"\xff","is_active":true}',
        b'{"id":11,"\\u0069d":11,"oidc_sub":"synthetic-\\u00e9","is_active":true}',
    ):
        with pytest.raises(ValueError):
            bind_subject(subject, invalid, member, 12, bytes(32))
    decomposed_subject = "synthetic-e\u0301"
    decomposed_user = {**user, "oidc_sub": decomposed_subject}
    normalized = bind_subject(subject, literal, member, 12, bytes(32))
    decomposed = bind_subject(decomposed_subject, json.dumps(decomposed_user).encode(), member, 12, bytes(32))
    if normalized.subject_digest == decomposed.subject_digest:
        raise AssertionError("distinct opaque subject strings collapsed under Unicode normalization")
