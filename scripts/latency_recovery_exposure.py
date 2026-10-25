"""Executed idle exposures and window rates of a collected latency-recovery run.

The configured windows L and W are delays the circuit requests; the controller
overlaps a requested delay with the feed-forward broadcast, so the exposure an
arm actually accrues comes from the returned schedule. For every member the
script reads ``metadata.compilation.scheduler_timing`` in raw/<job>/pub_NN.json
and takes the exposure as the cycles from the end of the syndrome captures to
the first main-branch CZ after them, the start of the decode. Every basis of an
arm must share one exposure.

From the collect.json summary it then reports, for each window pair
(ff_0 to ff_w, frame_l to frame_lw), on the executed exposure increment dt:

- the finite-window fidelity-loss slope (F(0) - F(W)) / dt;
- the rate -ln(F(W) / F(0)) / dt, which equals an exponential law's
  parameter only if F decays exponentially;
- the coherence rate -ln(C(W) / C(0)) / dt and the phase frequency
  (phi(W) - phi(0)) / (2 pi dt);
- the slope of the phase-removed fidelity (1 + 2C + ZZ) / 4.

The output is printed JSON and is descriptive; the preregistered contracts
stay in collect.json's family_analysis. ``--self-test`` exercises the
extraction on a synthetic schedule.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PAIRS = (("ff_0", "ff_w"), ("frame_l", "frame_lw"))
LATENCY_PAIRS = (("ff_0", "frame_0"), ("ff_0", "frame_l"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def exposure(timing: str) -> int | None:
    """Cycles from the end of the syndrome captures to the first main-branch CZ after them."""
    rows = [line.split(",") for line in timing.splitlines()]
    ends = [
        int(row[3]) + int(row[4])
        for row in rows
        if row[5] == "capture" and row[0] == "main" and row[1].startswith("measure")
    ]
    require(bool(ends), "no syndrome capture in the schedule")
    # The two syndrome captures are the earliest measurements and end together.
    syndrome_end = min(ends)
    decode = [
        int(row[3]) for row in rows if row[0] == "main" and row[1].startswith("cz_") and int(row[3]) > syndrome_end
    ]
    return min(decode) - syndrome_end if decode else None


def member_exposures(run: Path) -> dict[str, int | None]:
    collect = json.loads((run / "collect.json").read_text())
    groups = [entry for entry in collect if isinstance(entry, dict) and entry.get("group")]
    require(len(groups) == 1, f"{run}: expected one collected group")
    executed = groups[0]["executed"]
    pubs: dict[str, Path] = {}
    for path in sorted(run.glob("raw/*/pub_*.json")):
        pubs[json.loads(path.read_text())["pub_name"]] = path
    out = {}
    for member, row in executed.items():
        payload = json.loads(pubs[row["pub"]].read_text())
        out[member] = exposure(payload["metadata"]["compilation"]["scheduler_timing"]["timing"])
    return out


def arm_exposures(members: dict[str, int | None]) -> dict[str, int | None]:
    """One exposure per arm and error state, required equal across the arm's bases."""
    arms: dict[str, set[int | None]] = {}
    for member, value in members.items():
        stem = member.removeprefix("lr_").rsplit("_", 1)[0]
        arms.setdefault(stem, set()).add(value)
    for stem, values in arms.items():
        require(len(values) == 1, f"{stem}: bases differ in exposure {sorted(values, key=str)}")
    return {stem: next(iter(values)) for stem, values in sorted(arms.items())}


