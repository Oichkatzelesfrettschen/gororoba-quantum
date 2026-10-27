"""Population against misassignment in a state-prep-control run with the two-read arms, from its raw shots.

The run selects the arms prep0, x_remeasure and remeasure (diagnostic_experiments.STATE_PREP_ARM_STEPS), three
static PUBs in that row order in one job. The service runs every circuit of shot s in row order before shot s + 1
(docs/notes/ibm_quantum/repetition-rate-execution.md), so within a shot the remeasure circuit follows the
x_remeasure circuit, and the prep0 circuit of shot s + 1 follows the remeasure circuit of shot s. The raw PUB files
hold each register as shot-ordered bit strings (live_run --collect), bit b the b-th character from the right; the
two-read arms record the first read in bit 0 and the second in bit 1.

Per qubit the report gives:
- prep0: P(1), the one-read excited fraction, with its Clopper-Pearson interval;
- x_remeasure: P(first read 1); P(second read 1 | first read 0), the |1> shots the first read misassigned and the
  second read recovers; P(second read 1 | first read 1);
- remeasure: P(first read 1); the persistence pi = P(second read 1 | first read 1); P(second read 1 | first read 0);
- the readout-event link: remeasure's first read conditioned on the same shot's x_remeasure first read (0 or 1),
  as a two-proportion test, and prep0's read at shot s + 1 conditioned on remeasure's first read at shot s.

Decision rule, fixed before the run (the case names the qubit it applies to): a population the first read found
reads 1 again, so pi sits near (1 - e01) exp(-t_measure / T1); a misassigned first read is followed by a read
of the prepared |0>, so pi sits near the one-read excited fraction. The reading is "population" when the lower
end of pi's two-sided 99 percent Clopper-Pearson interval exceeds 0.5, "misassignment" when the upper end lies
below 0.5, and "undecided" otherwise. The same rule, applied to x_remeasure's first-read-0 shots through
P(second read 1 | first read 0), names whether a |1> read as 0 keeps its population (the excess history of
docs/evidence/primorial_cover/case3/README.md) or lost it before the first read.

Usage, from the repository root:

    "$PYTHON" scripts/remeasure_history.py RUN_DIR [--out FILE] [--e01 E01 --t1-us T1 [--measure-us T]]
    "$PYTHON" scripts/remeasure_history.py --self-test

With --e01 and --t1-us the report also prints the population prediction for pi. --self-test builds a synthetic
run by construction, with no random draw, and checks every count and the decision rule against closed forms.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import tempfile
from pathlib import Path
from typing import Any

from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

from diagnostic_experiments import STATE_PREP_FAMILY, STATE_PREP_REMEASURE_ARMS  # noqa: E402

SCHEMA = "remeasure-history-v1"
ARMS = ("prep0", "x_remeasure", "remeasure")
DECISION_ALPHA = 0.01
DECISION_THRESHOLD = 0.5
# ibm_kingston's measure duration on every qubit in the case-3 stage-2 snapshot
# (docs/evidence/primorial_cover/case3/stage2-snapshot-a.json, instructions.measure).
DEFAULT_MEASURE_US = 2.18


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def clopper_pearson(hits: int, trials: int, alpha: float) -> tuple[float, float]:
    """Two-sided Clopper-Pearson interval at level 1 - alpha; (0, 1) for no trials."""
    if trials == 0:
        return 0.0, 1.0
    lower = 0.0 if hits == 0 else float(stats.beta.ppf(alpha / 2, hits, trials - hits + 1))
    upper = 1.0 if hits == trials else float(stats.beta.ppf(1 - alpha / 2, hits + 1, trials - hits))
    return lower, upper


def fraction(hits: int, trials: int) -> dict[str, Any]:
    lower, upper = clopper_pearson(hits, trials, DECISION_ALPHA)
    return {
        "hits": hits,
        "trials": trials,
        "fraction": hits / trials if trials else math.nan,
        "interval_99": [lower, upper],
    }


def decide(hits: int, trials: int) -> str:
    lower, upper = clopper_pearson(hits, trials, DECISION_ALPHA)
    if trials == 0:
        return "undecided"
    if lower > DECISION_THRESHOLD:
        return "population"
    if upper < DECISION_THRESHOLD:
        return "misassignment"
    return "undecided"


def two_proportion(hit_a: int, n_a: int, hit_b: int, n_b: int) -> dict[str, Any]:
    """P(A) - P(B) with the pooled-variance z and its two-sided normal p-value."""
    pa = hit_a / n_a if n_a else math.nan
    pb = hit_b / n_b if n_b else math.nan
    if n_a and n_b:
        pool = (hit_a + hit_b) / (n_a + n_b)
        se = math.sqrt(pool * (1 - pool) * (1 / n_a + 1 / n_b))
        z = (pa - pb) / se if se > 0 else 0.0
    else:
        z = math.nan
    p_value = math.erfc(abs(z) / math.sqrt(2.0)) if not math.isnan(z) else math.nan
    return {
        "p_given_1": pa,
        "n_given_1": n_a,
        "p_given_0": pb,
        "n_given_0": n_b,
        "difference": pa - pb,
        "z": z,
        "p_two_sided": p_value,
    }


def conditional(target: list[int], given: list[int]) -> dict[str, Any]:
    require(len(target) == len(given), f"{len(target)} target shots against {len(given)} conditioning shots")
    hit_1 = sum(t for t, g in zip(target, given, strict=True) if g)
    n_1 = sum(1 for g in given if g)
    hit_0 = sum(t for t, g in zip(target, given, strict=True) if not g)
    return two_proportion(hit_1, n_1, hit_0, len(given) - n_1)


def member_arm_qubit(member: str) -> tuple[str, int]:
    """spc_ARM_qQ -> (ARM, Q)."""
    require(member.startswith("spc_") and "_q" in member, f"{member}: not a state-prep-control member")
    arm, qubit = member.removeprefix("spc_").rsplit("_q", 1)
    return arm, int(qubit)


def register_bits(pub: dict[str, Any], register: str, bits: int) -> list[list[int]]:
    """The shot-ordered reads of each of the register's bits, bit b the b-th character from the right."""
    data = pub["registers"][register]
    strings = data["bitstrings"]
    require(len(strings) == int(data["num_shots"]), f"{register}: {len(strings)} strings for {data['num_shots']}")
    require(all(len(s) == bits for s in strings), f"{register}: a string is not {bits} bits wide")
    return [[int(s[-1 - b]) for s in strings] for b in range(bits)]


