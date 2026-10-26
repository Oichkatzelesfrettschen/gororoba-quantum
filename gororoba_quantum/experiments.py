"""Experiment groups: each a primary circuit, its controls, and their ideal distributions.

A group runs on one backend from one initial layout: the primary circuit picks
the layout and every control compiles onto it, so a control compares one patch
of the device against itself. Ideals come from predict.py; summaries reduce the
noisy or measured distributions to each design's observable.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter

import predict
import variance
from cd_core import sedenion_zero_divisors
from designs import (
    SPECTRUM_EXEMPLARS,
    SWEEP_PHASES,
    design_a_associator,
    design_c_associator_spectrum,
    design_d_phase_sweep,
)
from factoring import distribution_success, ideal_phase_distribution, reference_multiplicative_order
from order_finding import factor_order_finding, folded_qpe

Summary = Callable[[dict[str, np.ndarray]], dict[str, float]]
# Readout-inverted quasi-probabilities and each circuit's one-shot covariance.
CovarianceSummary = Callable[[dict[str, np.ndarray], dict[str, np.ndarray]], dict[str, float]]
Admission = Callable[[list[dict[str, float]], int], dict[str, Any]]
# Every member's routed ISA in member order and the Target they compiled
# against, to the reasons the candidate is rejected.
RoutedCheck = Callable[[list[QuantumCircuit], Any], list[str]]


@dataclass(frozen=True)
class Member:
    """One circuit of a group.

    binding assigns the parameters of a shared circuit: members whose circuit is
    the same parametrized object compile once and differ only by bound angles,
    so they share routing and readout qubits
    (live_run.select). mirror asks the compiler for a calibration twin cut from
    the member's compiled ISA circuit, on the same physical qubits with the same
    two-qubit content (live_run.mirror_isa); summaries find its distribution
    under the member's name plus MIRROR_SUFFIX. weights scores each outcome in
    [0, 1] for the variance decomposition (variance.score); without it the
    score follows the ideal.
    """

    name: str
    circuit: QuantumCircuit
    ideal: np.ndarray
    binding: dict[Parameter, float] | None = None
    mirror: bool = False
    weights: np.ndarray | None = None


MIRROR_SUFFIX = "_mirror"


@dataclass(frozen=True)
class Group:
    """Members that share one layout, their summary, and their replicated statistics.

    instances names members that are equal-cost instances of one experiment
    with comparable ideal-weighted scores, the instance axis of the variance
    decomposition. admission turns per-replica summaries and the shots per
    replica into an admission verdict for the group's claim. rate_keys names
    summary values that are per-shot rates over one member's shots, whose
    replicate intervals carry a pooled-shot Wilson bound. replica_floor, when
    set, replaces the default replica floor for this group; an explicit
    --replica-floor still governs every group (live_run.replica_floor).
    execution_rows assigns each member an explicit global PUB row; sparse
    rows preserve isolated workloads without inserting idle measurements.
    Explicit schedules prohibit automatic mirrors and replica references.
    summarize_with_covariance, when set, summarizes readout-inverted
    quasi-probabilities M p together with each circuit's one-shot covariance
    M (diag(p) - p p^T) M^T, so a summary that propagates the multinomial
    covariance itself stays exact through live_run.corrected_summary.
    routed_violations, when set, rejects a candidate whose routed members
    break a physical-placement invariant of the group's model
    (live_run.select_candidates).
    """

    name: str
    members: tuple[Member, ...]
    summarize: Summary
    instances: tuple[str, ...] = ()
    admission: Admission | None = None
    rate_keys: frozenset[str] = frozenset()
    replica_floor: float | None = None
    execution_rows: tuple[int, ...] | None = None
    summarize_with_covariance: CovarianceSummary | None = None
    routed_violations: RoutedCheck | None = None

    def __post_init__(self) -> None:
        if self.execution_rows is None:
            return
        if not isinstance(self.execution_rows, tuple):
            raise ValueError(f"{self.name}: execution rows must be an immutable tuple")
        if len(self.execution_rows) != len(self.members):
            raise ValueError(f"{self.name}: execution rows must match member count")
        if any(type(row) is not int or row < 0 for row in self.execution_rows):
            raise ValueError(f"{self.name}: execution rows must be nonnegative integers")
        if len(set(self.execution_rows)) != len(self.execution_rows):
            raise ValueError(f"{self.name}: execution rows must be unique within a group")
        if any(member.mirror for member in self.members):
            raise ValueError(f"{self.name}: explicit execution rows prohibit automatic mirrors")


def tvd(p: np.ndarray, q: np.ndarray) -> float:
    return 0.5 * float(np.sum(np.abs(np.asarray(p) - np.asarray(q))))


def fit_fringe(phases: list[float], p0: list[float]) -> dict[str, float]:
    """Least-squares P0 = o + A cos(phi) + B sin(phi): offset, visibility, phase.

    Visibility is 2 sqrt(A^2 + B^2) and the fringe phase is atan2(B, A); the
    ideal (1 - s cos phi)/2 has offset 1/2, visibility 1, and phase 0 for s = -1.
    """
    basis = np.column_stack([np.ones(len(phases)), np.cos(phases), np.sin(phases)])
    (o, a, b), *_ = np.linalg.lstsq(basis, np.array(p0), rcond=None)
    return {"offset": float(o), "visibility": float(2 * math.hypot(a, b)), "phase": float(math.atan2(b, a))}


def _two_outcome(p1: float) -> np.ndarray:
    return np.array([1.0 - p1, p1])


def z_expectation(dist: np.ndarray) -> float:
    """<Z> of a one-bit distribution: P(0) - P(1)."""
    return float(dist[0] - dist[1])


def odr_p1(dist: np.ndarray, mirror: np.ndarray) -> float:
    """P(1) after dividing <Z> by the mirror circuit's attenuation.

    The value is left unclipped: a result outside [0, 1] means the mirror
    attenuates less than the witness does, which is itself the diagnostic.
    """
    att = z_expectation(mirror)
    corrected = z_expectation(dist) / att if att > 0 else math.nan
    return float((1.0 - corrected) / 2.0)


def _uniform(clbits: int) -> np.ndarray:
    return np.full(2**clbits, 1.0 / 2**clbits)


def _design_a() -> Group:
    qc = design_a_associator(1, 2)[0]

    def summarize(dist: dict[str, np.ndarray]) -> dict[str, float]:
        got = dist["design_a_1_2"]
        return {
            "p1": float(got[1]),
            "p1_odr": odr_p1(got, dist["design_a_1_2" + MIRROR_SUFFIX]),
            "mirror_z": z_expectation(dist["design_a_1_2" + MIRROR_SUFFIX]),
            "tvd_to_uniform": tvd(got, _uniform(1)),
        }

    return Group(
        "design_a",
        (Member("design_a_1_2", qc, _two_outcome(1.0), mirror=True),),
        summarize,
        rate_keys=frozenset({"p1"}),
    )


def _zero_divisor_fringe() -> Group:
    """Design B dark and bright and the design D sweep as bindings of one circuit.

    b = (e_k + e^{i phi} e_l)/sqrt2 covers all of them: phi = pi for s = -1 is
    the zero divisor, phi = 0 its sign-flipped control, and the sweep phases
    the fringe. One parametrized circuit gives every member the same compiled
    routing and readout qubit, so the suppression ratio and the fringe compare
    one set of physical qubits.
    """
    (i, j), (k, el), s = sedenion_zero_divisors()[0]
    tag = f"{i}_{j}_{k}_{el}"
    phi = Parameter("phi")
    template = design_d_phase_sweep((i, j), (k, el), phi)
    dark_phase, bright_phase = (0.0, math.pi) if s > 0 else (math.pi, 0.0)
    dark_p0 = predict.zero_divisor_p0((i, j), (k, el), s)
    bright_p0 = predict.zero_divisor_p0((i, j), (k, el), -s)
    dark_name, bright_name = f"design_b_dark_{tag}", f"design_b_bright_{tag}"
    members = [
        # Each witness gets its own mirror; the sweep points share the dark one,
        # since they differ from it only by the bound input phase.
        Member(dark_name, template, _two_outcome(1 - dark_p0), {phi: dark_phase}, mirror=True),
        Member(bright_name, template, _two_outcome(1 - bright_p0), {phi: bright_phase}, mirror=True),
    ]
    sweep_names = []
    for n, phase in enumerate(SWEEP_PHASES):
        want = predict.phase_sweep_p0((i, j), (k, el), phase)
        name = f"design_d_{tag}_phase_{n}of8"
        sweep_names.append(name)
        members.append(Member(name, template, _two_outcome(1 - want), {phi: phase}))

    def summarize(dist: dict[str, np.ndarray]) -> dict[str, float]:
        dark, bright = float(dist[dark_name][0]), float(dist[bright_name][0])
        dark_odr = 1.0 - odr_p1(dist[dark_name], dist[dark_name + MIRROR_SUFFIX])
        bright_odr = 1.0 - odr_p1(dist[bright_name], dist[bright_name + MIRROR_SUFFIX])
        fit = fit_fringe(SWEEP_PHASES, [float(dist[name][0]) for name in sweep_names])
        odr_sweep = [1.0 - odr_p1(dist[name], dist[dark_name + MIRROR_SUFFIX]) for name in sweep_names]
        fit_odr = {f"{k}_odr": v for k, v in fit_fringe(SWEEP_PHASES, odr_sweep).items()}
        return (
            {
                "p0_dark": dark,
                "p0_bright": bright,
                "ratio": dark / bright if bright else math.nan,
                "p0_dark_odr": dark_odr,
                "p0_bright_odr": bright_odr,
                "ratio_odr": dark_odr / bright_odr if bright_odr else math.nan,
                "mirror_z_dark": z_expectation(dist[dark_name + MIRROR_SUFFIX]),
                "mirror_z_bright": z_expectation(dist[bright_name + MIRROR_SUFFIX]),
                "tvd_to_uniform_dark": tvd(dist[dark_name], _uniform(1)),
                "tvd_to_uniform_bright": tvd(dist[bright_name], _uniform(1)),
            }
            | fit
            | fit_odr
        )

    return Group("zero_divisor_fringe", tuple(members), summarize, rate_keys=frozenset({"p0_dark", "p0_bright"}))


def _associator_spectrum(dim: int, i: int, j: int) -> Group:
    n = dim.bit_length() - 1
    omega = predict.associator_phase(dim, i, j)
    true = predict.walsh_distribution(omega)
    flipped = predict.walsh_distribution([w * (-1 if x == 0 else 1) for x, w in enumerate(omega)])
    hn = np.array([[(-1) ** bin(x & y).count("1") for x in range(dim)] for y in range(dim)]) / math.sqrt(dim)
    plus = np.full(dim, 1.0 / math.sqrt(dim))
    omitted = np.abs(hn @ predict.left_mult_matrix(dim, i) @ predict.left_mult_matrix(dim, j) @ plus) ** 2
    base = f"design_c_{dim}_{i}_{j}"
    members = (
        Member(base, design_c_associator_spectrum(dim, i, j), true),
        # flip=j negates L_{e_i}'s sign on input j, which the block sees at x = 0.
        Member(f"{base}_flip", design_c_associator_spectrum(dim, i, j, flip=j), flipped),
        Member(f"{base}_omit", design_c_associator_spectrum(dim, i, j, omit_adjoint=True), omitted),
    )

    def summarize(dist: dict[str, np.ndarray]) -> dict[str, float]:
        got = dist[base]
        return {
            "qubits": float(n),
            "tvd_to_true": tvd(got, true),
            "tvd_to_flip_prediction": tvd(got, flipped),
            "tvd_to_omit_prediction": tvd(got, omitted),
            "tvd_to_uniform": tvd(got, _uniform(n)),
            "flip_control_tvd_to_own": tvd(dist[f"{base}_flip"], flipped),
            "omit_control_tvd_to_own": tvd(dist[f"{base}_omit"], omitted),
        }

    return Group(base, members, summarize)


def _folded_qpe_mod15() -> Group:
    """Eigenphases of x -> 2x mod 15 read by semiclassical phase estimation (order_finding.py).

    The four eigenstates run identical-cost circuits with distinct deterministic
    outcomes s, so each serves as the others' control; the identity multiplier
    is the null and reads 0.
    """

    def one_hot(s: int) -> np.ndarray:
        out = np.zeros(4)
        out[s] = 1.0
        return out

    members = [Member(f"folded_qpe_s{s}", folded_qpe(s), one_hot(s)) for s in (1, 0, 2, 3)]
    members.append(Member("folded_qpe_null", folded_qpe(1, identity=True), one_hot(0)))

    def summarize(dist: dict[str, np.ndarray]) -> dict[str, float]:
        correct = {s: float(dist[f"folded_qpe_s{s}"][s]) for s in range(4)}
        return {f"p_correct_s{s}": p for s, p in correct.items()} | {
            "p_correct_mean": float(np.mean(list(correct.values()))),
            "null_p0": float(dist["folded_qpe_null"][0]),
            "tvd_to_uniform_mean": float(np.mean([tvd(dist[f"folded_qpe_s{s}"], _uniform(2)) for s in range(4)])),
        }

    return Group(
        "folded_qpe_mod15",
        tuple(members),
        summarize,
        instances=tuple(f"folded_qpe_s{s}" for s in range(4)),
        # p_correct_mean averages four members' rates; its Wilson bound over one
        # member's shots is the wider, conservative one.
        rate_keys=frozenset({*(f"p_correct_s{s}" for s in range(4)), "p_correct_mean", "null_p0"}),
    )


def _hybrid_shor_mod15() -> Group:
    """Faithful |1> order finding and an identity null at eight-bit precision."""
    modulus, base, phase_bits = 15, 2, 8
    reference_order = reference_multiplicative_order(base, modulus)
    ideal = np.asarray(ideal_phase_distribution(reference_order, phase_bits))
    null_ideal = np.zeros(1 << phase_bits)
    null_ideal[0] = 1.0
    uniform_null = distribution_success(_uniform(phase_bits), phase_bits, modulus, base)
    primary_name = "hybrid_shor_N15_a2"
    null_name = "hybrid_shor_N15_a2_null"
    # Every outcome of the pruned circuit lies in the ideal's support, so the
    # ideal-weighted score is constant; each shot instead scores whether its
    # outcome decodes to a verified factor.
    factor_shot = np.array(
        [
            distribution_success(np.eye(1 << phase_bits)[y], phase_bits, modulus, base)["factorable_probability"]
            for y in range(1 << phase_bits)
        ]
    )
    members = (
        Member(primary_name, factor_order_finding(modulus, base, phase_bits), ideal, weights=factor_shot),
        Member(
            null_name,
            factor_order_finding(modulus, base, phase_bits, identity=True),
            null_ideal,
            weights=factor_shot,
        ),
    )

    def summarize(dist: dict[str, np.ndarray]) -> dict[str, float]:
        primary = distribution_success(dist[primary_name], phase_bits, modulus, base)
        identity_null = distribution_success(dist[null_name], phase_bits, modulus, base)
        return {
            **primary,
            "identity_null_factorable_probability": identity_null["factorable_probability"],
            "identity_null_order_recovery_probability": identity_null["order_recovery_probability"],
            "uniform_null_factorable_probability": uniform_null["factorable_probability"],
            "uniform_null_order_recovery_probability": uniform_null["order_recovery_probability"],
            "factorable_margin_over_identity_null": (
                primary["factorable_probability"] - identity_null["factorable_probability"]
            ),
            "order_recovery_margin_over_identity_null": (
                primary["order_recovery_probability"] - identity_null["order_recovery_probability"]
            ),
            "factorable_margin_over_uniform_null": (
                primary["factorable_probability"] - uniform_null["factorable_probability"]
            ),
            "order_recovery_margin_over_uniform_null": (
                primary["order_recovery_probability"] - uniform_null["order_recovery_probability"]
            ),
            "tvd_to_ideal": tvd(dist[primary_name], ideal),
            "identity_null_p0": float(dist[null_name][0]),
        }

    def admit(per_replica: list[dict[str, float]], shots: int) -> dict[str, Any]:
        """HYBRID_SHOR.md roadmap item 5 on the replicated yields.

        A yield is admitted when its interval lower bound exceeds the exact
        uniform-null yield and the identity null's upper bound stays below
        that lower bound.
        """
        verdict: dict[str, Any] = {}
        for quantity in ("factorable_probability", "order_recovery_probability"):
            primary = variance.interval([r[quantity] for r in per_replica], shots, bernoulli=True)
            null = variance.interval([r[f"identity_null_{quantity}"] for r in per_replica], shots, bernoulli=True)
            uniform = per_replica[0][f"uniform_null_{quantity}"]
            admitted = "lo" in primary and "hi" in null and primary["lo"] > uniform and null["hi"] < primary["lo"]
            verdict[quantity] = {
                "primary": primary,
                "identity_null": null,
                "uniform_null": uniform,
                "admitted": admitted,
            }
        return verdict

    return Group(
        "hybrid_shor_mod15",
        members,
        summarize,
        admission=admit,
        # The admission interval's t multiplier falls from 4.30 at three
        # replicas to 2.45 at seven; a 0.8 floor reaches seven placements on a
        # kingston-class device, and the layout-variance decomposition prices
        # the weaker ones.
        replica_floor=0.8,
        rate_keys=frozenset(
            {
                "factorable_probability",
                "order_recovery_probability",
                "identity_null_factorable_probability",
                "identity_null_order_recovery_probability",
                "identity_null_p0",
            }
        ),
    )


def experiment_groups() -> list[Group]:
    return [
        _design_a(),
        _zero_divisor_fringe(),
        *(_associator_spectrum(dim, i, j) for dim, i, j in SPECTRUM_EXEMPLARS),
        _folded_qpe_mod15(),
        _hybrid_shor_mod15(),
    ]


def standalone_campaign_groups() -> list[Group]:
    """Opt-in campaigns, selected with --groups and run alone.

    They stay out of the default suite, so default replica placement is
    unchanged; plan() refuses to co-run a campaign with any other group.
    """
    from conditional_ramsey import conditional_ramsey_group
    from crossed_tile_template import crossed_group
    from diagnostic_controls import readout_delay_group, scaffold_ab_group
    from maximal_experiments import spectator_wavefront_ramsey_group
    from primorial_campaigns import coherence_probe_group, gap88_group, readout_preflight_group
    from qet_ladder import qet_compensated_ladder_group, qet_frame_diagnostic_group, qet_ladder_group
    from qubit_baseline import qubit_baseline_group
    from star_ramsey import star_ramsey_group

    return [
        spectator_wavefront_ramsey_group(),
        qubit_baseline_group(),
        crossed_group(),
        conditional_ramsey_group(),
        star_ramsey_group(),
        scaffold_ab_group(),
        readout_delay_group(),
        coherence_probe_group(),
        gap88_group(),
        readout_preflight_group(),
        qet_ladder_group(),
        qet_frame_diagnostic_group(),
        qet_compensated_ladder_group(),
    ]


def all_experiment_groups() -> list[Group]:
    """All registered experiment groups across default suites and standalone campaigns."""
    return [*experiment_groups(), *standalone_campaign_groups()]
