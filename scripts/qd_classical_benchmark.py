"""Certified classical fidelity benchmarks for heralded qubit teleportation, from the separable Choi cone.

A classical (measure-and-prepare) strategy with post-selection is a
trace-non-increasing entanglement-breaking map E, and its Choi operator
``J = sum_ij |i><j| (x) E(|i><j|)`` on input (x) output is separable with
``tr_out J <= I``. For one input qubit and one output qubit the separable cone
equals the PPT cone (Horodecki, Phys. Lett. A 223, 1 (1996)), so the
semidefinite program over ``J >= 0`` and ``J^Gamma >= 0`` (partial transpose
on the input) gives the exact classical optimum. An input ``psi`` succeeds
with probability ``tr[J (psi^T (x) I)]`` and reaches unnormalized fidelity
``tr[J (psi^T (x) psi)]``.

Three figures of merit, each over an ensemble of pure inputs with priors p_j:

- pooled, free post-selection (no success profile): the conditional fidelity
  pooled over accepted trials, ``sum p_j f_j / sum p_j s_j``, maximized over
  every classical strategy whatever its success profile. Homogeneity lets the
  program fix ``sum p_j s_j = 1``. The uniform six-state ensemble gives 2/3,
  the four BB84 states 3/4.
- pooled with a success profile: the same ratio over strategies that
  reproduce a given ``s_j`` for every input.
- average with a success profile: the mean of per-input conditional
  fidelities, ``sum p_j f_j / s_j``, over strategies that reproduce ``s_j``.

The uniform six-state ensemble keeps the classical bound at 2/3 in both
figures under every realizable profile the test exercises, tilted ones
included; unequal priors raise it (3/4 when the Z eigenstates carry weight
1/4 each), and the pooled figure of joint_teleportation_scores weights each
input by its matching-basis attempts, so attempts_benchmark supplies the
bound for an unequal allocation.

Every success profile of a map on a qubit is affine in the Bloch vector,
``s(r) = m_0 + m . r``; realizable_profile fits that form to six-state data
and reports the residual a measured profile carries.

Every bound comes from a certificate built on the dual program: the dual
variables are projected onto the PSD cone, and the residual operator's least
eigenvalue enters through a bound on ``tr J`` (``1/mu`` under free
post-selection, mu the least eigenvalue of the prior-weighted input state;
``tr K`` when the profile fixes the acceptance operator ``K = tr_out J``; 2
otherwise). The returned value therefore upper-bounds every classical
strategy up to floating-point rounding whatever the solver's accuracy, the
primal optimum supplies the achieving Choi operator, and a
certified-minus-achieved gap above GAP_LIMIT refuses the run.

tests/scripts/test_qd_classical_benchmark.py holds the contract. Usage:
"$PYTHON" scripts/qd_classical_benchmark.py --tables
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

import cvxpy as cp
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gororoba_quantum"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from qd_network_protocol import SIX_STATES, ProtocolError  # noqa: E402

from parallel import ordered_map  # noqa: E402

I2 = np.eye(2, dtype=complex)
SOLVER = "CLARABEL"
FEASIBILITY_TOLERANCE = 1e-7
GAP_LIMIT = 1e-6
FIGURES = ("pooled", "average")
DIMS = (2, 2)
# Output-basis isometries I (x) |a>, so tr_out J = sum_a E_a^T J E_a.
OUTPUT_RAILS = tuple(np.kron(np.eye(2), np.eye(2)[:, [a]]) for a in range(2))
SIX_LABELS = tuple(label for label, _, _, _ in SIX_STATES)
SIX_AMPLITUDES = {label: amps for label, amps, _, _ in SIX_STATES}


@dataclass(frozen=True)
class Benchmark:
    """A certified classical bound, the primal value that reaches it and the achieving Choi operator."""

    figure: str
    certified: float
    achieved: float
    choi: np.ndarray

    @property
    def gap(self) -> float:
        return self.certified - self.achieved


def partial_transpose_input(matrix: np.ndarray) -> np.ndarray:
    """Partial transpose on the input factor of a 4 x 4 operator ordered input (x) output."""
    return matrix.reshape(2, 2, 2, 2).transpose(2, 1, 0, 3).reshape(4, 4)


def partial_trace_output(matrix: np.ndarray) -> np.ndarray:
    return np.einsum("iaja->ij", matrix.reshape(2, 2, 2, 2))


def _psd_part(matrix: np.ndarray) -> np.ndarray:
    hermitian = (matrix + matrix.conj().T) / 2.0
    values, vectors = np.linalg.eigh(hermitian)
    clipped: np.ndarray = (vectors * np.clip(values, 0.0, None)) @ vectors.conj().T
    return clipped


def _least_eigenvalue(matrix: np.ndarray) -> float:
    return float(np.linalg.eigvalsh((matrix + matrix.conj().T) / 2.0).min())


def _projectors(states: Sequence[tuple[complex, complex]]) -> list[np.ndarray]:
    projectors = []
    for amplitudes in states:
        vector = np.array(amplitudes, dtype=complex)
        if vector.shape != (2,) or abs(float(np.vdot(vector, vector).real) - 1.0) > 1e-12:
            raise ProtocolError(f"input {amplitudes!r} is not a normalized qubit state")
        projectors.append(np.outer(vector, vector.conj()))
    return projectors


def _require_priors(priors: Sequence[float], count: int) -> np.ndarray:
    weights = np.array(priors, dtype=float)
    if weights.shape != (count,):
        raise ProtocolError(f"{count} inputs need {count} priors")
    if not np.all(np.isfinite(weights)) or weights.min() < 0.0 or abs(weights.sum() - 1.0) > 1e-12:
        raise ProtocolError("priors must be finite, nonnegative and sum to 1")
    return weights


def _require_profile(success: Sequence[float], count: int) -> np.ndarray:
    profile = np.array(success, dtype=float)
    if profile.shape != (count,):
        raise ProtocolError(f"{count} inputs need {count} success probabilities")
    if not np.all(np.isfinite(profile)) or profile.min() <= 0.0 or profile.max() > 1.0:
        raise ProtocolError("every success probability must lie in (0, 1]")
    return profile


def _require_optimal(problem: cp.Problem, side: str) -> float:
    """The solver's value; an inaccurate optimum passes because the certificate and the gap check judge it."""
    if problem.status not in (cp.OPTIMAL, cp.OPTIMAL_INACCURATE):
        if side == "primal" and problem.status in (cp.INFEASIBLE, cp.INFEASIBLE_INACCURATE):
            raise ProtocolError(
                "no trace-non-increasing map reproduces the success profile; a qubit map's success is "
                "affine in the Bloch vector (realizable_profile)"
            )
        raise ProtocolError(f"the {side} program ended {problem.status}")
    return float(problem.value)