def load_reads(run: Path) -> tuple[dict[str, Any], dict[int, dict[str, list[list[int]]]]]:
    """The run record and, per qubit and arm, the shot-ordered bit lists of its register."""
    record = json.loads((run / "record.json").read_text(encoding="utf-8"))
    configuration = record["family_configuration"]
    require(configuration.get("name") == STATE_PREP_FAMILY, f"{run}: not a state-prep-control record")
    arms = tuple(configuration["arms"])
    require(arms == ARMS, f"{run}: arms {arms}, the analysis needs {ARMS} in that order")
    require(record["policy"]["twirl"] is False, f"{run}: twirling changes the readout the arms compare")
    pubs = record["execution_pubs"]
    require([pub["kind"] for pub in pubs] == ["static"] * 3, f"{run}: PUB kinds {[pub['kind'] for pub in pubs]}")
    jobs = sorted(path for path in (run / "raw").iterdir() if path.is_dir())
    require(len(jobs) == 1, f"{run}: {len(jobs)} raw jobs, the three arms share one")
    index = json.loads((jobs[0] / "index.json").read_text(encoding="utf-8"))
    files = sorted((name for name in index["files"] if name.startswith("pub_")), key=lambda n: int(n[4:-5]))
    require(len(files) == 3, f"{run}: {len(files)} raw PUB files")
    reads: dict[int, dict[str, list[list[int]]]] = {}
    for position, (manifest, name) in enumerate(zip(pubs, files, strict=True)):
        pub = json.loads((jobs[0] / name).read_text(encoding="utf-8"))
        require(int(pub["pub_index"]) == position, f"{name}: pub_index {pub['pub_index']} at position {position}")
        for component in manifest["components"]:
            arm, qubit = member_arm_qubit(component["member"])
            require(arm == ARMS[position], f"{name}: member {component['member']} in the {ARMS[position]} row")
            (registers,) = component["registers_by_replica"]
            (register,) = registers
            reads.setdefault(qubit, {})[arm] = register_bits(
                pub, register, 2 if arm in STATE_PREP_REMEASURE_ARMS else 1
            )
    for qubit, by_arm in reads.items():
        require(set(by_arm) == set(ARMS), f"qubit {qubit}: arms {sorted(by_arm)}")
        shots = {len(bits[0]) for bits in by_arm.values()}
        require(len(shots) == 1, f"qubit {qubit}: shot counts {shots} differ between arms")
    return record, reads


