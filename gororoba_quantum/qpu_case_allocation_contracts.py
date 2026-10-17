"""Reject incomplete allocated QPU cases and preserve their artifact bindings."""

from __future__ import annotations

import argparse
import copy
import json
import math
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import patch

from qiskit import QuantumCircuit, qpy

import qpu_cases


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def fixture() -> dict[str, Any]:
    record = qpu_cases._fixture()
    record["family_configuration"]["name"] = "ripple"
    design = record["policy"]["design"]
    design.update(
        family="ripple", shot_allocation="per-pub", shot_tiers=[1024, 4096], max_total_execution_seconds=180.0
    )
    design["cost_scenarios"] = [
        {"name": "controller-stress", "job_overhead_seconds": 4.6, "classical_latency_us": 40.0}
    ]
    record["shots"] = 4096
    record["pub_shots"] = {"low_pub": 1024, "high_pub": 4096, "high_control_pub": 4096}
    record["execution_pubs"] = [{"name": name, "backend": "ibm_fez", "kind": "static"} for name in record["pub_shots"]]
    candidate = record["optimization"]["candidates"][0]
    candidate["name"] = record["optimization"]["selected"] = "allocated-fixture"
    source_pub = candidate["jobs"][0]["pubs"][0]
    candidate["jobs"] = []
    budget_jobs = []
    for index, tier in enumerate((1024, 4096), 1):
        pubs = [
            dict(source_pub, name=name, shots=tier, classical_stage_count=0, classical_latency_seconds=0.0)
            for name, shots in record["pub_shots"].items()
            if shots == tier
        ]
        candidate["jobs"].append(
            dict(name=f"ibm_fez/static/{index}", pubs=pubs, overhead_seconds=2.3, max_execution_seconds=90)
        )
        budget_jobs.append(
            dict(
                backend="ibm_fez",
                kind="static",
                batch_index=index,
                pubs=len(pubs),
                pub_names=[pub["name"] for pub in pubs],
                ceiling_seconds=90,
                shots=tier,
            )
        )
    candidate["total_execution_ceiling_seconds"] = 180.0
    candidate["cost_scenarios"] = [
        {"name": "controller-stress", "feasible": True, "jobs": copy.deepcopy(candidate["jobs"])}
    ]
    for job in candidate["cost_scenarios"][0]["jobs"]:
        job["overhead_seconds"] = 4.6
    record["budget_plan"].update(jobs=budget_jobs, combined_ceiling_seconds=180.0, max_total_execution_seconds=180.0)
    reprice(record)
    return record


def reprice(record: dict[str, Any]) -> None:
    candidate = record["optimization"]["candidates"][0]
    for ledger in [candidate, *candidate["cost_scenarios"]]:
        for job in ledger["jobs"]:
            for pub in job["pubs"]:
                pub["estimated_execution_seconds"] = pub["shots"] * math.fsum(
                    pub[key]
                    for key in (
                        "scheduled_seconds",
                        "repetition_delay_seconds",
                        "reset_seconds",
                        "classical_latency_seconds",
                    )
                )
            job["estimated_charge_seconds"] = math.fsum(
                [job["overhead_seconds"], *(pub["estimated_execution_seconds"] for pub in job["pubs"])]
            )
        ledger["estimated_charge_seconds"] = math.fsum(job["estimated_charge_seconds"] for job in ledger["jobs"])
    candidate["worst_case_charge_seconds"] = max(
        ledger["estimated_charge_seconds"] for ledger in [candidate, *candidate["cost_scenarios"]]
    )


def parsed_reproduction(arguments: list[str]) -> argparse.Namespace:
    """Use the real CLI parser, stopping before any service or preparation call."""
    import live_run

    class ParsedArguments(Exception):
        def __init__(self, namespace: argparse.Namespace):
            self.namespace = namespace

    original_parse = argparse.ArgumentParser.parse_args

    def capture(parser: argparse.ArgumentParser, args: Any = None, namespace: Any = None) -> argparse.Namespace:
        raise ParsedArguments(original_parse(parser, args, namespace))

    with patch.object(argparse.ArgumentParser, "parse_args", capture):
        try:
            live_run.main(arguments)
        except ParsedArguments as captured:
            return captured.namespace
    raise RuntimeError("reproduction did not reach the live CLI parser")