def _primal(
    objective: np.ndarray,
    constraints: list[tuple[np.ndarray, float]],
    trace_bounded: bool,
) -> tuple[float, np.ndarray]:
    choi = cp.Variable((4, 4), hermitian=True)
    rules = [choi >> 0, cp.partial_transpose(choi, DIMS, 0) >> 0]
    rules += [cp.real(cp.trace(choi @ operator)) == value for operator, value in constraints]
    if trace_bounded:
        rules.append(I2 - sum(rail.T @ choi @ rail for rail in OUTPUT_RAILS) >> 0)
    problem = cp.Problem(cp.Maximize(cp.real(cp.trace(choi @ objective))), rules)
    problem.solve(solver=SOLVER)
    value = _require_optimal(problem, "primal")
    matrix = np.array(choi.value, dtype=complex)
    violations = [
        -_least_eigenvalue(matrix),
        -_least_eigenvalue(partial_transpose_input(matrix)),
        *(abs(float(np.trace(matrix @ operator).real) - target) for operator, target in constraints),
    ]
    if trace_bounded:
        violations.append(-_least_eigenvalue(I2 - partial_trace_output(matrix)))
    if max(violations) > FEASIBILITY_TOLERANCE:
        raise ProtocolError(f"the primal optimum violates a constraint by {max(violations):.3g}")
    return value, matrix