def population_prediction(e01: float, t1_us: float, measure_us: float) -> float:
    """pi under a real population: read 1 again at 1 - e01 after one measurement of T1 decay."""
    return (1.0 - e01) * math.exp(-measure_us / t1_us)


def analyze_qubit(by_arm: dict[str, list[list[int]]]) -> dict[str, Any]:
    (prep0,) = by_arm["prep0"]
    x_first, x_second = by_arm["x_remeasure"]
    r_first, r_second = by_arm["remeasure"]
    shots = len(prep0)
    r_first_one = [s for s in range(shots) if r_first[s]]
    r_first_zero = [s for s in range(shots) if not r_first[s]]
    x_first_zero = [s for s in range(shots) if not x_first[s]]
    x_first_one = [s for s in range(shots) if x_first[s]]
    persist_hits = sum(r_second[s] for s in r_first_one)
    recovered_hits = sum(x_second[s] for s in x_first_zero)
    return {
        "shots": shots,
        "prep0": {"excited": fraction(sum(prep0), shots)},
        "x_remeasure": {
            "first_read_one": fraction(len(x_first_one), shots),
            "second_one_given_first_zero": fraction(recovered_hits, len(x_first_zero)),
            "second_one_given_first_one": fraction(sum(x_second[s] for s in x_first_one), len(x_first_one)),
            "first_zero_reading": decide(recovered_hits, len(x_first_zero)),
        },
        "remeasure": {
            "first_read_one": fraction(len(r_first_one), shots),
            "persistence": fraction(persist_hits, len(r_first_one)),
            "second_one_given_first_zero": fraction(sum(r_second[s] for s in r_first_zero), len(r_first_zero)),
            "reading": decide(persist_hits, len(r_first_one)),
        },
        "link": {
            # The remeasure shot follows the same shot's x_remeasure read.
            "remeasure_first_given_x_remeasure_first": conditional(r_first, x_first),
            "remeasure_first_given_x_remeasure_second": conditional(r_first, x_second),
            # The prep0 shot s + 1 follows the remeasure shot s.
            "next_prep0_given_remeasure_first": conditional(prep0[1:], r_first[:-1]),
            "next_prep0_given_remeasure_second": conditional(prep0[1:], r_second[:-1]),
            # The successor cannot act on its predecessor: the same conditioning one shot later reads no link.
            "remeasure_first_given_next_x_remeasure_first": conditional(r_first[:-1], x_first[1:]),
        },
    }


def analyze(run: Path, prediction: dict[str, float] | None) -> dict[str, Any]:
    record, reads = load_reads(run)
    out: dict[str, Any] = {
        "schema": SCHEMA,
        "run": run.name,
        "experiment_digest": record.get("experiment_digest"),
        "rep_delay_seconds": record["policy"].get("rep_delay_seconds"),
        "decision": {
            "alpha": DECISION_ALPHA,
            "threshold": DECISION_THRESHOLD,
            "rule": "population when the 99 percent interval of pi lies above 0.5, misassignment when below",
        },
        "qubits": {str(qubit): analyze_qubit(by_arm) for qubit, by_arm in sorted(reads.items())},
    }
    if prediction is not None:
        out["population_prediction"] = {
            **prediction,
            "pi": population_prediction(prediction["e01"], prediction["t1_us"], prediction["measure_us"]),
        }
    return out