def verify() -> dict[str, Any]:
    record = fixture()
    with tempfile.TemporaryDirectory(prefix="qpu-allocated-case-check-") as temporary:
        run_dir = Path(temporary) / "allocated-run"
        run_dir.mkdir()
        circuits = [QuantumCircuit(1, 1, name=pub["name"]) for pub in record["execution_pubs"]]
        for circuit in circuits:
            circuit.measure(0, 0)
        with (run_dir / "isa.qpy").open("wb") as handle:
            qpy.dump(circuits, handle)

        def retain(value: dict[str, Any]) -> None:
            (run_dir / "record.json").write_text(json.dumps(value, sort_keys=True) + "\n")

        for family in ("ripple", "rank-sector"):
            record["family_configuration"]["name"] = record["policy"]["design"]["family"] = family
            retain(record)
            destination = qpu_cases.write_case(run_dir, record)
            require(destination is not None, "allocated case was rejected")
            if destination is None:
                raise RuntimeError("case destination is absent")
            text = destination.read_text()
            require(
                "per-PUB shot allocation (used tiers: 1024, 4096; 2 jobs)" in text, "allocation description is absent"
            )
            require("4096 shots per PUB" not in text, "case falsely declares uniform shots")
            require("| low_pub | 1024 |" in text and "| high_pub | 4096 |" in text, "PUB shot ledger is incomplete")
            arguments = qpu_cases._reproduction_arguments(record, Path("results/live/allocated-run"))
            parsed = parsed_reproduction(arguments)
            require(
                parsed.shot_allocation == "per-pub" and parsed.optimize is True, "reproduction loses allocation mode"
            )
            require(parsed.shot_tiers == [1024, 4096] and parsed.shots == 4096, "reproduction loses shot domain")
            require(
                parsed.max_execution_seconds == 90 and parsed.max_total_execution_seconds == 180.0,
                "reproduction loses aggregate ceilings",
            )
            require(parsed.family == family and parsed.submit is False, "reproduction changes family or submits")
        historical = qpu_cases._fixture()
        arguments = qpu_cases._reproduction_arguments(historical, Path("results/live/historical-run"))
        require("--shot-allocation" not in arguments, "legacy reproduction acquired a new option")
        historical["policy"]["design"]["shot_allocation"] = "uniform"
        arguments = qpu_cases._reproduction_arguments(historical, Path("results/live/historical-run"))
        require(parsed_reproduction(arguments).shot_allocation == "uniform", "explicit uniform policy was lost")

        record["family_configuration"]["name"] = record["policy"]["design"]["family"] = "ripple"
        retain(record)
        destination = qpu_cases.write_case(run_dir, record)
        if destination is None:
            raise RuntimeError("case destination is absent")
        case_bytes = destination.read_bytes()
        rejected = 0

        def rejects(changed: dict[str, Any], message: str) -> None:
            nonlocal rejected
            retain(changed)
            before = {name: (run_dir / name).read_bytes() for name in ("record.json", "isa.qpy")}
            try:
                qpu_cases.write_case(run_dir, changed)
            except ValueError as error:
                require(message in str(error), f"unexpected allocation rejection: {error}")
            else:
                raise RuntimeError(f"case admitted mutation requiring {message!r}")
            require(destination.read_bytes() == case_bytes, "rejected mutation overwrote the retained case")
            require(
                all((run_dir / name).read_bytes() == value for name, value in before.items()), "case changed its inputs"
            )
            rejected += 1

        selected = ("optimization", "candidates", 0)
        first_pub = (*selected, "jobs", 0, "pubs", 0)
        scenario = (*selected, "cost_scenarios", 0)
        design = ("policy", "design")
        missing = object()
        mutations = [
            (("pub_shots", "low_pub"), missing, "complete execution-PUB manifest"),
            (("pub_shots", "extra_pub"), 1024, "complete execution-PUB manifest"),
            (("pub_shots",), None, "complete mapping"),
            (("pub_shots", "low_pub"), True, "positive integer"),
            (("pub_shots", "low_pub"), 1024.0, "positive integer"),
            (("pub_shots", "low_pub"), 0, "positive integer"),
            (("pub_shots", "low_pub"), -1, "positive integer"),
            (("pub_shots", "low_pub"), 2048, "declared tier domain"),
            (("shots",), 1024, "allocation maximum"),
            ((*design, "shot_allocation"), "uniform", "uniform design carries"),
            ((*design, "shot_allocation"), "unknown", "unknown shot allocation"),
            ((*design, "optimize"), False, "optimized algebra or patch family"),
            ((*design, "shot_tiers"), [4096, 1024], "unique and increasing"),
            (("execution_pubs", 0, "kind"), "dynamic", "static execution PUBs"),
            (("execution_pubs", 1, "name"), "low_pub", "identities must be unique"),
            (("budget_plan", "jobs"), [], "reserve every selected job"),
            (("budget_plan", "jobs", 0, "pub_names"), [], "membership or order"),
            (("budget_plan", "jobs", 1, "pub_names"), ["high_control_pub", "high_pub"], "membership or order"),
            (("budget_plan", "jobs", 0, "pubs"), 2, "PUB count differs"),
            (("budget_plan", "jobs", 0, "shots"), 4096, "budget shots differ"),
            (("budget_plan", "jobs", 0, "batch_index"), 2, "job identity differs"),
            (("budget_plan", "jobs", 0, "ceiling_seconds"), 60, "budget ceiling differs"),
            (("execution_pubs", 0, "backend"), "ibm_kingston", "backend or kind differs"),
            ((*first_pub, "shots"), 4096, "PUB shots differ"),
            ((*first_pub, "classical_stage_count"), 1, "zero classical stages"),
            ((*scenario, "jobs", 0, "pubs", 0, "shots"), 4096, "PUB shots differ"),
            ((*scenario, "jobs", 0, "pubs", 0, "classical_stage_count"), False, "zero classical stages"),
            ((*scenario, "jobs", 0, "name"), "ibm_fez/static/3", "job identity differs"),
            ((*scenario, "jobs"), [], "changed the job count"),
            ((*scenario, "feasible"), False, "scenario fails admission"),
            ((*selected, "cost_scenarios"), [], "scenarios differ"),
            ((*selected, "worst_case_charge_seconds"), 1.0, "envelope disagrees"),
        ]
        for path, value, expected in mutations:
            changed = copy.deepcopy(record)
            owner: Any = changed
            for key in path[:-1]:
                owner = owner[key]
            if value is missing:
                del owner[path[-1]]
            else:
                owner[path[-1]] = value
            rejects(changed, expected)
        changed = copy.deepcopy(record)
        candidate = changed["optimization"]["candidates"][0]
        candidate["jobs"][0]["pubs"].extend(candidate["jobs"].pop()["pubs"])
        candidate["total_execution_ceiling_seconds"] = changed["budget_plan"]["combined_ceiling_seconds"] = 90.0
        reprice(changed)
        rejects(changed, "one PUB shot count")
        changed = copy.deepcopy(record)
        changed["optimization"]["candidates"][0]["cost_scenarios"][0]["jobs"][0]["pubs"][0]["scheduled_seconds"] *= 2
        reprice(changed)
        rejects(changed, "changed the compiled workload")
        changed = copy.deepcopy(record)
        changed["optimization"]["candidates"][0]["jobs"][1]["pubs"].reverse()
        changed["budget_plan"]["jobs"][1]["pub_names"].reverse()
        rejects(changed, "tier PUB order differs")
        changed = copy.deepcopy(record)
        changed["budget_plan"]["jobs"][1]["batch_index"] = 3
        changed["optimization"]["candidates"][0]["jobs"][1]["name"] = "ibm_fez/static/3"
        rejects(changed, "canonical batch sequence")
        # A dynamic patch job's latency equals its stage count times the
        # declared classical latency; halving one PUB's latency is refused.
        dynamic = copy.deepcopy(record)
        dynamic["family_configuration"]["name"] = dynamic["policy"]["design"]["family"] = "patch-window"
        latency_us = dynamic["policy"]["design"]["classical_latency_us"]
        candidate = dynamic["optimization"]["candidates"][0]
        for ledger in [candidate, *candidate["cost_scenarios"]]:
            ledger["jobs"][0]["name"] = "ibm_fez/dynamic/1"
            for pub in ledger["jobs"][0]["pubs"]:
                pub["classical_stage_count"] = 2
                pub["classical_latency_seconds"] = 2 * latency_us * 1e-6
        dynamic["budget_plan"]["jobs"][0]["kind"] = "dynamic"
        reprice(dynamic)
        qpu_cases._validate_costs(candidate, dynamic)
        candidate["jobs"][0]["pubs"][0]["classical_latency_seconds"] = latency_us * 1e-6
        reprice(dynamic)
        try:
            qpu_cases._validate_costs(candidate, dynamic)
        except ValueError as error:
            require("differs from its stages" in str(error), f"unexpected latency rejection: {error}")
            rejected += 1
        else:
            raise RuntimeError("case admitted a dynamic PUB latency below its declared stages")
        # A cost scenario prices the dynamic stages at its own classical
        # latency while the nominal ledger keeps the declared latency.
        scenario_dynamic = copy.deepcopy(record)
        scenario_dynamic["family_configuration"]["name"] = "patch-window"
        scenario_design = scenario_dynamic["policy"]["design"]
        scenario_design["family"] = "patch-window"
        nominal_us = scenario_design["classical_latency_us"]
        stress_us = scenario_design["cost_scenarios"][0]["classical_latency_us"]
        require(stress_us != nominal_us, "the scenario fixture must change the classical latency")
        candidate = scenario_dynamic["optimization"]["candidates"][0]
        for ledger, ledger_us in ((candidate, nominal_us), (candidate["cost_scenarios"][0], stress_us)):
            ledger["jobs"][0]["name"] = "ibm_fez/dynamic/1"
            ledger["jobs"][1]["name"] = "ibm_fez/static/1"
            for pub in ledger["jobs"][0]["pubs"]:
                pub["classical_stage_count"] = 2
                pub["classical_latency_seconds"] = 2 * ledger_us * 1e-6
        dynamic_job, static_job = scenario_dynamic["budget_plan"]["jobs"]
        dynamic_job["kind"] = "dynamic"
        static_job["batch_index"] = 1
        for pub in scenario_dynamic["execution_pubs"]:
            if pub["name"] in dynamic_job["pub_names"]:
                pub["kind"] = "dynamic"
        reprice(scenario_dynamic)
        qpu_cases._validate_costs(candidate, scenario_dynamic)
        qpu_cases._validate_allocated_scenarios(candidate, scenario_dynamic)
        nominal_priced = copy.deepcopy(scenario_dynamic)
        candidate = nominal_priced["optimization"]["candidates"][0]
        for pub in candidate["cost_scenarios"][0]["jobs"][0]["pubs"]:
            pub["classical_latency_seconds"] = 2 * nominal_us * 1e-6
        reprice(nominal_priced)
        try:
            qpu_cases._validate_allocated_scenarios(candidate, nominal_priced)
        except ValueError as error:
            require("differs from its stages" in str(error), f"unexpected scenario latency rejection: {error}")
            rejected += 1
        else:
            raise RuntimeError("case admitted a scenario ledger priced at the nominal classical latency")
        retain(record)
        require(qpu_cases.write_case(run_dir, record) == destination, "valid allocation stopped reproducing")
        require(destination.read_bytes() == case_bytes, "allocated case reproduction changed bytes")
    return {
        "schema": "qpu-case-allocation-contracts-v1",
        "families": ["ripple", "rank-sector"],
        "rejected_mutations": rejected,
        "historical_option_omission": True,
        "explicit_uniform_option": True,
        "live_parser_reproduction": True,
        "artifact_preservation": True,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