def _free_postselection_bound(objective: np.ndarray, success: np.ndarray) -> float:
    """Certified ``max tr[J objective]`` over PPT J with ``tr[J success] = 1``, from ``t S - G - B^Gamma >= 0``."""
    level = cp.Variable()
    witness = cp.Variable((4, 4), hermitian=True)
    residual = level * success - objective - cp.partial_transpose(witness, DIMS, 0)
    problem = cp.Problem(cp.Minimize(level), [witness >> 0, residual >> 0])
    problem.solve(solver=SOLVER)
    _require_optimal(problem, "dual")
    bound = float(np.asarray(level.value))
    projected = _psd_part(np.array(witness.value, dtype=complex))
    slack = _least_eigenvalue(bound * success - objective - partial_transpose_input(projected))
    mu = _least_eigenvalue(success)
    return bound + max(0.0, -slack) / mu


PAULI_BASIS = (
    np.eye(2, dtype=complex),
    np.array([[0, 1], [1, 0]], dtype=complex),
    np.array([[0, -1j], [1j, 0]], dtype=complex),
    np.array([[1, 0], [0, -1]], dtype=complex),
)


def success_operator(
    projectors: Sequence[np.ndarray], profile: np.ndarray
) -> tuple[list[tuple[np.ndarray, float]], float | None]:
    """Independent linear constraints on ``K = tr_out J`` that reproduce the profile, and ``tr K`` when they fix K.

    Input ``psi`` succeeds with ``tr[K psi^T]``, and ``K = sum_a kappa_a sigma_a``
    in the Pauli basis gives one row ``tr[sigma_a psi^T]`` per input. The
    least-squares kappa must reproduce every success probability within
    FEASIBILITY_TOLERANCE, and a fixed K must lie between 0 and I; the right
    singular vectors of the rows give constraints without the redundancy an
    overcomplete ensemble carries, each ``v . kappa = tr[J ((v . sigma)/2 (x) I)]``.
    """
    rows = np.array([[float(np.trace(sigma @ rho.T).real) for sigma in PAULI_BASIS] for rho in projectors])
    kappa = np.linalg.lstsq(rows, profile, rcond=None)[0]
    residual = float(np.abs(rows @ kappa - profile).max())
    if residual > FEASIBILITY_TOLERANCE:
        raise ProtocolError(
            f"no trace-non-increasing map reproduces the success profile (residual {residual:.3g}); a qubit map's "
            "success is affine in the Bloch vector (realizable_profile)"
        )
    _, singular, right = np.linalg.svd(rows)
    rank = int(np.sum(singular > 1e-9))
    constraints = []
    for vector in right[:rank]:
        operator = sum((v * sigma for v, sigma in zip(vector, PAULI_BASIS, strict=True)), start=np.zeros((2, 2)))
        constraints.append((np.kron(operator / 2.0, I2), float(vector @ kappa)))
    if rank < 4:
        return constraints, None
    fixed = sum((k * sigma for k, sigma in zip(kappa, PAULI_BASIS, strict=True)), start=np.zeros((2, 2)))
    eigenvalues = np.linalg.eigvalsh(fixed)
    if eigenvalues.min() < -FEASIBILITY_TOLERANCE or eigenvalues.max() > 1.0 + FEASIBILITY_TOLERANCE:
        raise ProtocolError("the success profile needs an acceptance operator outside [0, I]")
    return constraints, 2.0 * float(kappa[0])


