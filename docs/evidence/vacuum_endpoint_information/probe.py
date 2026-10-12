"""Ideal finite-state acquisition comparison; CPU evidence only."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
from pathlib import Path
from typing import Any, TypeAlias

import numpy as np
import scipy
from numpy.typing import NDArray
from scipy.linalg import expm

Record: TypeAlias = dict[str, Any]
ComplexArray: TypeAlias = NDArray[np.complex128]
RealArray: TypeAlias = NDArray[np.float64]
BUNDLE = Path(__file__).resolve().parent
ABSOLUTE_TOLERANCE = 1e-12
RELATIVE_TOLERANCE = 1e-10
VERSION_KEYS = frozenset(("python", "numpy", "scipy"))
EXPECTED_INPUTS: dict[str, Record] = {
    "inputs/reviewed_probe.py.txt": {
        "bytes": 12803,
        "sha256": "88bc49cf92deadba0e2ee4360825844a7c9b561647f5a76feefde8900f431029",
    },
    "inputs/reviewed_result.json": {
        "bytes": 107998,
        "sha256": "e29459a8958cc5c8ee462d2ea023b15373602d333028219e390d00635f041028",
    },
    "inputs/previous_probe.py.txt": {
        "bytes": 13104,
        "sha256": "22c1c130a42440074b66aa93f990e0920ff91e08c7b04e9bb63df718d5a834a5",
    },
    "inputs/previous_result.json": {
        "bytes": 9713,
        "sha256": "6147433302a506c33f5a9c9367b7f67b6d22d2398f82577a179bb503cdf7207b",
    },
    "inputs/source-note.md.txt": {
        "bytes": 12851,
        "sha256": "8e3b0cd1c14970bb5c3ea97ea8aaa401932471c357fd484d99a7f952e5ffbafd",
    },
}
SOURCE_FILES = ("probe.py", "check_probe.py", "provenance.json", *EXPECTED_INPUTS)


def require(condition: bool | np.bool_, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def real_scalar(value: Any) -> float:
    require(abs(complex(value).imag) < 1e-11, "Expected a real probability/moment")
    return float(complex(value).real)


paulis: dict[str, ComplexArray] = {
    "I": np.eye(2, dtype=complex),
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.diag([1, -1]).astype(complex),
}
all_settings = ["".join(labels) for labels in itertools.product("XYZ", repeat=2)]
four_settings = ["ZZ", "ZX", "XX", "YY"]
pauli_products = {label: np.kron(paulis[label[0]], paulis[label[1]]) for label in all_settings}
pair = np.zeros((4, 4), dtype=complex)
for occupation in range(1, 4):
    pair[occupation - 1, occupation] = occupation
real_pair = (pair + pair.conj().T) / 2
imaginary_pair = (pair - pair.conj().T) / (2j)
number = np.diag(np.arange(4)).astype(complex)
total_shots_per_arm = 36000


def density(strength: float, phase: float) -> ComplexArray:
    generator = 1j * (np.exp(1j * phase) * pair.conj().T - np.exp(-1j * phase) * pair)
    vacuum = np.eye(4, dtype=complex)[:, 0]
    state = expm(-1j * strength * generator) @ vacuum
    return np.outer(state, state.conj())


def setting_moments(state_density: ComplexArray, setting: str) -> Record:
    local_left = paulis[setting[0]]
    local_right = paulis[setting[1]]
    probabilities = []
    outcomes = []
    for left_result, right_result in itertools.product((-1, 1), repeat=2):
        projector = np.kron(
            (paulis["I"] + left_result * local_left) / 2,
            (paulis["I"] + right_result * local_right) / 2,
        )
        probability = real_scalar(np.trace(projector @ state_density))
        require(probability >= -1e-12, "Positive measurement probability")
        probabilities.append(probability)
        outcomes.append([left_result, right_result, left_result * right_result])
    outcomes_array = np.array(outcomes)
    probabilities_array = np.array(probabilities)
    means = probabilities_array @ outcomes_array
    centered = outcomes_array - means
    covariance = centered.T @ (probabilities_array[:, None] * centered)
    exact_second_moment = np.array(
        [
            [1, means[2], means[1]],
            [means[2], 1, means[0]],
            [means[1], means[0], 1],
        ]
    )
    analytic_covariance = exact_second_moment - np.outer(means, means)
    analytic_probabilities = (1 + outcomes_array @ means) / 4
    require(np.max(np.abs(covariance - analytic_covariance)) < 1e-12, "Analytic covariance formula")
    require(np.max(np.abs(probabilities_array - analytic_probabilities)) < 1e-12, "Analytic product probability law")
    require(abs(sum(probabilities) - 1) < 1e-12, "Normalized measurement law")
    require(np.linalg.eigvalsh(covariance).min() > -1e-12, "Positive covariance")
    return {
        "outcomes_q1_q0_product": outcomes,
        "probabilities": probabilities,
        "means_q1_q0_product": means.tolist(),
        "covariance_q1_q0_product": covariance.tolist(),
    }


four_weights: dict[str, RealArray] = {
    "XX": np.array([0.0, 0.5, 0.5]),
    "ZX": np.array([0.0, 0.5, -0.5]),
    "YY": np.array([0.0, 0.0, 0.5]),
}
nine_weights: dict[str, RealArray] = {
    "XX": np.array([0.0, 1 / 3, 0.5]),
    "YX": np.array([0.0, 1 / 3, 0.0]),
    "ZX": np.array([0.0, 1 / 3, -0.5]),
    "YY": np.array([0.0, 0.0, 0.5]),
}
imaginary_weights_nine: dict[str, RealArray] = {
    "XY": np.array([0.0, 1 / 3, -0.5]),
    "YY": np.array([0.0, 1 / 3, 0.0]),
    "ZY": np.array([0.0, 1 / 3, -0.5]),
    "YX": np.array([0.0, 0.0, 0.5]),
}


def reconstruct(weights: dict[str, RealArray]) -> ComplexArray:
    operator = np.zeros((4, 4), dtype=complex)
    for setting, weight in weights.items():
        operator += (
            weight[0] * np.kron(paulis[setting[0]], paulis["I"])
            + weight[1] * np.kron(paulis["I"], paulis[setting[1]])
            + weight[2] * pauli_products[setting]
        )
    return operator


def estimator_summary(moments: dict[str, Record], weights: dict[str, RealArray], setting_count: int) -> Record:
    group_variances = {}
    group_means = {}
    for setting, weight in weights.items():
        means = np.array(moments[setting]["means_q1_q0_product"])
        covariance = np.array(moments[setting]["covariance_q1_q0_product"])
        group_variances[setting] = float(weight @ covariance @ weight)
        group_means[setting] = float(weight @ means)
    scaled_variance = setting_count * sum(group_variances.values())
    return {
        "weights_q1_q0_product": {setting: weight.tolist() for setting, weight in weights.items()},
        "group_means": group_means,
        "group_variances_per_shot": group_variances,
        "N_times_estimator_variance": scaled_variance,
        "variance_at_N_36000": scaled_variance / total_shots_per_arm,
        "shots_per_setting": total_shots_per_arm // setting_count,
        "mean": sum(group_means.values()),
    }


def build_reference(original_result: Record, original_inputs: list[Record]) -> Record:
    require(np.max(np.abs(reconstruct(four_weights) - real_pair)) < 1e-12, "Four-setting estimator operator")
    require(np.max(np.abs(reconstruct(nine_weights) - real_pair)) < 1e-12, "Nine-setting estimator operator")
    require(
        np.max(np.abs(reconstruct(imaginary_weights_nine) - imaginary_pair)) < 1e-12, "Imaginary estimator operator"
    )
    record: Record = {
        "reference_assumptions": [
            "Exact cutoff-four Hamiltonian; q1q0 binary ordering",
            "Independent identically prepared shots within each setting and arm",
            "Ideal projective product measurements and ideal readout",
            "Different settings/arms have independent shot samples",
            "Reference-state allocation is conditional on the known ideal finite model",
            "Every arm receives N=36000 total shots; zero controls retained separately per strength",
            "Four settings receive N/4 each; nine settings receive N/9 each",
            "IX is averaged equally across settings ending in X; same-shot covariance retained",
        ],
        "inputs": original_inputs,
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "arms": [],
        "hidden_imaginary_control_counterexamples": [],
        "moments_formula": (
            "For outcomes (s1,s0,s1*s0), mu=(m1,m0,m12); P=(1+s1*m1+s0*m0+s1*s0*m12)/"
            "4; Cov= [[1,m12,m0],[m12,1,m1],[m0,m1,1]]-mu*mu.T"
        ),
    }

    for strength in (0.2, 0.4):
        positive_density = density(strength, 0.0)
        state_candidates = [
            ("phase_zero", positive_density),
            ("phase_pi", density(strength, math.pi)),
            ("diagonal_mixture", np.diag(np.diag(positive_density)).astype(complex)),
            ("zero_interaction", density(0.0, 0.0)),
        ]
        for arm_name, state_density in state_candidates:
            moments = {setting: setting_moments(state_density, setting) for setting in all_settings}
            four_summary = estimator_summary(moments, four_weights, 4)
            nine_summary = estimator_summary(moments, nine_weights, 9)
            imaginary_summary = estimator_summary(moments, imaginary_weights_nine, 9)
            exact_real_pair = real_scalar(np.trace(real_pair @ state_density))
            require(abs(four_summary["mean"] - exact_real_pair) < 1e-12, "Unbiased four-setting reference")
            require(abs(nine_summary["mean"] - exact_real_pair) < 1e-12, "Unbiased nine-setting reference")
            population = np.diag(state_density).real
            mean_number = real_scalar(np.trace(number @ state_density))
            variance_number = real_scalar(np.trace(number @ number @ state_density)) - mean_number**2
            top_probability = float(population[-1])
            sqrt_group_variances = {
                setting: math.sqrt(max(value, 0.0))
                for setting, value in four_summary["group_variances_per_shot"].items()
            }
            sum_sqrt_variances = sum(sqrt_group_variances.values())
            require(sum_sqrt_variances > 0, "Nondegenerate coherence sampling")
            conditional_allocation = {
                "ZZ": 0.25,
                **{setting: 0.75 * value / sum_sqrt_variances for setting, value in sqrt_group_variances.items()},
            }
            conditional_scaled_variance = sum_sqrt_variances**2 / 0.75
            record["arms"].append(
                {
                    "r": strength,
                    "arm": arm_name,
                    "population": population.tolist(),
                    "exact_Re_ab": exact_real_pair,
                    "exact_Im_ab": real_scalar(np.trace(imaginary_pair @ state_density)),
                    "mean_number": mean_number,
                    "variance_number_per_ZZ_shot": variance_number,
                    "top_probability": top_probability,
                    "commutator_variance_per_ZZ_shot": 16 * top_probability * (1 - top_probability),
                    "setting_moments": moments,
                    "four_uniform_Re_ab": four_summary,
                    "nine_uniform_Re_ab": nine_summary,
                    "nine_uniform_Im_ab": imaginary_summary,
                    "fixed_shot_variance_ratio_nine_over_four": nine_summary["N_times_estimator_variance"]
                    / four_summary["N_times_estimator_variance"],
                    "conditional_Neyman_fixed_IX_weights_ZZ_quarter": {
                        "shot_fractions": conditional_allocation,
                        "N_times_estimator_variance": conditional_scaled_variance,
                        "scope": (
                            "Oracle allocation for fixed estimator weights, known finite state, and Z"
                            "Z=N/4; zero reference permits a zero-variance group only under that know"
                            "n-state assumption"
                        ),
                    },
                }
            )
            if arm_name == "phase_zero":
                previous = next(
                    item for item in original_result["cutoff_results"] if item["cutoff"] == 4 and item["r"] == strength
                )
                require(
                    abs(previous["finite_re_ab"] - exact_real_pair) < 1e-12, "Independent finite-reference reproduction"
                )

        populations = np.diag(positive_density).real
        perturbation = 0.5 * min(
            math.sqrt(populations[0] * populations[3]),
            math.sqrt(populations[1] * populations[2]),
        )
        control_density = np.diag(populations).astype(complex)
        hidden_density = control_density + perturbation * pauli_products["XY"]
        minimum_eigenvalue = float(np.linalg.eigvalsh(hidden_density).min())
        require(minimum_eigenvalue > 0, "Physical hidden-coherence control")
        hidden_probability_residual = 0.0
        for setting in four_settings:
            original = np.array(setting_moments(control_density, setting)["probabilities"])
            modified = np.array(setting_moments(hidden_density, setting)["probabilities"])
            hidden_probability_residual = max(hidden_probability_residual, float(np.max(np.abs(original - modified))))
        require(hidden_probability_residual < 1e-12, "Four-setting blind subspace")
        record["hidden_imaginary_control_counterexamples"].append(
            {
                "r": strength,
                "construction": "rho_hidden = diag(p_n) + t XY",
                "t": perturbation,
                "minimum_eigenvalue": minimum_eigenvalue,
                "four_setting_probability_residual": hidden_probability_residual,
                "Re_ab": real_scalar(np.trace(real_pair @ hidden_density)),
                "Im_ab": real_scalar(np.trace(imaginary_pair @ hidden_density)),
                "XY": real_scalar(np.trace(pauli_products["XY"] @ hidden_density)),
            }
        )

    record["workload"] = {
        "strengths": 2,
        "arms_per_strength": ["phase_zero", "phase_pi", "diagonal_mixture", "zero_interaction"],
        "four_setting_arm_basis_variants": 32,
        "nine_setting_arm_basis_variants": 72,
        "shots_per_arm": total_shots_per_arm,
        "whole_workload_shots_each_design": 8 * total_shots_per_arm,
        "excluded_additional_costs": [
            "Full-encoding references",
            "Independent readout/preparation calibration",
            "Packing and patch/time controls",
            "Implementation variants",
            "Job floors and splits",
        ],
        "odd_contrast_variance": "For independent equal-N phase arms: Var((Re_plus-Re_minus)/2)=(Var_plus+Var_minus)/4",
        "occupation_constraint": "n_ZZ >= Var(n)/sigma_n^2",
        "commutator_constraint": "n_ZZ >= 16 p_top(1-p_top)/sigma_commutator^2",
        "prospective_gate": (
            "Compare complete-arm endpoint mean-square error/information and returned"
            " charged time, retaining occupancy/cutoff and diagnostic requirements; s"
            "ettings count alone is insufficient"
        ),
    }
    record["status"] = "CPU ideal finite-state acquisition comparison passed"
    return record


def source_hashes() -> dict[str, str]:
    hashes = {}
    for name in SOURCE_FILES:
        path = BUNDLE / name
        require(path.is_file() and not path.is_symlink(), f"Source must be a regular file: {name}")
        if name in EXPECTED_INPUTS:
            require(path.stat().st_size == EXPECTED_INPUTS[name]["bytes"], f"Bound input size differs: {name}")
        else:
            require(path.stat().st_size <= 400000, f"Source byte ceiling: {name}")
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def verify_unchanged_sources(before: dict[str, str], after: dict[str, str]) -> None:
    require(before == after, "Replay source changed during computation")


def load_json_object(path: Path) -> Record:
    def reject_constant(value: str) -> None:
        raise RuntimeError(f"Nonfinite JSON constant: {value}")

    def finite_float(value: str) -> float:
        number = float(value)
        require(math.isfinite(number), "Nonfinite JSON number")
        return number

    def unique_object(pairs: list[tuple[str, Any]]) -> Record:
        result: Record = {}
        for key, value in pairs:
            require(key not in result, f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    record = json.loads(
        path.read_text(encoding="utf-8"),
        parse_constant=reject_constant,
        parse_float=finite_float,
        object_pairs_hook=unique_object,
    )
    require(isinstance(record, dict), "JSON record must be an object")
    return dict(record)


def validate_provenance(provenance: Record, identities: dict[str, Record]) -> None:
    compare_records(provenance.get("schema_version"), 1, "provenance.schema_version")
    compare_records(provenance.get("inputs"), EXPECTED_INPUTS, "provenance.inputs")
    compare_records(identities, EXPECTED_INPUTS, "input.identities")
    require(sum(identity["bytes"] for identity in identities.values()) <= 260000, "Input byte ceiling")


def compare_records(observed: Any, retained: Any, location: str = "record") -> None:
    require(type(observed) is type(retained), f"{location}: value type differs")
    if isinstance(observed, dict):
        require(observed.keys() == retained.keys(), f"{location}: keys differ")
        for key, value in observed.items():
            compare_records(value, retained[key], f"{location}.{key}")
    elif isinstance(observed, list):
        require(len(observed) == len(retained), f"{location}: length differs")
        for index, (value, expected) in enumerate(zip(observed, retained, strict=True)):
            compare_records(value, expected, f"{location}[{index}]")
    elif isinstance(observed, float):
        require(math.isfinite(observed) and math.isfinite(retained), f"{location}: nonfinite value")
        require(
            math.isclose(observed, retained, rel_tol=RELATIVE_TOLERANCE, abs_tol=ABSOLUTE_TOLERANCE),
            f"{location}: numeric result differs",
        )
    else:
        require(observed == retained, f"{location}: categorical result differs")


def compare_version_aware(observed: Record, retained: Record) -> Record:
    versions: Record = {}
    for key in sorted(VERSION_KEYS):
        require(isinstance(observed.get(key), str) and bool(observed[key]), f"Missing observed version: {key}")
        require(isinstance(retained.get(key), str) and bool(retained[key]), f"Missing retained version: {key}")
        versions[key] = {"observed": observed[key], "retained": retained[key]}
    compare_records(
        {key: value for key, value in observed.items() if key not in VERSION_KEYS},
        {key: value for key, value in retained.items() if key not in VERSION_KEYS},
    )
    return versions


def validate_coverage(reference: Record) -> None:
    expected = [
        (strength, arm)
        for strength in (0.2, 0.4)
        for arm in ("phase_zero", "phase_pi", "diagonal_mixture", "zero_interaction")
    ]
    observed = [(arm["r"], arm["arm"]) for arm in reference["arms"]]
    require(observed == expected, "Eight-arm denominator or order differs")
    for arm in reference["arms"]:
        require(list(arm["setting_moments"]) == all_settings, "Nine-law setting denominator or order differs")
    require(sum(len(arm["setting_moments"]) for arm in reference["arms"]) == 72, "Seventy-two-law denominator")
    require(reference["workload"]["whole_workload_shots_each_design"] == 288000, "Matched complete workload shots")


def supplementary_checks() -> Record:
    required = {"ZI", "IZ", "ZZ", "IX", "XX", "YY", "ZX", "IY", "XY", "YX", "ZY"}

    def covers(settings: tuple[str, ...]) -> bool:
        visible = {label for setting in settings for label in (setting, setting[0] + "I", "I" + setting[1])}
        return required <= visible

    cover = ["ZZ", "ZX", "XX", "YY", "XY", "YX", "ZY"]
    require(covers(tuple(cover)), "Seven-setting endpoint cover")
    minimum_covers: list[list[str]] = []
    for count in range(1, 8):
        candidates = [list(settings) for settings in itertools.combinations(all_settings, count) if covers(settings)]
        if candidates:
            minimum_covers = candidates
            require(count == 7 and len(candidates) == 1, "Unique product-Pauli endpoint cover")
            break
    require(bool(minimum_covers), "Endpoint cover exists")
    hidden_after_xy: list[Record] = []
    for strength in (0.2, 0.4):
        populations = np.diag(density(strength, 0.0)).real
        perturbation = 0.5 * min(math.sqrt(populations[0] * populations[3]), math.sqrt(populations[1] * populations[2]))
        control = np.diag(populations).astype(complex)
        hidden = control + perturbation * pauli_products["YX"]
        minimum_eigenvalue = float(np.linalg.eigvalsh(hidden).min())
        require(minimum_eigenvalue > 0, "Physical YX hidden witness")
        residual = max(
            float(
                np.max(
                    np.abs(
                        np.array(setting_moments(control, setting)["probabilities"])
                        - np.array(setting_moments(hidden, setting)["probabilities"])
                    )
                )
            )
            for setting in (*four_settings, "XY")
        )
        imaginary_value = real_scalar(np.trace(imaginary_pair @ hidden))
        require(residual < 1e-12 and abs(imaginary_value) > 1e-8, "Five-setting imaginary witness")
        hidden_after_xy.append(
            {
                "r": strength,
                "construction": "diag(p_n) + t YX",
                "t": perturbation,
                "minimum_eigenvalue": minimum_eigenvalue,
                "five_setting_probability_residual": residual,
                "Im_ab": imaginary_value,
            }
        )
    return {
        "minimal_product_cover": cover,
        "minimum_setting_count": 7,
        "unique_minimum_cover": minimum_covers,
        "required_nonidentity_paulis": sorted(required),
        "all_state_tomography_settings": all_settings,
        "hidden_after_XY_counterexamples": hidden_after_xy,
        "same_shot_covariance": "Every linear estimator retains full within-setting three-outcome covariance.",
        "cross_arm_covariance": "Independence is an assumption. General odd contrast variance=(Vplus+Vminus-2cov)/4.",
        "allocation_scope": (
            "Neyman allocation is conditional on fixed weights and known finite-state"
            " variances; not an unknown-state optimum."
        ),
    }


def build_record() -> Record:
    before = source_hashes()
    identities = {}
    for name in EXPECTED_INPUTS:
        content = (BUNDLE / name).read_bytes()
        identities[name] = {"bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()}
    provenance = load_json_object(BUNDLE / "provenance.json")
    validate_provenance(provenance, identities)
    previous = load_json_object(BUNDLE / "inputs/previous_result.json")
    original_inputs = [
        dict(EXPECTED_INPUTS[name])
        for name in ("inputs/previous_probe.py.txt", "inputs/previous_result.json", "inputs/source-note.md.txt")
    ]
    reference = build_reference(previous, original_inputs)
    validate_coverage(reference)
    reviewed = load_json_object(BUNDLE / "inputs/reviewed_result.json")
    compare_version_aware(reference, reviewed)
    record: Record = {
        "schema_version": 1,
        "boundary": provenance["boundary"],
        "python": reference["python"],
        "numpy": reference["numpy"],
        "scipy": reference["scipy"],
        "source_sha256": before,
        "historical_audit": identities,
        "reference_record": {key: value for key, value in reference.items() if key not in VERSION_KEYS},
        "supplementary_checks": supplementary_checks(),
        "status": "Finite ideal-readout endpoint replay passed",
    }
    verify_unchanged_sources(before, source_hashes())
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Compare with the adjacent retained result")
    arguments = parser.parse_args()
    record = build_record()
    if arguments.check:
        retained = load_json_object(BUNDLE / "result.json")
        versions = compare_version_aware(record, retained)
        print(json.dumps({"status": "Endpoint replay matches retained evidence", "versions": versions}, sort_keys=True))
    else:
        print(json.dumps(record, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