def _synthetic_run(root: Path) -> tuple[Path, dict[str, Any]]:
    """A run whose bits are laid out by construction; returns the run and the counts the layout fixes."""
    shots = 1000
    # x_remeasure: 940 shots read 1 then 1; 40 read 1 then 0; 19 read 0 then 1 (misassigned, population kept);
    # 1 reads 0 then 0.
    x_pairs = [(1, 1)] * 940 + [(1, 0)] * 40 + [(0, 1)] * 19 + [(0, 0)] * 1
    # remeasure: the first read is 1 in 60 shots, 54 of which read 1 again; 2 of the 940 first-read-0 shots read
    # 1 second. The first-read-1 shots sit on the 20 x_remeasure first-read-0 shots (indices 980 to 999) and on
    # 40 of its first-read-1 shots, so the link reads 20 / 20 against 40 / 980.
    r_pairs = [(0, 0)] * shots
    for index in range(980, 1000):
        r_pairs[index] = (1, 1)
    for index in range(0, 40):
        r_pairs[index] = (1, 1) if index < 34 else (1, 0)
    r_pairs[500] = (0, 1)
    r_pairs[501] = (0, 1)
    # prep0: reads 1 in 10 shots, 8 of them right after a remeasure first read of 1 (shots 1 to 8 follow shots 0
    # to 7) and 2 after a first read of 0 (shots 600 and 601); shot 999's remeasure read has no successor.
    prep0 = [0] * shots
    for index in (1, 2, 3, 4, 5, 6, 7, 8, 600, 601):
        prep0[index] = 1
    run = root / "2026-01-01T000000.000000Z"
    job = run / "raw" / "job_synthetic"
    job.mkdir(parents=True)
    record = {
        "family_configuration": {"name": STATE_PREP_FAMILY, "qubits": [7], "arms": dict.fromkeys(ARMS, "")},
        "policy": {"twirl": False, "rep_delay_seconds": 2e-05},
        "experiment_digest": "synthetic",
        "execution_pubs": [
            {
                "kind": "static",
                "components": [{"member": f"spc_{arm}_q7", "registers_by_replica": [[f"g0_r0_{arm}"]]}],
            }
            for arm in ARMS
        ],
    }
    (run / "record.json").write_text(json.dumps(record), encoding="utf-8")
    pubs = {
        "prep0": [str(bit) for bit in prep0],
        "x_remeasure": [f"{second}{first}" for first, second in x_pairs],
        "remeasure": [f"{second}{first}" for first, second in r_pairs],
    }
    files = {}
    for position, arm in enumerate(ARMS):
        name = f"pub_{position:02d}.json"
        payload = {
            "pub_index": position,
            "registers": {f"g0_r0_{arm}": {"bitstrings": pubs[arm], "num_shots": shots}},
        }
        (job / name).write_text(json.dumps(payload), encoding="utf-8")
        files[name] = ""
    (job / "index.json").write_text(json.dumps({"files": files, "job_id": "job_synthetic"}), encoding="utf-8")
    expected = {
        "shots": shots,
        "prep0_hits": 10,
        "x_first_one": 980,
        "x_recovered": (19, 20),
        "r_first_one": 60,
        "r_persist": (54, 60),
        "r_second_given_first_zero": (2, 940),
        "link_given_x_first": (20, 20, 40, 980),
        "next_prep0": (8, 59, 2, 940),
    }
    return run, expected