def _profile_bound(
    objective: np.ndarray, constraints: list[tuple[np.ndarray, float]], fixed_trace: float | None
) -> float:
    """Certified bound from ``sum y_i C_i + Z (x) I - G - B^Gamma >= 0``; a fixed K drops Z and sets ``tr J``."""
    multipliers = cp.Variable(len(constraints))
    witness = cp.Variable((4, 4), hermitian=True)
    ceiling = cp.Variable((2, 2), hermitian=True)
    residual = sum(multipliers[k] * operator for k, (operator, _) in enumerate(constraints)) - objective
    residual = residual - cp.partial_transpose(witness, DIMS, 0)
    rules = [witness >> 0]
    targets = np.array([value for _, value in constraints])
    cost = targets @ multipliers
    if fixed_trace is None:
        residual = residual + cp.kron(ceiling, I2)
        rules.append(ceiling >> 0)
        cost = cost + cp.real(cp.trace(ceiling))
    problem = cp.Problem(cp.Minimize(cost), [*rules, residual >> 0])
    problem.solve(solver=SOLVER)
    _require_optimal(problem, "dual")
    y = np.array(multipliers.value, dtype=float)
    projected_witness = _psd_part(np.array(witness.value, dtype=complex))
    operator_sum = sum((y[k] * operator for k, (operator, _) in enumerate(constraints)), start=np.zeros((4, 4)))
    value = float(targets @ y)
    slack_operator = operator_sum - objective - partial_transpose_input(projected_witness)
    if fixed_trace is not None:
        trace_bound = fixed_trace
    else:
        projected_ceiling = _psd_part(np.array(ceiling.value, dtype=complex))
        slack_operator = slack_operator + np.kron(projected_ceiling, I2)
        value += float(np.trace(projected_ceiling).real)
        trace_bound = 2.0
    return value + trace_bound * max(0.0, -_least_eigenvalue(slack_operator))


def classical_benchmark(
    states: Sequence[tuple[complex, complex]],
    priors: Sequence[float],
    success: Sequence[float] | None = None,
    figure: str = "pooled",
) -> Benchmark:
    """The certified classical optimum of ``figure`` over the ensemble, with or without a fixed success profile."""
    if figure not in FIGURES:
        raise ProtocolError(f"figure must be one of {FIGURES}")
    projectors = _projectors(states)
    weights = _require_priors(priors, len(projectors))
    gates = [np.kron(rho.T, I2) for rho in projectors]
    overlaps = [np.kron(rho.T, rho) for rho in projectors]
    if success is None:
        if figure == "average":
            raise ProtocolError("the average of per-input conditional fidelities needs a success profile")
        accepted = sum((w * gate for w, gate in zip(weights, gates, strict=True)), start=np.zeros((4, 4)))
        objective = sum((w * overlap for w, overlap in zip(weights, overlaps, strict=True)), start=np.zeros((4, 4)))
        if _least_eigenvalue(accepted) <= 1e-9:
            raise ProtocolError("the prior-weighted input state is singular; free post-selection is unbounded on it")
        achieved, choi = _primal(objective, [(accepted, 1.0)], trace_bounded=False)
        certified = _free_postselection_bound(objective, accepted)
    else:
        profile = _require_profile(success, len(projectors))
        if figure == "pooled":
            scale = weights / float(weights @ profile)
        else:
            scale = weights / profile
        objective = sum((c * overlap for c, overlap in zip(scale, overlaps, strict=True)), start=np.zeros((4, 4)))
        constraints, fixed_trace = success_operator(projectors, profile)
        achieved, choi = _primal(objective, constraints, trace_bounded=fixed_trace is None)
        certified = _profile_bound(objective, constraints, fixed_trace)
    if certified - achieved > GAP_LIMIT or achieved - certified > FEASIBILITY_TOLERANCE:
        raise ProtocolError(f"certified bound {certified} and achieved value {achieved} disagree")
    return Benchmark(figure=figure, certified=certified, achieved=achieved, choi=choi)


