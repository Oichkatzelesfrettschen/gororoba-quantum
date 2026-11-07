"""The iterated-job billing statement that versioned producers write in place of the full-cap wording.

`qd_platform.job_billing` holds the rule: one credit per job plus 1e-6 per billed shot, where an iterated job
bills the smaller of the shots it used and its largest iteration's max_shots, and the cap in full when its
result reports no shots used. docs/evidence/quandela-billing-rule-successor/README.md lists the pinned records
whose fields state the cap as the charge and the producers that wrote them; each producer's `_v2` successor
rebuilds its records and replaces only those fields through `supersede`.
"""

from __future__ import annotations

from typing import Any

RULE_SOURCE = "qd_platform.job_billing, docs/runbooks/quandela-credit-optimization.md section 'The billing rule'"
RULE = (
    "1 credit per job plus 1e-6 per billed shot; an iterated job bills the smaller of the shots it used and its "
    "largest iteration's max_shots, and that cap in full when its result reports no shots used "
    f"({RULE_SOURCE}); a credit figure computed at max_shots is the job's ceiling"
)


def supersede(record: dict[str, Any], path: tuple[str, ...], old: str, new: str) -> None:
    """Replace the string at `path` in place, refusing a record whose current value is not `old`.

    The check ties a successor to the exact wording its pinned producer emits, so a producer that changes the
    field under it fails the build instead of passing a second, unreviewed statement through.
    """
    parent: Any = record
    for key in path[:-1]:
        parent = parent[key]
    current = parent.get(path[-1]) if isinstance(parent, dict) else None
    if current != old:
        raise ValueError(f"/{'/'.join(path)} reads {current!r}, not the superseded wording {old!r}")
    parent[path[-1]] = new