def self_test() -> None:
    with tempfile.TemporaryDirectory() as scratch:
        run, expected = _synthetic_run(Path(scratch))
        report = analyze(run, {"e01": 0.0076, "t1_us": 350.0, "measure_us": DEFAULT_MEASURE_US})
    qubit = report["qubits"]["7"]
    checks = {
        "shots": qubit["shots"] == expected["shots"],
        "prep0": qubit["prep0"]["excited"]["hits"] == expected["prep0_hits"],
        "x first": qubit["x_remeasure"]["first_read_one"]["hits"] == expected["x_first_one"],
        "x recovered": (
            qubit["x_remeasure"]["second_one_given_first_zero"]["hits"],
            qubit["x_remeasure"]["second_one_given_first_zero"]["trials"],
        )
        == expected["x_recovered"],
        "r first": qubit["remeasure"]["first_read_one"]["hits"] == expected["r_first_one"],
        "r persist": (qubit["remeasure"]["persistence"]["hits"], qubit["remeasure"]["persistence"]["trials"])
        == expected["r_persist"],
        "r second given zero": (
            qubit["remeasure"]["second_one_given_first_zero"]["hits"],
            qubit["remeasure"]["second_one_given_first_zero"]["trials"],
        )
        == expected["r_second_given_first_zero"],
        "reading": qubit["remeasure"]["reading"] == "population",
        "x first-zero reading": qubit["x_remeasure"]["first_zero_reading"] == "population",
    }
    link = qubit["link"]["remeasure_first_given_x_remeasure_first"]
    a, n_a, b, n_b = expected["link_given_x_first"]
    checks["link"] = (link["n_given_0"], link["n_given_1"]) == (n_a, n_b) and math.isclose(
        link["p_given_0"] - link["p_given_1"], a / n_a - b / n_b
    )
    nxt = qubit["link"]["next_prep0_given_remeasure_first"]
    a, n_a, b, n_b = expected["next_prep0"]
    checks["next prep0"] = (nxt["n_given_1"], nxt["n_given_0"]) == (n_a, n_b) and math.isclose(
        nxt["p_given_1"], a / n_a
    )
    failed = [name for name, passed in checks.items() if not passed]
    require(not failed, f"synthetic counts differ: {failed}")
    # The decision rule against closed forms: 54 of 60 has a 99 percent lower end above 0.5, 15 of 60 an upper
    # end below 0.5, and 30 of 60 straddles it.
    require(decide(54, 60) == "population", "54 of 60 is a population")
    require(decide(15, 60) == "misassignment", "15 of 60 is a misassignment")
    require(decide(30, 60) == "undecided" and decide(0, 0) == "undecided", "30 of 60 and no trials are undecided")
    lower, upper = clopper_pearson(54, 60, DECISION_ALPHA)
    beta_lower = float(stats.beta.ppf(0.005, 54, 7))
    beta_upper = float(stats.beta.ppf(0.995, 55, 6))
    require(math.isclose(lower, beta_lower) and math.isclose(upper, beta_upper), "Clopper-Pearson moved")
    require(
        math.isclose(sum(math.comb(60, k) * lower**k * (1 - lower) ** (60 - k) for k in range(54, 61)), 0.005),
        "the lower end does not invert the binomial tail",
    )
    pi = report["population_prediction"]["pi"]
    require(math.isclose(pi, (1 - 0.0076) * math.exp(-DEFAULT_MEASURE_US / 350.0)), "the population prediction moved")
    print(
        f"remeasure_history: the synthetic run reproduces every count, pi 54/60 reads population, the link "
        f"reads 20/20 against 40/980, the rule's three verdicts match closed forms, and a q147-like population "
        f"predicts pi {pi:.4f}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("run", nargs="?", type=Path, help="a collected state-prep-control run directory")
    parser.add_argument("--out", type=Path, help="write the JSON report here instead of stdout")
    parser.add_argument("--e01", type=float, help="prob_meas0_prep1 of the qubit the population prediction is for")
    parser.add_argument("--t1-us", type=float, help="T1 in microseconds of that qubit")
    parser.add_argument("--measure-us", type=float, default=DEFAULT_MEASURE_US, help="measure duration in us")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        self_test()
        return 0
    if args.run is None:
        parser.error("a run directory or --self-test is required")
    if (args.e01 is None) != (args.t1_us is None):
        parser.error("--e01 and --t1-us come together")
    prediction = None
    if args.e01 is not None:
        prediction = {"e01": args.e01, "t1_us": args.t1_us, "measure_us": args.measure_us}
    report = analyze(args.run, prediction)
    text = json.dumps(report, indent=1, sort_keys=True) + "\n"
    if args.out is None:
        sys.stdout.write(text)
    else:
        args.out.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