def six_state_benchmark(
    priors: Mapping[str, float],
    success: Mapping[str, float] | None = None,
    figure: str = "pooled",
) -> Benchmark:
    """classical_benchmark over the six Pauli eigenstates, keyed by their labels (+Z, -Z, +X, -X, +Y, -Y)."""
    if set(priors) != set(SIX_LABELS) or (success is not None and set(success) != set(SIX_LABELS)):
        raise ProtocolError(f"priors and success need exactly the labels {SIX_LABELS}")
    return classical_benchmark(
        [SIX_AMPLITUDES[label] for label in SIX_LABELS],
        [priors[label] for label in SIX_LABELS],
        None if success is None else [success[label] for label in SIX_LABELS],
        figure,
    )


def attempts_benchmark(matching_attempts: Mapping[str, int]) -> Benchmark:
    """Free-post-selection pooled bound when each input's matching-basis attempts set its prior.

    The pooled conditional fidelity of joint_teleportation_scores weights an
    input by its accepted matching-basis trials, attempts times success, so the
    classical bound for that figure takes priors proportional to attempts.
    """
    if set(matching_attempts) != set(SIX_LABELS):
        raise ProtocolError(f"attempts need exactly the labels {SIX_LABELS}")
    for label, count in matching_attempts.items():
        if not isinstance(count, int) or isinstance(count, bool) or count <= 0:
            raise ProtocolError(f"attempts for {label} must be a positive integer")
    total = sum(matching_attempts.values())
    return six_state_benchmark({label: count / total for label, count in matching_attempts.items()})


def realizable_profile(success: Mapping[str, float]) -> tuple[dict[str, float], float]:
    """The six-state profile ``m_0 + m . r`` nearest in least squares, and the largest residual from the data."""
    if set(success) != set(SIX_LABELS):
        raise ProtocolError(f"success needs exactly the labels {SIX_LABELS}")
    _require_profile([success[label] for label in SIX_LABELS], 6)
    offset = sum(success.values()) / 6.0
    fitted: dict[str, float] = {}
    for axis in "ZXY":
        tilt = (success[f"+{axis}"] - success[f"-{axis}"]) / 2.0
        fitted[f"+{axis}"] = offset + tilt
        fitted[f"-{axis}"] = offset - tilt
    residual = max(abs(fitted[label] - success[label]) for label in SIX_LABELS)
    return fitted, residual


def _table_row(case: tuple[str, tuple[float, ...], tuple[float, ...] | None, str]) -> tuple[str, float]:
    name, priors, success, figure = case
    if name == "bb84_uniform":
        states = [SIX_AMPLITUDES[label] for label in ("+Z", "-Z", "+X", "-X")]
        return name, classical_benchmark(states, priors, success, figure).certified
    priors_map = dict(zip(SIX_LABELS, priors, strict=True))
    success_map = None if success is None else dict(zip(SIX_LABELS, success, strict=True))
    return name, six_state_benchmark(priors_map, success_map, figure).certified


TABLE_CASES: tuple[tuple[str, tuple[float, ...], tuple[float, ...] | None, str], ...] = (
    ("six_uniform_free", (1 / 6,) * 6, None, "pooled"),
    ("bb84_uniform", (0.25,) * 4, None, "pooled"),
    ("six_z_weighted_free", (0.25, 0.25, 0.125, 0.125, 0.125, 0.125), None, "pooled"),
    ("six_uniform_tilted_pooled", (1 / 6,) * 6, (0.9, 0.5, 0.7, 0.7, 0.7, 0.7), "pooled"),
    ("six_uniform_tilted_average", (1 / 6,) * 6, (0.9, 0.5, 0.7, 0.7, 0.7, 0.7), "average"),
)


def tables() -> dict[str, float]:
    return dict(ordered_map(_table_row, list(TABLE_CASES)))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tables", action="store_true", required=True, help="print the certified benchmarks as JSON")
    parser.parse_args(argv)
    rows = tables()
    json.dump({name: round(value, 9) for name, value in rows.items()}, sys.stdout, indent=1)
    sys.stdout.write("\n")
    return 0 if all(math.isfinite(value) for value in rows.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