def rates(summary: dict[str, float], arms: dict[str, int | None], dt_seconds: float) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for start, end in PAIRS:
        a, b = arms[f"{start}_err"], arms[f"{end}_err"]
        if a is None or b is None or b <= a:
            raise ValueError(f"{start} to {end}: exposures {a}, {b}")
        cycles = b - a
        microseconds = cycles * dt_seconds * 1e6

        def value(arm: str, key: str) -> float:
            return float(summary[f"{arm}_err_{key}"])

        f0, f1 = value(start, "F"), value(end, "F")
        c0, c1 = value(start, "C"), value(end, "C")
        removed = [(1 + 2 * value(arm, "C") + value(arm, "ZZ_expectation")) / 4 for arm in (start, end)]
        out[f"{start}_to_{end}"] = {
            "exposure_increment_cycles": cycles,
            "exposure_increment_us": microseconds,
            "fidelity_loss": f0 - f1,
            "fidelity_slope_per_us": (f0 - f1) / microseconds,
            "fidelity_log_rate_per_us": -math.log(f1 / f0) / microseconds,
            "coherence_rate_per_us": -math.log(c1 / c0) / microseconds,
            "coherence_time_constant_us": microseconds / -math.log(c1 / c0),
            "phase_frequency_khz": (value(end, "phi") - value(start, "phi")) / (2 * math.pi * microseconds) * 1e3,
            "phase_removed_slope_per_us": (removed[0] - removed[1]) / microseconds,
        }
    for first, second in LATENCY_PAIRS:
        a, b = arms[f"{first}_err"], arms[f"{second}_err"]
        out[f"{first}_minus_{second}_exposure_cycles"] = None if a is None or b is None else int(a) - int(b)
    return out


def report(run: Path) -> dict[str, Any]:
    record = json.loads((run / "record.json").read_text())
    dt_seconds = float(record["family_configuration"]["dt_seconds"])
    collect = json.loads((run / "collect.json").read_text())
    summary = next(entry for entry in collect if isinstance(entry, dict) and entry.get("group"))["measured_statistics"][
        "summary"
    ]
    arms = arm_exposures(member_exposures(run))
    return {"run": str(run.relative_to(ROOT)), "exposure_cycles": arms, "windows": rates(summary, arms, dt_seconds)}


SYNTHETIC = "\n".join(
    [
        "main,cz_1_4,Qubit 1,100,25,shift_phase",
        "main,measure_4,Qubit 4,200,64,play",
        "main,measure_4,AWGR1_4,321,325,capture",
        "main,measure_5,AWGR1_5,321,325,capture",
        "then,x_1,Qubit 1,900,8,play",
        "main,cz_1_3,Qubit 1,946,25,shift_phase",
        "main,measure_1,AWGR1_1,1200,325,capture",
    ]
)


def self_test() -> str:
    require(exposure(SYNTHETIC) == 300, f"exposure {exposure(SYNTHETIC)}")
    require(exposure(SYNTHETIC.replace("main,cz_1_3,Qubit 1,946,25,shift_phase\n", "")) is None, "no decode")
    try:
        arm_exposures({"lr_ff_0_err_XX": 300, "lr_ff_0_err_YY": 301})
    except ValueError:
        pass
    else:
        raise ValueError("bases with unequal exposures were accepted")
    summary = {
        f"{arm}_err_{key}": value
        for arm, values in (("ff_0", (0.8, 0.7, 0.0, 0.7)), ("ff_w", (0.6, 0.5, -0.5, 0.6)))
        for key, value in zip(("F", "C", "phi", "ZZ_expectation"), values, strict=True)
    } | {
        f"{arm}_err_{key}": value
        for arm, values in (("frame_l", (0.8, 0.7, 0.0, 0.7)), ("frame_lw", (0.7, 0.6, -0.4, 0.65)))
        for key, value in zip(("F", "C", "phi", "ZZ_expectation"), values, strict=True)
    }
    arms: dict[str, int | None] = {
        "ff_0_err": 300,
        "ff_w_err": 2800,
        "frame_l_err": 300,
        "frame_lw_err": 2800,
        "frame_0_err": 100,
    }
    got = rates(summary, arms, 4e-9)["ff_0_to_ff_w"]
    require(math.isclose(got["exposure_increment_us"], 10.0), str(got))
    require(math.isclose(got["fidelity_slope_per_us"], 0.02), str(got))
    require(math.isclose(got["fidelity_log_rate_per_us"], -math.log(0.6 / 0.8) / 10), str(got))
    require(math.isclose(got["phase_frequency_khz"], -0.5 / (2 * math.pi * 10) * 1e3), str(got))
    return "latency_recovery_exposure self-test passed"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--run", type=Path, help="a collected latency-recovery run directory")
    mode.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        print(self_test())
        return 0
    print(json.dumps(report(args.run.resolve()), indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
