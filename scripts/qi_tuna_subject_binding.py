"""Check a caller-verified OAuth subject against supplied QI identity records.

The caller verifies the token signature and claims, authenticates and retains
the exact provider readbacks, establishes pagination and subject semantics, and
protects the namespace secret. This module contacts no provider and cannot
establish authentication, admission or the timing of its supplied records.
"""

import hmac
from dataclasses import dataclass

from qi_tuna_account_binding import HOST, account_digest
from qi_tuna_source_association import _json_object

DOMAIN = b"gororoba-qi-subject-v1\0https://api.quantum-inspire.com\0"
USER_DOMAIN = b"gororoba-qi-user-v1\0https://api.quantum-inspire.com\0"
MEMBER_DOMAIN = b"gororoba-qi-member-v1\0https://api.quantum-inspire.com\0"


@dataclass(frozen=True)
class SubjectBinding:
    """Keyed identities for an already authenticated subject and team."""

    subject_digest: bytes
    team_digest: bytes
    user_digest: bytes
    member_digest: bytes


def bind_subject(subject: str, user_bytes: bytes, member_bytes: bytes, member_id: int, secret: bytes) -> SubjectBinding:
    """Validate a supplied user/member chain and derive private keyed identities."""
    if type(subject) is not str or not subject or len(subject) > 256:
        raise ValueError("verified subject must be a nonempty bounded string")
    try:
        encoded_subject = subject.encode("utf-8")
    except UnicodeEncodeError as error:
        raise ValueError("verified subject must be valid UTF-8") from error
    user = _json_object(user_bytes)
    member = _json_object(member_bytes)
    user_id = user.get("id")
    observed_subject = user.get("oidc_sub")
    member_user_id = member.get("user_id")
    if (
        type(user_id) is not int
        or user_id < 1
        or type(member_user_id) is not int
        or member_user_id != user_id
        or type(observed_subject) is not str
        or observed_subject != subject
        or user.get("is_active") is not True
    ):
        raise ValueError("subject, user and member records are inconsistent")
    team = account_digest(HOST, member_id, member, secret)
    try:
        encoded_user = str(user_id).encode("ascii")
        encoded_member = str(member_id).encode("ascii")
    except ValueError as error:
        raise ValueError("identity cannot be encoded") from error
    role = member["role"].encode("ascii")
    return SubjectBinding(
        hmac.digest(secret, DOMAIN + encoded_subject, "sha256"),
        team,
        hmac.digest(secret, USER_DOMAIN + encoded_user, "sha256"),
        hmac.digest(secret, MEMBER_DOMAIN + encoded_member + b"\0" + role, "sha256"),
    )
