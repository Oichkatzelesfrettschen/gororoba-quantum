"""Inventory of the installed qiskit-ibm-runtime controls, and a read-only backend snapshot.

``--out FILE`` (offline) writes the inventory of the installed package:

- every field of every options class that the client-side primitives
  (``executor_sampler.Sampler``, ``executor_estimator.Estimator``,
  ``Executor``, ``NoiseLearnerV3``, ``Calibrator``) and the deprecated
  server-side ``SamplerV2`` and ``EstimatorV2`` accept, nested classes
  included: its path, the source text of its annotation and default, the
  default its docstring states, its Literal values and numeric bounds, and
  the release whose validator deprecates it;
- the defaults ``finalize_sampler_options`` and ``finalize_estimator_options``
  resolve, and the twirling shot split ``calculate_twirling_shots`` computes;
- the REST adaptors under ``api/rest`` (path templates, HTTP verbs, payload
  keys) and the ``IBM-API-Version`` header they send;
- the deprecation sites of the primitives and option models;
- offline ``prepare()`` probes on FakeFez that record which option and
  circuit combinations the client-side Sampler and Estimator accept, and the
  error each rejection raises.

Types and defaults are the ``ast`` text of the installed source, Literal
values and bounds come from the runtime annotations, and the package's own
exception messages are kept verbatim; messages of third-party exceptions
(samplomatic, qiskit) are reduced to their class so a dependency release
that keeps the behavior keeps the inventory.

``--check FILE`` regenerates the inventory and requires FILE to equal it,
requires the installed versions of the packages the probes exercise to equal
the versions FILE records, requires each generated block of the
hardware-controls note (the backend table included, rendered from the
retained snapshot) to equal ``--render``, and validates the schema of the
backend snapshot: its backend set equals ``accessible_backends`` and its
qiskit-ibm-runtime version equals RUNTIME_VERSION.

``--render`` prints the generated blocks with their markers.

``--self-test`` (offline) feeds each check a corrupted copy of the retained
records and requires the matching rejection.

``--backends FILE`` (network, read-only) reads the account's backends through
QiskitRuntimeService: ``backends()``, ``usage()``, and for each backend
``backends()`` returns ``configuration()``, ``status()``, ``properties()`` and the Target,
plainly and with ``use_fractional_gates=True``, then transpiles an
out-of-range ``rzz`` locally against the fractional Target. Each call carries
its UTC time. The instance appears only as the 12-hex sha256 of its CRN;
``instance_id`` and ``plan_id`` are dropped. Nothing is submitted.

Usage: "$PYTHON" scripts/ibm_runtime_options_inventory.py
       (--out FILE | --check FILE | --render | --backends FILE | --self-test)
"""

from __future__ import annotations

import argparse
import ast
import copy
import datetime
import hashlib
import importlib
import inspect
import json
import math
import os
import re
import statistics
import sys
import textwrap
import unicodedata
from collections.abc import Callable, Iterator
from functools import cache, partial
from pathlib import Path
from typing import Any, Literal, get_args, get_origin

ROOT = Path(__file__).resolve().parents[1]
# CI sets it so a version mismatch fails instead of replaying the retained inventory (ci/pins.py).
PINS_REQUIRED = "GOROROBA_PINS_REQUIRED"
NOTE = ROOT / "docs/notes/ibm_quantum/hardware-controls.md"
BACKENDS = ROOT / "docs/evidence/ibm_runtime_options/backends.json"
SCHEMA = "ibm-runtime-options-inventory-v1"
BACKENDS_SCHEMA = "ibm-runtime-backend-controls-v1"
RUNTIME_VERSION = "0.50.0"
REQUIREMENTS = ROOT / "requirements.txt"
PACKAGE = "qiskit_ibm_runtime"
# Distributions whose versions shape the probe outcomes; None records an absent one.
PROBE_PACKAGES = ("qiskit", "samplomatic", "pydantic", "qiskit-mitigation", "ibm-quantum-schemas")

