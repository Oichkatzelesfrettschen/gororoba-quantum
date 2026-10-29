"""Derive a private team namespace from a supplied Quantum Inspire member record.

The caller authenticates and retains a duplicate-key-rejected member readback,
protects and shares the same high-entropy secret and marker namespace, and
prevents concurrent mutation of the record. This function reads no provider data
and cannot establish those trust or cross-host coordination properties.
"""

import hmac
from collections.abc import Mapping

HOST = "https://api.quantum-inspire.com"
DOMAIN = b"gororoba-qi-team-namespace-v1\0https://api.quantum-inspire.com\0"


def account_digest(host: str, member_id: int, member: Mapping[str, object], secret: bytes) -> bytes:
    """Derive a keyed team digest from one already authenticated member record."""
    if type(host) is not str or host != HOST or type(member_id) is not int or member_id < 1:
        raise ValueError("provider host or member identity differs")
    if type(secret) is not bytes or len(secret) != 32:
        raise ValueError("namespace secret must contain 32 bytes")
    if type(member) is not dict:
        raise ValueError("member must be a plain JSON object")
    observed_id = member.get("id")
    team_id = member.get("team_id")
    user_id = member.get("user_id")
    role = member.get("role")
    if (
        type(observed_id) is not int
        or observed_id != member_id
        or type(team_id) is not int
        or team_id < 1
        or type(user_id) is not int
        or user_id < 1
        or type(role) is not str
        or role not in ("member", "admin")
        or member.get("is_active") is not True
    ):
        raise ValueError("member record does not establish an active team")
    try:
        encoded_team = str(team_id).encode("ascii")
    except ValueError as error:
        raise ValueError("team identity cannot be encoded") from error
    return hmac.digest(secret, DOMAIN + encoded_team, "sha256")
