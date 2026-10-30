"""Compare supplied identity bindings within one serialized process.

The caller authenticates the approved binding and every observation, verifies
issuer and audience, and enforces refusal across restart and account users.
This guard performs no provider I/O and cannot establish those properties.
"""

import hmac

from qi_tuna_subject_binding import SubjectBinding


def _snapshot(binding: SubjectBinding) -> tuple[bytes, bytes, bytes, bytes]:
    if type(binding) is not SubjectBinding:
        raise ValueError("identity binding must contain four 32-byte digests")
    try:
        digests = (binding.subject_digest, binding.team_digest, binding.user_digest, binding.member_digest)
    except AttributeError as error:
        raise ValueError("identity binding must contain four 32-byte digests") from error
    if any(type(digest) is not bytes or len(digest) != 32 for digest in digests):
        raise ValueError("identity binding must contain four 32-byte digests")
    return digests


class IdentityContinuity:
    """Latch a refusal after an invalid or changed identity in one process."""

    __slots__ = ("_approved", "_refused")
    _approved: tuple[bytes, bytes, bytes, bytes]
    _refused: bool

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("identity guard state is read-only")

    def __delattr__(self, name: str) -> None:
        raise AttributeError("identity guard state is read-only")

    def __init__(self, approved: SubjectBinding) -> None:
        object.__setattr__(self, "_approved", _snapshot(approved))
        object.__setattr__(self, "_refused", False)

    def check(self, observed: SubjectBinding) -> None:
        if self._refused:
            raise ValueError("identity guard already refused this attempt")
        try:
            snapshot = _snapshot(observed)
            comparisons = [
                hmac.compare_digest(expected, actual) for expected, actual in zip(self._approved, snapshot, strict=True)
            ]
            if not all(comparisons):
                raise ValueError("identity differs from approved binding")
        except ValueError:
            object.__setattr__(self, "_refused", True)
            raise