# (label, module, class, primitive that accepts the options)
ROOTS = (
    ("client Sampler", "options_models", "SamplerOptions", "executor_sampler.Sampler"),
    ("client Estimator", "options_models", "EstimatorOptions", "executor_estimator.Estimator"),
    ("Executor", "options_models", "ExecutorOptions", "Executor"),
    ("NoiseLearnerV3", "options_models", "NoiseLearnerV3Options", "NoiseLearnerV3"),
    ("Calibrator", "options_models.calibrator", "CalibratorOptions", "calibrator.Calibrator"),
    ("server SamplerV2", "options", "SamplerOptions", "SamplerV2"),
    ("server EstimatorV2", "options", "EstimatorOptions", "EstimatorV2"),
)
DEPRECATION_MODULES = (
    "sampler",
    "estimator",
    "options_models.environment",
    "options_models.post_selection",
    "options_models.base",
    "options.measure_noise_learning_options",
)
REST_MODULES = ("runtime", "cloud_backend", "program_job", "runtime_session")
TWIRL_SHOTS = (1024, 4096, 8192, 65536, 100000, 122880)
BLOCKS = ("rest", "options", "behavior", "backends", "usage")
ASCII = {
    "\u2013": "--",
    "\u2014": "--",
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2026": "...",
    "\u25b8": ">",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def ascii_text(text: str) -> str:
    """Project text the checked-in files carry: ASCII, IBM's dashes and glyphs spelled out."""
    text = "".join(ASCII.get(character, character) for character in text)
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")


def module(name: str) -> Any:
    return importlib.import_module(f"{PACKAGE}.{name}")


@cache
def module_tree(name: str) -> ast.Module:
    return ast.parse(inspect.getsource(importlib.import_module(name)))


def doc_paragraph(doc: str | None) -> str:
    if not doc:
        return ""
    first = inspect.cleandoc(doc).split("\n\n", 1)[0]
    return ascii_text(" ".join(first.replace("``", "`").split()))


def args_docs(doc: str | None) -> dict[str, str]:
    """Entries of a Google-style "Args:" section, for fields documented on the class rather than the field."""
    if not doc or "Args:" not in doc:
        return {}
    entries: dict[str, str] = {}
    name = None
    for line in inspect.cleandoc(doc).split("Args:", 1)[1].splitlines():
        match = re.match(r"    (\w+): (.*)", line)
        if match:
            name = match.group(1)
            entries[name] = match.group(2)
        elif name and line.startswith("        "):
            entries[name] += "\n" + line.strip()
        elif line.strip() and not line.startswith(" "):
            break
        elif not line.strip() and name:
            entries[name] += "\n"
    return entries


def doc_sentence(doc: str | None) -> str:
    paragraph = doc_paragraph(doc)
    match = re.search(r"(?<=[.:])\s", paragraph)
    return paragraph[: match.start()] if match else paragraph


def documented_default(doc: str | None) -> str | None:
    """The text after "Default:" or "Default is" up to the next blank line, backticks reduced."""
    if not doc:
        return None
    match = re.search(r"Default(?: is|:)\s*(.*?)(?:\n\s*\n|\Z)", inspect.cleandoc(doc), re.DOTALL)
    if match is None:
        return None
    return ascii_text(" ".join(match.group(1).replace("``", "`").split()))


def deprecation_call(node: ast.AST) -> dict[str, str] | None:
    """The msg and version of the first issue_deprecation_msg call under node."""
    for call in ast.walk(node):
        if isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id == "issue_deprecation_msg":
            keywords = {k.arg: k.value for k in call.keywords if k.arg in ("msg", "version")}
            return {key: ascii_text(str(ast.literal_eval(value))) for key, value in sorted(keywords.items())}
    return None


@cache
def class_source(cls: type) -> dict[str, Any]:
    """Field annotations, defaults, docstrings, bound validators and deprecating validators of one class body."""
    tree = ast.parse(textwrap.dedent(inspect.getsource(cls)))
    body = next(node for node in tree.body if isinstance(node, ast.ClassDef)).body
    functions = {node.name: node for node in module_tree(cls.__module__).body if isinstance(node, ast.FunctionDef)}
    fields: dict[str, dict[str, Any]] = {}
    bounds: dict[str, dict[str, Any]] = {}
    validators: dict[str, list[str]] = {}
    deprecations: dict[str, dict[str, str]] = {}
    for index, node in enumerate(body):
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            following = body[index + 1] if index + 1 < len(body) else None
            doc = (
                following.value.value
                if isinstance(following, ast.Expr)
                and isinstance(following.value, ast.Constant)
                and isinstance(following.value.value, str)
                else None
            )
            name = node.target.id
            doc = doc or args_docs(cls.__doc__).get(name)
            fields[name] = {
                "annotation": ascii_text(ast.unparse(node.annotation)),
                "default": None if node.value is None else ascii_text(ast.unparse(node.value)),
                "doc": doc,
            }
            for call in ast.walk(node.annotation):
                if (
                    isinstance(call, ast.Call)
                    and isinstance(call.func, ast.Name)
                    and call.func.id == "AfterValidator"
                    and call.args
                    and isinstance(call.args[0], ast.Name)
                    and call.args[0].id in functions
                ):
                    found = deprecation_call(functions[call.args[0].id])
                    if found:
                        deprecations[name] = found
        elif (
            isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == "make_constraint_validator"
        ):
            owner_module = importlib.import_module(cls.__module__)
            for argument in node.value.args:
                bound = bounds.setdefault(str(ast.literal_eval(argument)), {})
                bound.update(
                    {
                        k.arg: getattr(owner_module, k.value.id)
                        if isinstance(k.value, ast.Name)
                        else ast.literal_eval(k.value)
                        for k in node.value.keywords
                        if k.arg
                    }
                )
        elif isinstance(node, ast.FunctionDef):
            for decorator in node.decorator_list:
                if (
                    isinstance(decorator, ast.Call)
                    and isinstance(decorator.func, ast.Name)
                    and decorator.func.id == "field_validator"
                ):
                    found = deprecation_call(node)
                    for argument in decorator.args:
                        target = str(ast.literal_eval(argument))
                        validators.setdefault(target, []).append(node.name)
                        if found:
                            deprecations[target] = found
    return {"fields": fields, "bounds": bounds, "validators": validators, "deprecations": deprecations}


def is_options_class(value: Any) -> bool:
    return (
        isinstance(value, type)
        and value.__module__.startswith(f"{PACKAGE}.options")
        and (hasattr(value, "model_fields") or hasattr(value, "__pydantic_fields__"))
    )


def field_infos(cls: type) -> dict[str, Any]:
    """Pydantic field infos in declaration order, inherited first; private names excluded."""
    infos = cls.model_fields if hasattr(cls, "model_fields") else cls.__pydantic_fields__  # type: ignore[attr-defined]
    return {name: info for name, info in infos.items() if not name.startswith("_")}


def walk_type(annotation: Any) -> Iterator[Any]:
    """Every node of a runtime annotation: unions, Annotated metadata and Literal arguments included."""
    yield annotation
    origin = get_origin(annotation)
    if origin is Literal:
        return
    for argument in get_args(annotation):
        yield from walk_type(argument)


def bound_items(metadata: Any) -> Iterator[tuple[str, Any]]:
    """ge, gt, le and lt of annotated-types constraints, also inside a pydantic FieldInfo."""
    for item in metadata:
        nested = getattr(item, "metadata", None)
        if isinstance(nested, list):
            yield from bound_items(nested)
        for key in ("ge", "gt", "le", "lt"):
            if type(item).__name__.lower() == key and hasattr(item, key):
                yield key, getattr(item, key)


def allowed(info: Any) -> tuple[list[Any], dict[str, Any], list[type]]:
    """Literal values, numeric bounds and nested options classes of one field."""
    literals: list[Any] = []
    bounds: dict[str, Any] = dict(bound_items(info.metadata))
    nested: list[type] = []
    for node in walk_type(info.annotation):
        if get_origin(node) is Literal:
            literals.extend(value for value in get_args(node) if value not in literals)
        elif is_options_class(node) and node not in nested:
            nested.append(node)
        if get_origin(node) is not None and str(get_origin(node)).endswith("Annotated"):
            bounds.update(bound_items(get_args(node)[1:]))
    return literals, bounds, nested


def qualified(cls: type) -> str:
    return f"{cls.__module__}.{cls.__qualname__}"


def declaring(cls: type, name: str) -> tuple[type, dict[str, Any]]:
    for base in cls.__mro__:
        if base.__module__.startswith(f"{PACKAGE}.") and name in class_source(base)["fields"]:
            return base, class_source(base)
    raise RuntimeError(f"{qualified(cls)}.{name}: no declaring class body in {PACKAGE}")


def class_record(cls: type) -> tuple[dict[str, Any], list[type]]:
    rows = []
    children: list[type] = []
    for name, info in field_infos(cls).items():
        owner, source = declaring(cls, name)
        field = source["fields"][name]
        literals, bounds, nested = allowed(info)
        bounds.update(class_source(owner)["bounds"].get(name, {}))
        for base in cls.__mro__:
            if base.__module__.startswith(f"{PACKAGE}."):
                bounds.update(class_source(base)["bounds"].get(name, {}))
        deprecated = None
        validators: list[str] = []
        for base in reversed(cls.__mro__):
            if base.__module__.startswith(f"{PACKAGE}."):
                deprecated = class_source(base)["deprecations"].get(name, deprecated)
                validators.extend(class_source(base)["validators"].get(name, []))
        children.extend(child for child in nested if child not in children)
        rows.append(
            {
                "name": name,
                "declared_in": qualified(owner),
                "annotation": field["annotation"],
                "default": field["default"],
                "documented_default": documented_default(field["doc"]),
                "literals": literals,
                "bounds": dict(sorted(bounds.items())),
                "nested": [qualified(child) for child in nested],
                "validators": validators,
                "deprecated": deprecated,
                "summary": doc_sentence(field["doc"]),
            }
        )
    family = "client" if cls.__module__.startswith(f"{PACKAGE}.options_models") else "server"
    return {"class": qualified(cls), "family": family, "summary": doc_sentence(cls.__doc__), "fields": rows}, children


def option_inventory() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    classes: dict[str, dict[str, Any]] = {}
    roots = []
    for label, module_name, class_name, primitive in ROOTS:
        root = getattr(module(module_name), class_name)
        paths: list[str] = []

        def visit(cls: type, prefix: str, paths: list[str] = paths) -> None:
            record, children = class_record(cls)
            classes.setdefault(record["class"], record)
            for row in record["fields"]:
                path = f"{prefix}{row['name']}"
                if row["nested"]:
                    for child in children:
                        if qualified(child) in row["nested"]:
                            visit(child, f"{path}.")
                else:
                    paths.append(path)

        visit(root, "")
        roots.append(
            {
                "label": label,
                "class": qualified(root),
                "accepted_by": f"{PACKAGE}.{primitive}",
                "leaf_paths": paths,
            }
        )
    return roots, sorted(classes.values(), key=lambda record: (record["family"], record["class"]))


def deprecation_sites() -> list[dict[str, str]]:
    sites = []
    for name in DEPRECATION_MODULES:
        tree = module_tree(f"{PACKAGE}.{name}")
        stack: list[tuple[ast.AST, str]] = [(tree, "")]
        while stack:
            node, scope = stack.pop()
            for child in ast.iter_child_nodes(node):
                if isinstance(child, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
                    stack.append((child, f"{scope}.{child.name}" if scope else child.name))
                elif not isinstance(child, ast.ClassDef | ast.FunctionDef):
                    for call in ast.walk(child):
                        found = deprecation_call(call) if isinstance(call, ast.Call) else None
                        if (
                            found
                            and isinstance(call, ast.Call)
                            and getattr(call.func, "id", "") == ("issue_deprecation_msg")
                        ):
                            sites.append({"module": f"{PACKAGE}.{name}", "site": scope, **found})
    unique = {json.dumps(site, sort_keys=True): site for site in sites}
    return sorted(unique.values(), key=lambda site: (site["module"], site["site"], site["msg"]))


def rest_inventory() -> dict[str, Any]:
    base = module_tree(f"{PACKAGE}.api.rest.base")
    header = next(
        ast.literal_eval(node.value)
        for node in ast.walk(base)
        if isinstance(node, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "_HEADER_API_VERSION" for t in node.targets)
    )
    adaptors = []
    for name in REST_MODULES:
        for node in module_tree(f"{PACKAGE}.api.rest.{name}").body:
            if not isinstance(node, ast.ClassDef):
                continue
            url_map = next(
                (
                    ast.literal_eval(statement.value)
                    for statement in node.body
                    if isinstance(statement, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == "URL_MAP" for t in statement.targets)
                ),
                None,
            )
            if url_map is None:
                continue
            prefixes = [
                ascii_text(ast.unparse(call.args[1]))
                for call in ast.walk(node)
                if isinstance(call, ast.Call)
                and isinstance(call.func, ast.Attribute)
                and call.func.attr == "__init__"
                and len(call.args) > 1
            ] or ['""']
            methods = []
            for function in node.body:
                if not isinstance(function, ast.FunctionDef) or function.name == "__init__":
                    continue
                keys: set[str] = set()
                verbs: set[str] = set()
                payload: list[list[str]] = []
                arguments = {argument.arg for argument in function.args.args + function.args.kwonlyargs}
                for item in ast.walk(function):
                    if isinstance(item, ast.Call) and isinstance(item.func, ast.Attribute):
                        if item.func.attr == "get_url" and item.args:
                            keys.add(str(ast.literal_eval(item.args[0])))
                        owner = item.func.value
                        if (
                            isinstance(owner, ast.Attribute)
                            and owner.attr == "session"
                            and item.func.attr in ("get", "post", "put", "patch", "delete")
                        ):
                            verbs.add(item.func.attr.upper())
                    if isinstance(item, ast.Assign) and isinstance(item.value, ast.Name):
                        for target in item.targets:
                            if (
                                isinstance(target, ast.Subscript)
                                and isinstance(target.value, ast.Name)
                                and target.value.id in ("payload", "params")
                                and isinstance(target.slice, ast.Constant)
                                and item.value.id in arguments
                            ):
                                payload.append([item.value.id, str(target.slice.value)])
                    if isinstance(item, ast.Assign) and isinstance(item.value, ast.Dict):
                        for key, value in zip(item.value.keys, item.value.values, strict=True):
                            if isinstance(key, ast.Constant) and isinstance(value, ast.Name) and value.id in arguments:
                                payload.append([value.id, str(key.value)])
                if keys and verbs:
                    methods.append(
                        {
                            "method": function.name,
                            "verbs": sorted(verbs),
                            "paths": sorted(url_map[key] for key in keys),
                            "payload": sorted(payload),
                        }
                    )
            adaptors.append(
                {
                    "adaptor": f"{PACKAGE}.api.rest.{name}.{node.name}",
                    "prefixes": prefixes,
                    "methods": methods,
                }
            )
    return {"api_version_header": header, "adaptors": adaptors}


def effective_defaults() -> dict[str, Any]:
    from qiskit_ibm_runtime.executor.calculate_twirling_shots import calculate_twirling_shots
    from qiskit_ibm_runtime.executor_estimator.finalize_options import finalize_estimator_options
    from qiskit_ibm_runtime.executor_sampler.finalize_options import finalize_sampler_options
    from qiskit_ibm_runtime.options_models import EstimatorOptions, SamplerOptions

    sampler = finalize_sampler_options(SamplerOptions())
    levels = []
    for level in (0, 1, 2):
        options = finalize_estimator_options(EstimatorOptions(resilience_level=level))
        levels.append(
            {
                "resilience_level": level,
                "twirling.enable_gates": options.twirling.enable_gates,
                "twirling.enable_measure": options.twirling.enable_measure,
                "resilience.measure_mitigation": options.resilience.measure_mitigation,
                "resilience.zne_mitigation": options.resilience.zne_mitigation,
                "resilience.pec_mitigation": options.resilience.pec_mitigation,
            }
        )
    splits = []
    for shots in TWIRL_SHOTS:
        for randomizations in ("auto", 32):
            count, per = calculate_twirling_shots(shots, randomizations, "auto")
            splits.append(
                {
                    "shots": shots,
                    "num_randomizations": randomizations,
                    "resolved_randomizations": count,
                    "shots_per_randomization": per,
                    "executed_shots": count * per,
                }
            )
    return {
        "sampler": {
            "twirling.enable_gates": sampler.twirling.enable_gates,
            "twirling.enable_measure": sampler.twirling.enable_measure,
        },
        "estimator_levels": levels,
        "twirling_split": splits,
    }


def outcome(action: Callable[[], Any]) -> dict[str, Any]:
    try:
        result = action()
    except Exception as error:
        own = type(error).__module__.startswith(PACKAGE)
        return {
            "accepted": False,
            "error": type(error).__name__,
            "message": ascii_text(str(error)) if own else None,
        }
    return {"accepted": True, **result}


def probes() -> list[dict[str, Any]]:
    """prepare() of the client-side Sampler and Estimator on FakeFez; nothing leaves the process."""
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import SparsePauliOp
    from qiskit.transpiler import generate_preset_pass_manager
    from qiskit_ibm_runtime.circuit import MidCircuitMeasure
    from qiskit_ibm_runtime.executor_estimator.prepare import prepare as estimator_prepare
    from qiskit_ibm_runtime.executor_sampler.prepare import prepare as sampler_prepare
    from qiskit_ibm_runtime.fake_provider import FakeFez
    from qiskit_ibm_runtime.options_models import EstimatorOptions, SamplerOptions

    backend = FakeFez()
    manager = generate_preset_pass_manager(optimization_level=1, backend=backend, seed_transpiler=1)

    static = QuantumCircuit(2)
    static.h(0)
    static.cx(0, 1)
    static.measure_all()
    feed_forward = QuantumCircuit(2, 2)
    feed_forward.h(0)
    feed_forward.measure(0, 0)
    with feed_forward.if_test((feed_forward.clbits[0], 1)):
        feed_forward.x(1)
    feed_forward.measure(1, 1)
    mid_measure = QuantumCircuit(2, 2)
    mid_measure.h(0)
    mid_measure.measure(0, 0)
    mid_measure.cx(0, 1)
    mid_measure.measure(1, 1)
    mid_measure_2 = QuantumCircuit(2, 2)
    mid_measure_2.h(0)
    mid_measure_2.append(MidCircuitMeasure(), [0], [0])
    mid_measure_2.cx(0, 1)
    mid_measure_2.measure(1, 1)
    reset = QuantumCircuit(2, 3)
    reset.h(0)
    reset.measure(0, 0)
    reset.reset(0)
    reset.cx(0, 1)
    reset.measure([0, 1], [1, 2])
    reused_bit = QuantumCircuit(2, 2)
    reused_bit.h(0)
    reused_bit.measure(0, 0)
    reused_bit.cx(0, 1)
    reused_bit.measure([0, 1], [0, 1])
    boxed = QuantumCircuit(2)
    with boxed.box():
        boxed.cx(0, 1)
    boxed.measure_all()
    circuits = {
        "static": manager.run(static),
        "if_else": manager.run(feed_forward),
        "mid-circuit measure": manager.run(mid_measure),
        "reset": manager.run(reset),
        "measure twice into one bit": manager.run(reused_bit),
    }
    # measure_2 is absent from FakeFez's Target, so the circuit stays logical.
    circuits["MidCircuitMeasure"] = mid_measure_2
    circuits["BoxOp"] = boxed
    twirl = {"enable_gates": True, "enable_measure": True}
    sampler_cases: list[tuple[str, list[Any], dict[str, Any]]] = [
        ("static, defaults", [circuits["static"]], {}),
        ("if_else, defaults", [circuits["if_else"]], {}),
        ("static, DD", [circuits["static"]], {"dynamical_decoupling": {"enable": True}}),
        ("if_else, DD", [circuits["if_else"]], {"dynamical_decoupling": {"enable": True}}),
        ("mid-circuit measure, DD", [circuits["mid-circuit measure"]], {"dynamical_decoupling": {"enable": True}}),
        ("reset, DD", [circuits["reset"]], {"dynamical_decoupling": {"enable": True}}),
        ("static, gate and measure twirling", [circuits["static"]], {"twirling": twirl}),
        ("if_else, gate twirling", [circuits["if_else"]], {"twirling": {"enable_gates": True}}),
        ("if_else, measure twirling", [circuits["if_else"]], {"twirling": {"enable_measure": True}}),
        ("mid-circuit measure, gate and measure twirling", [circuits["mid-circuit measure"]], {"twirling": twirl}),
        ("MidCircuitMeasure, gate and measure twirling", [circuits["MidCircuitMeasure"]], {"twirling": twirl}),
        ("reset, gate and measure twirling", [circuits["reset"]], {"twirling": twirl}),
        (
            "measure twice into one bit, gate and measure twirling",
            [circuits["measure twice into one bit"]],
            {"twirling": twirl},
        ),
        ("static, meas_type kerneled", [circuits["static"]], {"execution": {"meas_type": "kerneled"}}),
        (
            "static, meas_type kerneled, measure twirling",
            [circuits["static"]],
            {"execution": {"meas_type": "kerneled"}, "twirling": {"enable_measure": True}},
        ),
        ("BoxOp, twirling off", [circuits["BoxOp"]], {}),
        ("two PUBs, 1000 and 2000 shots", [(circuits["static"], None, 1000), (circuits["static"], None, 2000)], {}),
        (
            "static, 32 randomizations x 64 shots",
            [(circuits["static"], None, 2048)],
            {"twirling": {"enable_gates": True, "num_randomizations": 32, "shots_per_randomization": 64}},
        ),
    ]
    records = []
    for name, pubs, options in sampler_cases:

        def run_sampler(pubs: list[Any] = pubs, options: dict[str, Any] = options) -> dict[str, Any]:
            program, _ = sampler_prepare(pubs, SamplerOptions(**options), backend=backend)
            return {"program_shots": program.shots}

        records.append({"primitive": "client Sampler", "case": name, "options": options, **outcome(run_sampler)})
    observable = SparsePauliOp("ZZ").apply_layout(circuits["static"].layout)
    unmeasured = QuantumCircuit(2)
    unmeasured.h(0)
    unmeasured.cx(0, 1)
    isa = manager.run(unmeasured)
    estimator_cases: list[tuple[str, Any, dict[str, Any]]] = [
        ("level 0", isa, {"resilience_level": 0}),
        ("level 1", isa, {"resilience_level": 1}),
        ("level 2", isa, {"resilience_level": 2}),
        ("PEC without layer_noise_model", isa, {"resilience": {"pec_mitigation": True}}),
        (
            "ZNE with PEA without layer_noise_model",
            isa,
            {"resilience": {"zne_mitigation": True, "zne": {"amplifier": "pea"}}},
        ),
        ("ZNE with gate folding", isa, {"resilience": {"zne_mitigation": True}}),
        ("PEC and ZNE", isa, {"resilience": {"pec_mitigation": True, "zne_mitigation": True}}),
        ("DD", isa, {"dynamical_decoupling": {"enable": True}}),
    ]
    for name, circuit, options in estimator_cases:

        def run_estimator(circuit: Any = circuit, options: dict[str, Any] = options) -> dict[str, Any]:
            estimator_prepare([(circuit, observable)], EstimatorOptions(**options), backend=backend)
            return {}

        records.append({"primitive": "client Estimator", "case": name, "options": options, **outcome(run_estimator)})
    return records


def primitive_classes() -> list[dict[str, Any]]:
    import qiskit_ibm_runtime as runtime

    rows = []
    for name in ("Session", "Batch", "QiskitRuntimeService"):
        cls = getattr(runtime, name)
        rows.append({"name": f"{PACKAGE}.{name}", "signature": ascii_text(str(inspect.signature(cls.__init__)))})
    service = runtime.QiskitRuntimeService
    for method in ("backends", "backend", "usage", "least_busy"):
        rows.append(
            {
                "name": f"{PACKAGE}.QiskitRuntimeService.{method}",
                "signature": ascii_text(str(inspect.signature(getattr(service, method)))),
            }
        )
    for name, attribute in (("executor_sampler.Sampler", "run"), ("executor_estimator.Estimator", "run")):
        owner = getattr(module(name.split(".")[0]), name.split(".")[1])
        rows.append(
            {"name": f"{PACKAGE}.{name}.{attribute}", "signature": ascii_text(str(inspect.signature(owner.run)))}
        )
    return rows


def requirements() -> list[str]:
    """Runtime dependencies of the installed distribution, names and specifier order normalized.

    The wheel's metadata comes from whichever setuptools built it, which can
    order the specifiers of one requirement differently.
    """
    from importlib.metadata import requires

    rows = []
    for item in requires("qiskit-ibm-runtime") or []:
        if "extra ==" in item:
            continue
        match = re.fullmatch(r"([A-Za-z0-9_.\-]+)\s*(.*)", item.split(";")[0].strip())
        require(match is not None, f"unparsed requirement {item!r}")
        if match is None:
            raise AssertionError
        name = re.sub(r"[-_.]+", "-", match.group(1)).lower()
        specifiers = sorted(part.strip() for part in match.group(2).split(",") if part.strip())
        rows.append(f"{name} {','.join(specifiers)}".strip())
    return sorted(rows)


def probe_environment() -> dict[str, str | None]:
    """Installed versions of the distributions the probes exercise."""
    from importlib.metadata import PackageNotFoundError, version

    versions: dict[str, str | None] = {}
    for name in PROBE_PACKAGES:
        try:
            versions[name] = version(name)
        except PackageNotFoundError:
            versions[name] = None
    return versions


def environment_differences(recorded: Any, installed: dict[str, str | None]) -> list[str]:
    """Each probe distribution whose installed version differs from the one the inventory was generated with."""
    require(
        isinstance(recorded, dict) and set(recorded) == set(PROBE_PACKAGES),
        f"inventory probe_environment must name {', '.join(PROBE_PACKAGES)}",
    )
    return [
        f"{name} {installed[name]} is installed; the inventory was generated with {recorded[name]}"
        for name in PROBE_PACKAGES
        if recorded[name] != installed[name]
    ]


def check_environment(recorded: Any, installed: dict[str, str | None]) -> None:
    """The probe outcomes byte-compare only under the versions the inventory was generated with."""
    differing = environment_differences(recorded, installed)
    require(not differing, "; ".join(differing))


def allow_replay(differing: list[str], environment: Any) -> None:
    """A version mismatch replays the retained inventory unless GOROROBA_PINS_REQUIRED=1 demands the probes."""
    require(
        environment.get(PINS_REQUIRED) != "1",
        f"{'; '.join(differing)}; {PINS_REQUIRED}=1 requires the recorded versions",
    )


def inventory() -> dict[str, Any]:
    import qiskit_ibm_runtime

    require(
        qiskit_ibm_runtime.__version__ == RUNTIME_VERSION,
        f"qiskit-ibm-runtime {qiskit_ibm_runtime.__version__} is installed; the inventory pins {RUNTIME_VERSION}",
    )
    roots, classes = option_inventory()
    return {
        "schema": SCHEMA,
        "qiskit_ibm_runtime": RUNTIME_VERSION,
        "runtime_requirements": requirements(),
        "probe_environment": probe_environment(),
        "roots": roots,
        "classes": classes,
        "effective_defaults": effective_defaults(),
        "deprecations": deprecation_sites(),
        "rest": rest_inventory(),
        "entry_points": primitive_classes(),
        "probes": probes(),
    }


def cell(value: Any) -> str:
    text = value if isinstance(value, str) else json.dumps(value)
    return text.replace("|", "\\|").replace("\n", " ")


def code(value: str | None) -> str:
    if value is None or value == "":
        return ""
    return "`" + value.replace("`", "'").replace("|", "\\|") + "`"


def short_class(name: str) -> str:
    return name.removeprefix(f"{PACKAGE}.")


def render_options(data: dict[str, Any]) -> list[str]:
    lines = [
        f"Generated by `scripts/ibm_runtime_options_inventory.py --render` from the installed qiskit-ibm-runtime "
        f"{data['qiskit_ibm_runtime']}; `--check` (gate core-533) holds this block to the package.",
        "",
        "**Option roots.** Leaf fields count every nested path.",
        "",
        "| Root | Options class | Accepted by | Leaf fields |",
        "| --- | --- | --- | --- |",
    ]
    for root in data["roots"]:
        lines.append(
            f"| {root['label']} | {code(short_class(root['class']))} | {code(short_class(root['accepted_by']))} "
            f"| {len(root['leaf_paths'])} |"
        )
    labels = [root["label"] for root in data["roots"]]
    paths: list[str] = []
    for root in data["roots"]:
        paths.extend(path for path in root["leaf_paths"] if path not in paths)
    lines += [
        "",
        "**Leaf option paths by root** (x: the root accepts the path).",
        "",
        "| Path | " + " | ".join(labels) + " |",
        "| --- |" + " --- |" * len(labels),
    ]
    for path in sorted(paths):
        marks = ["x" if path in root["leaf_paths"] else "" for root in data["roots"]]
        lines.append(f"| {code(path)} | " + " | ".join(marks) + " |")
    for record in data["classes"]:
        lines += [
            "",
            f"**{record['family']} {code(short_class(record['class']))}**: {cell(record['summary'])}",
            "",
            "| Field | Type (source) | Default (source) | Documented default | Allowed values or bounds "
            "| Deprecated | Summary |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
        for row in record["fields"]:
            allowed_text = ", ".join(json.dumps(value) for value in row["literals"])
            bounds = ", ".join(f"{key} {value}" for key, value in row["bounds"].items())
            if row["nested"]:
                allowed_text = "nested " + ", ".join(short_class(name) for name in row["nested"])
            extra = "; ".join(part for part in (allowed_text, bounds) if part)
            if row["validators"]:
                extra = "; ".join(part for part in (extra, "validator " + ", ".join(row["validators"])) if part)
            deprecated = row["deprecated"]
            deprecated_text = f"{deprecated['version']}: {deprecated['msg']}" if deprecated else ""
            lines.append(
                f"| {code(row['name'])} | {code(row['annotation'])} | {code(row['default'])} "
                f"| {cell(row['documented_default'] or '')} | {cell(extra)} | {cell(deprecated_text)} "
                f"| {cell(row['summary'])} |"
            )
    return lines


def render_behavior(data: dict[str, Any]) -> list[str]:
    effective = data["effective_defaults"]
    lines = [
        "Generated by `scripts/ibm_runtime_options_inventory.py --render`; probes call `prepare()` of the "
        "client-side primitives on FakeFez and submit nothing.",
        "",
        "**Client-side Sampler, resolved twirling defaults** (`finalize_sampler_options`): "
        + ", ".join(f"`{key}` = {json.dumps(value)}" for key, value in sorted(effective["sampler"].items()))
        + ".",
        "",
        "**Client-side Estimator, resolved defaults by resilience level** (`finalize_estimator_options`).",
        "",
    ]
    # Columns follow key order, so the block renders alike from a fresh probe and from the
    # retained file, whose keys dumps() sorts.
    keys = sorted(key for key in effective["estimator_levels"][0] if key != "resilience_level")
    lines += ["| resilience_level | " + " | ".join(f"`{key}`" for key in keys) + " |"]
    lines += ["| --- |" + " --- |" * len(keys)]
    for level in effective["estimator_levels"]:
        lines.append(f"| {level['resilience_level']} | " + " | ".join(json.dumps(level[key]) for key in keys) + " |")
    lines += [
        "",
        '**Twirling shot split** (`calculate_twirling_shots` with `shots_per_randomization` "auto").',
        "",
        "| PUB shots | num_randomizations | resolved randomizations | shots per randomization | executed shots |",
        "| --- | --- | --- | --- | --- |",
    ]
    for split in effective["twirling_split"]:
        lines.append(
            f"| {split['shots']} | {json.dumps(split['num_randomizations'])} | {split['resolved_randomizations']} "
            f"| {split['shots_per_randomization']} | {split['executed_shots']} |"
        )
    lines += [
        "",
        "**Deprecation sites** (`issue_deprecation_msg` calls).",
        "",
        "| Module | Site | Since | Message |",
        "| --- | --- | --- | --- |",
    ]
    for site in data["deprecations"]:
        lines.append(
            f"| {code(short_class(site['module']))} | {code(site['site'])} | {site['version']} | {cell(site['msg'])} |"
        )
    lines += [
        "",
        "**Offline prepare() probes.** A rejection names its exception; the message is kept when "
        "qiskit-ibm-runtime raises it.",
        "",
        "| Primitive | Case | Options | Accepted | Program shots | Error |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for probe in data["probes"]:
        error = ""
        if not probe["accepted"]:
            error = probe["error"] + (f": {probe['message']}" if probe["message"] else "")
        lines.append(
            f"| {probe['primitive']} | {cell(probe['case'])} | {code(json.dumps(probe['options'], sort_keys=True))} "
            f"| {'yes' if probe['accepted'] else 'no'} | {probe.get('program_shots', '')} | {cell(error)} |"
        )
    return lines


def render_rest(data: dict[str, Any]) -> list[str]:
    rest = data["rest"]
    lines = [
        "Generated by `scripts/ibm_runtime_options_inventory.py --render` from the installed REST adaptors; "
        f"every request carries `IBM-API-Version: {rest['api_version_header']['IBM-API-Version']}`.",
        "",
        "| Adaptor | Path prefix | Method | Verb | Path suffix | Argument -> payload or query key |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for adaptor in rest["adaptors"]:
        prefix = " or ".join(code(prefix) for prefix in adaptor["prefixes"])
        for method in adaptor["methods"]:
            payload = ", ".join(f"{argument} -> {key}" for argument, key in method["payload"])
            lines.append(
                f"| {code(short_class(adaptor['adaptor']))} | {prefix} | {code(method['method'])} "
                f"| {', '.join(method['verbs'])} | {', '.join(code(path) or '(prefix)' for path in method['paths'])} "
                f"| {cell(payload)} |"
            )
    lines += ["", "**Entry points** (installed signatures).", "", "| Name | Signature |", "| --- | --- |"]
    for row in data["entry_points"]:
        lines.append(f"| {code(short_class(row['name']))} | {code(row['signature'])} |")
    return lines


def ns(value: Any) -> str:
    return "None" if value is None else f"{value:g} ns"


def timing(row: dict[str, Any], error: bool = True) -> str:
    """Median duration, with the median error when the Target carries one."""
    text = ns(row["duration_ns_median"])
    if error and row["error_median"] is not None:
        text += f" / {row['error_median']:.5f}"
    return text


def render_backends(record: dict[str, Any]) -> list[str]:
    """The section 4 table: one column per captured backend, every cell read from the snapshot."""
    names = sorted(record["backends"])
    entries = [record["backends"][name] for name in names]
    versions = record["versions"]

    def row(label: str, cells: Callable[[dict[str, Any]], str], source: str) -> str:
        return f"| {label} | " + " | ".join(cells(entry) for entry in entries) + f" | {source} |"

    def conf(key: str) -> Callable[[dict[str, Any]], str]:
        return lambda entry: cell(entry["configuration"][key])

    def listed(key: str) -> Callable[[dict[str, Any]], str]:
        return lambda entry: ", ".join(entry["configuration"][key])

    def instruction(name: str, error: bool = True) -> Callable[[dict[str, Any]], str]:
        return lambda entry: timing(entry["instructions"][name], error)

    def fractional(name: str) -> Callable[[dict[str, Any]], str]:
        return lambda entry: timing(entry["fractional_instructions"][name])

    def processor(entry: dict[str, Any]) -> str:
        kind = entry["configuration"]["processor_type"]
        return f"{kind['family']} r{kind['revision']}, {entry['configuration']['backend_version']}"

    def durations(entry: dict[str, Any]) -> str:
        table = entry["instructions"]
        return ", ".join(f"{name} {ns(table[name]['duration_ns_median'])}" for name in ("x", "sx", "id", "xslow"))

    def cz(entry: dict[str, Any]) -> str:
        row_ = entry["instructions"]["cz"]
        return f"{row_['duration_ns_median']:g} ({row_['duration_ns_max']:g}) ns / {row_['error_median']:.5f}"

    def constraints(entry: dict[str, Any]) -> str:
        return ", ".join(
            f"{key} {value}" for key, value in sorted(entry["configuration"]["timing_constraints"].items())
        )

    def rep_delay(entry: dict[str, Any]) -> str:
        c = entry["configuration"]
        low, high = c["rep_delay_range"]
        wire = entry["wire_units"]
        w_low, w_high = wire["rep_delay_range"]
        default = c["default_rep_delay"]
        return f"[{low:g}, {high:g}], {default:g} (wire {w_low:g} to {w_high:g}, {wire['default_rep_delay']:g})"

    def meas_map(entry: dict[str, Any]) -> str:
        return f"{entry['meas_map']['groups']} group(s), largest {entry['meas_map']['largest_group']}"

    def bounds(gate: str) -> Callable[[dict[str, Any]], str]:
        def text(entry: dict[str, Any]) -> str:
            info = entry["fractional_angle_bounds"][gate]
            if not info["has_angle_bounds"]:
                return "none"
            ok = [angle for angle, flag in info["supported"].items() if flag]
            bad = [angle for angle, flag in info["supported"].items() if not flag]
            admitted = ", ".join(f"{float(a):.4g}" for a in ok)
            refused = ", ".join(f"{float(a):.4g}" for a in bad)
            return f"admitted {admitted}; refused {refused}"

        return text

    def status(entry: dict[str, Any]) -> str:
        return f"{entry['status']['status_msg']}, {entry['status']['pending_jobs']} pending"

    lines = [
        "Generated by `scripts/ibm_runtime_options_inventory.py --render` from "
        f"`docs/evidence/ibm_runtime_options/backends.json`, read {record['retrieved']} under "
        f"qiskit {versions['qiskit']} and qiskit-ibm-runtime {versions['qiskit-ibm-runtime']}.",
        "",
        "| Control | " + " | ".join(names) + " | Source |",
        "| --- | " + " | ".join("---" for _ in names) + " | --- |",
        row("processor_type, backend_version", processor, "[M] `configuration()`"),
        row("qubits", conf("n_qubits"), "[M]; [P] processor-types.md for the heavy-hex coupling"),
        row("basis_gates", listed("basis_gates"), "[M]"),
        row("supported_instructions", listed("supported_instructions"), "[M]"),
        row("supported_features", listed("supported_features"), "[M]"),
        row(
            "`conditional` (legacy flag)",
            conf("conditional"),
            "[M]; `if_else` support comes from `supported_instructions` and `dynamic_circuits`, "
            "and every backend listed in `dynamic_circuit_backends` accepts it",
        ),
        row("measure duration / median error", instruction("measure"), "[M] Target"),
        row("measure_2 duration / median error", instruction("measure_2"), "[M] Target"),
        row("reset duration", instruction("reset", False), "[M] Target"),
        row("measure_reset duration", instruction("measure_reset", False), "[M] Target"),
        row("reset_2 duration", instruction("reset_2", False), "[M] Target"),
        row("measure_reset_2 duration", instruction("measure_reset_2", False), "[M] Target"),
        row("x, sx, id, xslow duration", durations, "[M] Target"),
        row("cz duration median (max) / median error", cz, "[M] Target"),
        row("dt, dtm (s)", lambda e: f"{e['configuration']['dt']:g}, {e['configuration']['dtm']:g}", "[M]"),
        row("timing_constraints", constraints, "[M]"),
        row("rep_delay_range, default_rep_delay (SDK seconds)", rep_delay, "[M]; `to_dict()` reports microseconds"),
        row("dynamic_reprate_enabled", conf("dynamic_reprate_enabled"), "[M]"),
        row("max_shots", conf("max_shots"), "[M]"),
        row(
            "max_experiments; `backend.max_circuits`",
            lambda e: f"{e['configuration']['max_experiments']}; {cell(e['max_circuits'])}",
            "[M]; [S] `IBMBackend.max_circuits` returns None because `max_experiments` "
            '"is no longer an accurate representation of backend circuit limits"',
        ),
        row("meas_map", meas_map, "[M]"),
        row(
            "meas_levels, meas_kernels, discriminators",
            lambda e: ", ".join(cell(e["configuration"][k]) for k in ("meas_levels", "meas_kernels", "discriminators")),
            "[M]",
        ),
        row(
            "multi_meas_enabled, measure_esp_enabled",
            lambda e: ", ".join(cell(e["configuration"][k]) for k in ("multi_meas_enabled", "measure_esp_enabled")),
            "[M]",
        ),
        row(
            "mcps, clops_h",
            lambda e: f"{e['configuration']['mcps']}, {e['configuration']['clops_h']}",
            "[M]",
        ),
        row("fractional `rzz` duration / median error", fractional("rzz"), "[M] fractional Target"),
        row("fractional `rx` median error", fractional("rx"), '[M]; [P] qpu-information.md "RX error"'),
        row("`rzz` angle bounds in the Target", bounds("rzz"), "[M] `supported_angle_bound`"),
        row("`rx` angle bounds", bounds("rx"), '[M] `gate_has_angle_bounds`; [P] "any theta"'),
        row("status at read", status, "[M] `status()`"),
    ]
    return lines


def render_usage(record: dict[str, Any]) -> list[str]:
    """The section 6 quota rows: every figure read from the snapshot's usage block."""
    usage = record["usage"]
    period = usage["usage_period"]

    def stamp(value: str) -> str:
        return re.sub(r"\.\d+Z$", "Z", value)

    return [
        "Generated by `scripts/ibm_runtime_options_inventory.py --render` from the `usage` block of "
        "`docs/evidence/ibm_runtime_options/backends.json`",
        "",
        "| Item | Value | Source |",
        "| --- | --- | --- |",
        f"| Plan window | {usage['usage_limit_seconds']} s on a rolling 28-day window; `usage()` returned a period "
        f"ending at the call ({stamp(period['start_time'])} to {stamp(period['end_time'])}), "
        f"{usage['usage_consumed_seconds']} s consumed, {usage['usage_remaining_seconds']} s remaining, "
        f"`usage_limit_reached` {str(usage['usage_limit_reached']).lower()} | "
        '[M] read B; AGENTS.md "QPU time and calibration" |',
        f"| Resource units | `usage()` also reports `usage_limit_ru` {usage['usage_limit_ru']} and "
        f"`usage_consumed_ru` {usage['usage_consumed_ru']}; job metrics carry `resource_units` | "
        "[M]; their conversion to seconds is **unverified** |",
    ]


def render(data: dict[str, Any], backends: dict[str, Any] | None = None) -> dict[str, str]:
    snapshot = backends if backends is not None else json.loads(BACKENDS.read_text())
    blocks = {
        "rest": render_rest(data),
        "options": render_options(data),
        "behavior": render_behavior(data),
        "backends": render_backends(snapshot),
        "usage": render_usage(snapshot),
    }
    return {name: "\n".join(lines) for name, lines in blocks.items()}


def marker(name: str, edge: str) -> str:
    return f"<!-- ibm-runtime-options:{name}:{edge} -->"


def note_blocks(text: str) -> dict[str, str]:
    blocks = {}
    for name in BLOCKS:
        begin, end = marker(name, "begin"), marker(name, "end")
        require(text.count(begin) == 1 and text.count(end) == 1, f"note needs one {begin} and one {end}")
        blocks[name] = text.split(begin, 1)[1].split(end, 1)[0].strip("\n")
    return blocks


def dumps(data: Any) -> str:
    return json.dumps(data, indent=1, sort_keys=True, ensure_ascii=True) + "\n"


def utc_now() -> str:
    return datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")


def sha12(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:12]


CONFIG_KEYS = (
    "backend_version",
    "processor_type",
    "n_qubits",
    "basis_gates",
    "supported_instructions",
    "supported_features",
    "conditional",
    "max_shots",
    "max_experiments",
    "dynamic_reprate_enabled",
    "rep_delay_range",
    "default_rep_delay",
    "dt",
    "dtm",
    "timing_constraints",
    "meas_levels",
    "meas_kernels",
    "discriminators",
    "multi_meas_enabled",
    "measure_esp_enabled",
    "memory",
    "n_registers",
    "mcps",
    "clops_h",
    "credits_required",
    "open_pulse",
    "simulator",
    "online_date",
)
INSTRUCTIONS = (
    "measure",
    "measure_2",
    "measure_reset",
    "measure_reset_2",
    "reset",
    "reset_2",
    "x",
    "sx",
    "xslow",
    "id",
    "rz",
    "cz",
    "delay",
    "if_else",
    "store",
    "for_loop",
    "switch_case",
    "while_loop",
)
FRACTIONAL = ("rzz", "rx")
USAGE_KEYS = (
    "usage_period",
    "usage_limit_seconds",
    "usage_consumed_seconds",
    "usage_remaining_seconds",
    "usage_limit_reached",
    "usage_limit_ru",
    "usage_consumed_ru",
)
ANGLES = (-0.3, 0.3, math.pi / 2, 2.0)
SECRET_KEYS = {"token", "instance", "instance_id", "plan_id", "crn", "url", "description", "account"}


def plain(value: Any) -> Any:
    if isinstance(value, datetime.datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): plain(item) for key, item in value.items()}
    if isinstance(value, list | tuple):
        return [plain(item) for item in value]
    if value is None or isinstance(value, bool | int | float | str):
        return value
    return str(value)


def instruction_table(target: Any, names: tuple[str, ...]) -> dict[str, Any]:
    rows: dict[str, Any] = {}
    for name in names:
        if name not in target.operation_names:
            rows[name] = {"present": False}
            continue
        properties = [p for p in (target[name] or {}).values() if p is not None]
        durations = [round(p.duration * 1e9, 3) for p in properties if p.duration is not None]
        errors = [p.error for p in properties if p.error is not None]
        rows[name] = {
            "present": True,
            "qargs_with_properties": len(properties),
            "duration_ns_median": statistics.median(durations) if durations else None,
            "duration_ns_min": min(durations) if durations else None,
            "duration_ns_max": max(durations) if durations else None,
            "error_median": statistics.median(errors) if errors else None,
        }
    return rows


def rzz_transpile_probe(backend: Any) -> dict[str, Any]:
    """Local transpilation of rzz(2.0) and rzz(0.3) against the fractional Target; nothing is sent."""
    from qiskit import QuantumCircuit
    from qiskit.transpiler import generate_preset_pass_manager

    circuit = QuantumCircuit(2)
    circuit.rzz(2.0, 0, 1)
    circuit.rzz(0.3, 0, 1)
    circuit.measure_all()
    results = {}
    for method in (None, "ibm_dynamic_and_fractional"):
        manager = generate_preset_pass_manager(
            optimization_level=1, backend=backend, translation_method=method, seed_transpiler=7
        )
        isa = manager.run(circuit)
        angles = sorted(
            round(float(instruction.operation.params[0]), 6)
            for instruction in isa.data
            if instruction.operation.name == "rzz"
        )
        results[method or "default (backend plugin)"] = {
            "operation_counts": dict(sorted(isa.count_ops().items())),
            "rzz_angles": angles,
            "all_rzz_in_bounds": all(0 < angle <= math.pi / 2 + 1e-9 for angle in angles),
        }
    return {"translation_plugin": backend.get_translation_stage_plugin(), "results": results}


def read_backends(out: Path) -> None:
    import qiskit
    import qiskit_ibm_runtime
    from qiskit_ibm_runtime import QiskitRuntimeService

    require_runtime_version(qiskit_ibm_runtime.__version__)
    require_qiskit_version(qiskit.__version__)
    reads: list[dict[str, str]] = []

    def stamp(call: str) -> None:
        reads.append({"call": call, "time": utc_now()})

    service = QiskitRuntimeService()
    stamp("QiskitRuntimeService() from the saved account")
    instance = str(service.active_instance() or "")
    require(bool(instance), "the saved account resolves no instance")
    names = sorted(backend.name for backend in service.backends())
    stamp("service.backends()")
    dynamic = sorted(backend.name for backend in service.backends(dynamic_circuits=True))
    stamp("service.backends(dynamic_circuits=True)")
    fractional = sorted(backend.name for backend in service.backends(use_fractional_gates=True))
    stamp("service.backends(use_fractional_gates=True)")
    usage = service.usage()
    stamp("service.usage()")
    budget = {key: plain(usage.get(key)) for key in USAGE_KEYS}
    budget["instance_sha256_12"] = sha12(instance)
    budget["usage_instance_is_active_instance"] = usage.get("instance_id") == instance
    backends: dict[str, Any] = {}
    for name in names:
        backend = service.backend(name)
        stamp(f"service.backend({name!r})")
        configuration = backend.configuration()
        stamp(f"{name}.configuration()")
        wire = configuration.to_dict()
        status = backend.status()
        stamp(f"{name}.status()")
        properties = backend.properties()
        stamp(f"{name}.properties()")
        target = backend.target
        stamp(f"{name}.target")
        fractional_backend = service.backend(name, use_fractional_gates=True)
        stamp(f"service.backend({name!r}, use_fractional_gates=True)")
        fractional_target = fractional_backend.target
        stamp(f"{name}.target with fractional gates")
        bounds = {}
        for gate in FRACTIONAL:
            present = gate in fractional_target.operation_names
            bounded = bool(present and fractional_target.gate_has_angle_bounds(gate))
            bounds[gate] = {
                "present": present,
                "has_angle_bounds": bounded,
                "supported": {
                    str(angle): bool(fractional_target.supported_angle_bound(gate, [angle])) if bounded else None
                    for angle in ANGLES
                },
            }
        meas_map = backend.meas_map
        backends[name] = {
            "configuration": {key: plain(getattr(configuration, key, None)) for key in CONFIG_KEYS},
            "wire_units": {
                "default_rep_delay": plain(wire.get("default_rep_delay")),
                "rep_delay_range": plain(wire.get("rep_delay_range")),
            },
            "max_circuits": plain(backend.max_circuits),
            "meas_map": {"groups": len(meas_map), "largest_group": max(len(group) for group in meas_map)},
            "status": {
                "status_msg": status.status_msg,
                "operational": status.operational,
                "pending_jobs": status.pending_jobs,
                "backend_version": status.backend_version,
            },
            "properties_last_update": plain(properties.last_update_date) if properties else None,
            "instructions": instruction_table(target, INSTRUCTIONS),
            "fractional_instructions": instruction_table(fractional_target, FRACTIONAL),
            "fractional_angle_bounds": bounds,
            "rzz_transpile_probe": rzz_transpile_probe(fractional_backend),
        }
        stamp(f"{name}: local rzz transpile probe finished")
    record = {
        "schema": BACKENDS_SCHEMA,
        "retrieved": reads[0]["time"],
        "versions": {"qiskit": qiskit.__version__, "qiskit-ibm-runtime": qiskit_ibm_runtime.__version__},
        "accessible_backends": names,
        "dynamic_circuit_backends": dynamic,
        "fractional_backends": fractional,
        "usage": budget,
        "backends": backends,
        "reads": reads,
    }
    check_backends(record)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(dumps(record))


def scan_secrets(value: Any, path: str = "") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            require(key not in SECRET_KEYS, f"backends snapshot carries key {path}/{key}")
            scan_secrets(item, f"{path}/{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            scan_secrets(item, f"{path}/{index}")
    elif isinstance(value, str):
        require("crn:" not in value, f"backends snapshot carries a CRN at {path}")
        require(
            re.search(r"[A-Za-z0-9_\-]{40,}", value) is None, f"backends snapshot carries a token-like string at {path}"
        )


def is_time(value: Any) -> bool:
    try:
        datetime.datetime.fromisoformat(value)
    except TypeError, ValueError:
        return False
    return True


def pinned_version(name: str) -> str:
    """The version requirements.txt pins for a distribution."""
    for line in REQUIREMENTS.read_text().splitlines():
        match = re.fullmatch(rf"{re.escape(name)}==(\S+)", line.strip())
        if match:
            return match.group(1)
    raise RuntimeError(f"requirements.txt pins no {name}")


def require_qiskit_version(found: Any) -> None:
    pin = pinned_version("qiskit")
    require(found == pin, f"qiskit {found} is recorded or installed; requirements.txt pins {pin}")


def require_runtime_version(found: Any) -> None:
    require(
        found == RUNTIME_VERSION,
        f"qiskit-ibm-runtime {found} is recorded or installed; the inventory pins {RUNTIME_VERSION}",
    )


def check_backends(record: dict[str, Any]) -> None:
    """Schema of a backend snapshot: keys, types and hygiene, never the live values."""
    require(record.get("schema") == BACKENDS_SCHEMA, "backends snapshot schema")
    require(is_time(record.get("retrieved")), "backends snapshot retrieval time")
    for key in ("accessible_backends", "dynamic_circuit_backends", "fractional_backends"):
        require(isinstance(record.get(key), list) and all(isinstance(n, str) for n in record[key]), key)
    versions: Any = record.get("versions")
    require(isinstance(versions, dict), "backends snapshot versions")
    require_runtime_version(versions.get("qiskit-ibm-runtime"))
    # Runtime 0.50 declares qiskit>=2.3.0,<3; a retained read keeps its producer
    # version when requirements.txt advances the interpreter used for new reads.
    producer = versions.get("qiskit")
    release = re.fullmatch(r"2\.(\d+)\.(\d+)", producer) if isinstance(producer, str) else None
    require(
        release is not None and int(release.group(1)) >= 3,
        f"backends snapshot qiskit producer {producer!r} must be a stable release >=2.3.0,<3",
    )
    require(
        sorted(record["backends"]) == sorted(record["accessible_backends"]),
        "backends snapshot captures a backend set that differs from accessible_backends",
    )
    for key in ("dynamic_circuit_backends", "fractional_backends"):
        require(
            set(record[key]) <= set(record["accessible_backends"]), f"{key} names a backend outside accessible_backends"
        )
    require(isinstance(record.get("usage"), dict), "usage block")
    usage: dict[str, Any] = record["usage"]
    require(re.fullmatch(r"[0-9a-f]{12}", str(usage.get("instance_sha256_12"))) is not None, "instance hash")
    require(set(usage) == set(USAGE_KEYS) | {"instance_sha256_12", "usage_instance_is_active_instance"}, "usage keys")
    require(
        usage["usage_instance_is_active_instance"] is True,
        "usage() reports an instance other than the active instance; the quota figures belong to another account",
    )
    require(isinstance(record.get("reads"), list) and bool(record["reads"]), "reads")
    reads: list[dict[str, Any]] = record["reads"]
    require(all(set(read) == {"call", "time"} and is_time(read["time"]) for read in reads), "read stamps")
    for name, entry in record["backends"].items():
        require(set(entry["configuration"]) == set(CONFIG_KEYS), f"{name}: configuration keys")
        configuration = entry["configuration"]
        require(isinstance(configuration["basis_gates"], list), f"{name}: basis_gates")
        require(isinstance(configuration["supported_instructions"], list), f"{name}: supported_instructions")
        require(isinstance(configuration["max_shots"], int), f"{name}: max_shots")
        require(isinstance(configuration["default_rep_delay"], float), f"{name}: default_rep_delay seconds")
        require(
            isinstance(configuration["rep_delay_range"], list) and len(configuration["rep_delay_range"]) == 2,
            f"{name}: rep_delay_range",
        )
        require(set(entry["instructions"]) == set(INSTRUCTIONS), f"{name}: instruction table")
        require(set(entry["fractional_instructions"]) == set(FRACTIONAL), f"{name}: fractional table")
        require(set(entry["fractional_angle_bounds"]) == set(FRACTIONAL), f"{name}: angle bounds")
        require({"status_msg", "operational", "pending_jobs", "backend_version"} == set(entry["status"]), name)
        require(isinstance(entry["rzz_transpile_probe"].get("results"), dict), f"{name}: rzz probe")
    scan_secrets(record)


def check_note(text: str, rendered: dict[str, str]) -> None:
    blocks = note_blocks(text)
    for name, block in rendered.items():
        require(blocks[name] == block, f"{NOTE.name}: block {name} differs from --render")


def check(path: Path) -> None:
    """Regenerate the inventory under its recorded versions, or replay what needs no installed package.

    Under other versions of the probe distributions the probes cannot
    byte-compare, so the check holds the retained file to its canonical
    serialization, the backend snapshot to its schema and the note blocks to
    the retained inventory's rendering, and names the differing versions.
    """
    recorded = json.loads(path.read_text())
    differing = environment_differences(recorded.get("probe_environment"), probe_environment())
    if differing:
        allow_replay(differing, os.environ)
        require(path.read_text() == dumps(recorded), f"{path} is not in its canonical serialization")
        snapshot = json.loads(BACKENDS.read_text())
        check_backends(snapshot)
        check_note(NOTE.read_text(), render(recorded, snapshot))
        print(f"replayed {path.name} without regenerating its probes: {'; '.join(differing)}")
        return
    data = inventory()
    require(path.read_text() == dumps(data), f"{path} differs from the installed package; rerun --out")
    snapshot = json.loads(BACKENDS.read_text())
    check_backends(snapshot)
    check_note(NOTE.read_text(), render(data, snapshot))
    counts = {record["class"]: len(record["fields"]) for record in data["classes"]}
    print(
        f"inventory matches qiskit-ibm-runtime {RUNTIME_VERSION}: {len(counts)} classes, "
        f"{sum(counts.values())} fields, {len(data['probes'])} probes; note blocks and backend schema hold"
    )


def rejects(action: Callable[[], Any], fragment: str) -> None:
    try:
        action()
    except RuntimeError as error:
        require(fragment in str(error), f"rejected with {error!r}, expected {fragment!r}")
        return
    raise RuntimeError(f"accepted a corrupted record; expected a rejection naming {fragment!r}")


def self_test() -> None:
    snapshot = json.loads(BACKENDS.read_text())
    check_backends(snapshot)

    extra = copy.deepcopy(snapshot)
    extra["accessible_backends"].append("ibm_extra")
    rejects(lambda: check_backends(extra), "accessible_backends")
    missing = copy.deepcopy(snapshot)
    del missing["backends"][sorted(missing["backends"])[0]]
    rejects(lambda: check_backends(missing), "accessible_backends")

    older = copy.deepcopy(snapshot)
    older["versions"]["qiskit-ibm-runtime"] = "0.49.0"
    rejects(lambda: check_backends(older), "pins")
    rejects(lambda: require_runtime_version("0.49.0"), "pins")

    foreign = copy.deepcopy(snapshot)
    foreign["usage"]["usage_instance_is_active_instance"] = False
    rejects(lambda: check_backends(foreign), "active instance")
    for producer in ("2.3.0", "2.5.1", "2.6.0"):
        historical = copy.deepcopy(snapshot)
        historical["versions"]["qiskit"] = producer
        check_backends(historical)
    for invalid_producer in ("2.2.9", "3.0.0", "2.6.0rc1", "invalid", None, 2):
        incompatible = copy.deepcopy(snapshot)
        incompatible["versions"]["qiskit"] = invalid_producer
        rejects(partial(check_backends, incompatible), "qiskit producer")
    rejects(lambda: require_qiskit_version("2.5.1"), "requirements.txt pins")

    installed = probe_environment()
    check_environment(dict(installed), installed)
    for name in PROBE_PACKAGES:
        drifted = dict(installed)
        drifted[name] = "0.0.0"
        rejects(partial(check_environment, drifted, installed), name)
    rejects(lambda: check_environment({}, installed), "probe_environment")
    allow_replay(["qiskit 0.0.0 is installed"], {})
    rejects(lambda: allow_replay(["qiskit 0.0.0 is installed"], {PINS_REQUIRED: "1"}), PINS_REQUIRED)

    changed = copy.deepcopy(snapshot)
    first = sorted(changed["backends"])[0]
    changed["backends"][first]["configuration"]["max_shots"] += 1
    text = NOTE.read_text()
    rendered = {"backends": "\n".join(render_backends(snapshot))}
    check_note(text, rendered)
    rejects(lambda: check_note(text, {"backends": "\n".join(render_backends(changed))}), "backends")
    spent = copy.deepcopy(snapshot)
    spent["usage"]["usage_consumed_seconds"] += 1
    rendered_usage = {"usage": "\n".join(render_usage(snapshot))}
    check_note(text, rendered_usage)
    rejects(lambda: check_note(text, {"usage": "\n".join(render_usage(spent))}), "usage")
    print(
        "self-test: backend set, runtime and incompatible producer versions, probe environment, usage instance "
        "and note drift each rejected"
    )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--out", type=Path)
    group.add_argument("--check", type=Path)
    group.add_argument("--render", action="store_true")
    group.add_argument("--backends", type=Path)
    group.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(dumps(inventory()))
    elif args.check:
        check(args.check)
    elif args.self_test:
        self_test()
    elif args.render:
        for name, text in render(inventory()).items():
            print(f"{marker(name, 'begin')}\n{text}\n{marker(name, 'end')}\n")
    else:
        read_backends(args.backends)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
