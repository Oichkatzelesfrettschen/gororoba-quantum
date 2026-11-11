"""Six-state linear-effect contrasts with observed trial and acceptance populations.

The states f, g, +, -, +i and -i obey rho_+ + rho_- = rho_f + rho_g and its imaginary-basis analogue.
A fixed effect therefore gives zero contrasts of *unconditional* selected-event probabilities. Conditioning on
acceptance replaces a linear probability by a ratio of linear forms, so the corresponding conditional contrasts
are diagnostics, not linearity tests. A selected count divided by genuine attempted trials gives the weighted
endpoint directly, including a state with no accepted event whose conditional probability is undefined.

Provider counters retain the population, status, scope, source and termination metadata. Detection events,
filtered samples, requested caps and modeled exposure never stand in for observed source triggers or circuit
executions. A genuine observed denominator remains descriptive under a stopping rule; independent trials alone
do not supply its fixed-sample covariance. The caller supplies a joint rate covariance or declares independent,
fixed-attempt sampling without recorded termination. The latter gives a plug-in reference, not a confidence
bound or a calibrated significance test. No p-value or physical-origin claim follows from this module.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import ArrayLike

from measurement_statistics import MAX_EXACT_COUNT, covariance_matrix
from provider_counters import Counter, Population, Status

STATE_LABELS = ("f", "g", "+", "-", "+i", "-i")
CONTRAST_LABELS = ("real", "imaginary")
CONTRAST_COEFFICIENTS = ((-1, -1, 1, 1, 0, 0), (-1, -1, 0, 0, 1, 1))
_TRIAL_POPULATIONS = frozenset((Population.SOURCE_TRIGGER, Population.CIRCUIT_EXECUTION))
MatrixRecord = tuple[tuple[float, ...], ...]


class AcceptanceError(ValueError):
    """An acceptance record or its declared statistical contract is inconsistent."""


def _text(value: object, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise AcceptanceError(f"{name} must be a nonempty string")


def _count(value: object, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0 or value > MAX_EXACT_COUNT:
        raise AcceptanceError(f"{name} must be an integer in [0, 2**53], excluding bool")


@dataclass(frozen=True)
class AcceptanceCounts:
    """One state's disjoint selected, other-accepted and rejected event counts.

    selected is a subset of accepted. scope identifies this state's population, not an aggregate containing
    several preparations; source identifies the selected and accepted count source. denominator retains the
    candidate provider counter even when its semantics do not identify genuine attempted trials.
    """

    state: str
    selected: int
    accepted: int
    denominator: Counter
    scope: str
    source: str

    def __post_init__(self) -> None:
        if not isinstance(self.state, str) or self.state not in STATE_LABELS:
            raise AcceptanceError(f"state must be one of {STATE_LABELS}")
        _count(self.selected, "selected")
        _count(self.accepted, "accepted")
        if self.selected > self.accepted:
            raise AcceptanceError("selected exceeds accepted")
        _text(self.scope, "scope")
        _text(self.source, "source")
        if not isinstance(self.denominator, Counter):
            raise AcceptanceError("denominator must be a provider_counters.Counter")
        counter = self.denominator
        if not isinstance(counter.population, Population) or not isinstance(counter.status, Status):
            raise AcceptanceError("denominator population and status must use the provider counter enums")
        _text(counter.name, "denominator name")
        _text(counter.source, "denominator source")
        if counter.scope != self.scope:
            raise AcceptanceError("denominator scope differs from the selected and accepted count scope")
        if counter.terminated_by is not None:
            _text(counter.terminated_by, "denominator terminated_by")
        if counter.status is Status.OBSERVED and counter.population in _TRIAL_POPULATIONS:
            _count(counter.value, "observed attempted count")
            if counter.value is None or self.accepted > counter.value:
                raise AcceptanceError("accepted exceeds observed attempted trials")

    def record(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "selected": self.selected,
            "accepted": self.accepted,
            "denominator": self.denominator.record(),
            "scope": self.scope,
            "source": self.source,
        }


@dataclass(frozen=True)
class AcceptanceEstimate:
    """Conditional and unconditional rates retain different denominators and availability."""

    counts: AcceptanceCounts
    conditional_probability: float | None
    acceptance_probability: float | None
    unconditional_probability: float | None
    unconditional_reason: str | None

    def record(self) -> dict[str, Any]:
        return {
            **self.counts.record(),
            "conditional_probability": self.conditional_probability,
            "acceptance_probability": self.acceptance_probability,
            "unconditional_probability": self.unconditional_probability,
            "unconditional_reason": self.unconditional_reason,
        }


def estimate_acceptance(counts: AcceptanceCounts) -> AcceptanceEstimate:
    """Preserve conditional information when genuine attempted trials remain unidentified."""
    if not isinstance(counts, AcceptanceCounts):
        raise AcceptanceError("counts must be AcceptanceCounts")
    conditional = counts.selected / counts.accepted if counts.accepted else None
    denominator = counts.denominator
    reason = None
    if denominator.status is not Status.OBSERVED:
        reason = f"denominator status {denominator.status.value} does not supply observed attempted trials"
    elif denominator.population not in _TRIAL_POPULATIONS:
        reason = f"denominator population {denominator.population.value} is not source triggers or circuit executions"
    elif denominator.value == 0:
        reason = "zero observed attempted trials leave the unconditional probability undefined"
    if reason is not None:
        return AcceptanceEstimate(counts, conditional, None, None, reason)
    total = denominator.value
    if not isinstance(total, int) or isinstance(total, bool) or total <= 0:
        raise AcceptanceError("observed attempted trials must be a positive integer")
    return AcceptanceEstimate(counts, conditional, counts.accepted / total, counts.selected / total, None)


@dataclass(frozen=True)
class SixStateConformance:
    """Two unconditional linear-effect endpoints and their jointly qualified uncertainty."""

    estimates: tuple[AcceptanceEstimate, ...]
    conditional_contrasts: tuple[float | None, float | None]
    unconditional_contrasts: tuple[float | None, float | None]
    rate_covariance: MatrixRecord | None
    contrast_covariance: MatrixRecord | None
    contrast_standard_errors: tuple[float, float] | None
    uncertainty_model: str | None
    uncertainty_reason: str | None
    independent_trials: bool
    fixed_attempts: bool

    def record(self) -> dict[str, Any]:
        return {
            "schema": "six-state-acceptance-v1",
            "state_order": list(STATE_LABELS),
            "contrast_order": list(CONTRAST_LABELS),
            "contrast_coefficients": [list(row) for row in CONTRAST_COEFFICIENTS],
            "estimates": [estimate.record() for estimate in self.estimates],
            "conditional_contrasts": dict(zip(CONTRAST_LABELS, self.conditional_contrasts, strict=True)),
            "unconditional_contrasts": dict(zip(CONTRAST_LABELS, self.unconditional_contrasts, strict=True)),
            "rate_covariance": None if self.rate_covariance is None else [list(row) for row in self.rate_covariance],
            "contrast_covariance": (
                None if self.contrast_covariance is None else [list(row) for row in self.contrast_covariance]
            ),
            "contrast_standard_errors": (
                None
                if self.contrast_standard_errors is None
                else dict(zip(CONTRAST_LABELS, self.contrast_standard_errors, strict=True))
            ),
            "uncertainty": {
                "model": self.uncertainty_model,
                "reason": self.uncertainty_reason,
                "independent_trials": self.independent_trials,
                "fixed_attempts": self.fixed_attempts,
            },
        }


def _contrast(values: Sequence[float | None], indices: tuple[int, int, int, int]) -> float | None:
    a, b, f, g = (values[index] for index in indices)
    if a is None or b is None or f is None or g is None:
        return None
    return a + b - f - g


def _matrix_record(matrix: np.ndarray) -> MatrixRecord:
    return tuple(tuple(float(value) for value in row) for row in matrix)


def analyze_six_state(
    records: Sequence[AcceptanceCounts],
    *,
    independent_trials: bool = False,
    fixed_attempts: bool = False,
    rate_covariance: ArrayLike | None = None,
) -> SixStateConformance:
    """Evaluate six-state contrasts in canonical f,g,+,-,+i,-i order.

    A supplied rate_covariance is the joint covariance of the six *unconditional selected-rate estimators*,
    in canonical state order, not a per-event covariance. It can represent shared drift and a qualified stopping
    rule. Combining it with independent_trials raises because the two uncertainty contracts differ.

    Without a supplied covariance, independent_trials and fixed_attempts must both be True and every denominator
    must lack termination metadata before the function returns the binomial plug-in covariance. Recorded
    stopping requires a supplied covariance even if the caller labels attempts fixed. Missing or zero trial
    denominators preserve any available endpoints but leave joint uncertainty unidentified.
    """
    if not isinstance(independent_trials, bool) or not isinstance(fixed_attempts, bool):
        raise AcceptanceError("independent_trials and fixed_attempts must be bool")
    if rate_covariance is not None and independent_trials:
        raise AcceptanceError("supply rate_covariance or declare independent_trials, not both")
    if len(records) != len(STATE_LABELS) or any(not isinstance(row, AcceptanceCounts) for row in records):
        raise AcceptanceError("records must contain exactly six AcceptanceCounts")
    by_state = {row.state: row for row in records}
    if set(by_state) != set(STATE_LABELS):
        raise AcceptanceError("records must contain each canonical state exactly once")
    estimates = tuple(estimate_acceptance(by_state[state]) for state in STATE_LABELS)
    conditional = [estimate.conditional_probability for estimate in estimates]
    unconditional = [estimate.unconditional_probability for estimate in estimates]
    conditional_contrasts = (_contrast(conditional, (2, 3, 0, 1)), _contrast(conditional, (4, 5, 0, 1)))
    unconditional_contrasts = (_contrast(unconditional, (2, 3, 0, 1)), _contrast(unconditional, (4, 5, 0, 1)))
    complete = all(rate is not None for rate in unconditional)
    covariance = None
    model = None
    reason = None
    if rate_covariance is not None:
        if not complete:
            raise AcceptanceError("rate_covariance requires six identified unconditional rate estimators")
        covariance = covariance_matrix(rate_covariance, dimension=6, name="unconditional rate covariance")
        model = "supplied_joint_rate_covariance"
    elif not complete:
        reason = "joint uncertainty requires positive observed attempted counts for all six states"
    elif not independent_trials or not fixed_attempts:
        reason = "supply joint rate covariance or declare both independent_trials and fixed_attempts"
    elif any(estimate.counts.denominator.terminated_by is not None for estimate in estimates):
        reason = "recorded stopping requires a supplied sampling-design covariance"
    else:
        selected = np.array([estimate.counts.selected for estimate in estimates], dtype=float)
        total = np.array([estimate.counts.denominator.value for estimate in estimates], dtype=float)
        probabilities = selected / total
        covariance = np.diag(probabilities * (1.0 - probabilities) / total)
        model = "independent_fixed_attempts_binomial_plugin"
        if np.any((selected == 0) | (selected == total)):
            reason = "boundary-count plug-in variance can vanish and does not supply a finite-sample confidence bound"
    contrast_covariance = None
    standard_errors = None
    if covariance is not None:
        coefficients = np.asarray(CONTRAST_COEFFICIENTS, dtype=float)
        try:
            with np.errstate(over="raise", invalid="raise"):
                projected_covariance = coefficients @ covariance @ coefficients.T
                if not np.isfinite(projected_covariance).all():
                    raise AcceptanceError("contrast covariance arithmetic overflows float64")
                contrast_covariance = covariance_matrix(projected_covariance, dimension=2, name="contrast covariance")
        except FloatingPointError as error:
            raise AcceptanceError("contrast covariance arithmetic overflows float64") from error
        diagonal = np.maximum(np.diag(contrast_covariance), 0.0)
        standard_errors = (float(np.sqrt(diagonal[0])), float(np.sqrt(diagonal[1])))
    return SixStateConformance(
        estimates,
        conditional_contrasts,
        unconditional_contrasts,
        None if covariance is None else _matrix_record(covariance),
        None if contrast_covariance is None else _matrix_record(contrast_covariance),
        standard_errors,
        model,
        reason,
        independent_trials,
        fixed_attempts,
    )
