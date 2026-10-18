"""Direct phase control of the Belenos interferometer: architecture decode, block placement, error models, RCA.

qpu:belenos is one fixed 24-mode mesh: the processor record's
specs.architecture lists 552 Rx beam splitters at calibrated angles and 574
symbolic phase shifters phi0..phi573, grouped as 276 MZIs (BS(m), PS on m+1
and m, BS(m)) plus 22 edge phases on modes 0 and 23. Every computed_circuit
the service returns carries that topology and those angles with numeric
phases, so a job is fully described by 574 numbers and the transpiler's only
freedom is how it chooses them.

- Decode. The protobuf messages (exqalibur circuit.proto: Experiment.components
  = 9, Circuit.components = 4, Component.circuit/phase_shifter/beam_splitter/
  barrier = 10/11/12/22, Parameter.real_value/symbol = 1/2) are read by a
  standard-library wire decoder, so CI decodes architectures and compiled
  meshes without exqalibur and no service string reaches Perceval's
  deserializer.
- Placement. A one-photon block U on modes lo..lo+3 occupies the first six
  MZIs inside those modes in column order (a rectangular 4-mode mesh); a
  least-squares fit sets their twelve phases so the mesh block equals
  D_out U D_in, with free diagonal frames that no Fock-input detection sees.
  Every other MZI either sits in bar (Delta = b - a minimizing the
  off-diagonal of its calibrated BS-PS-PS-BS product), the hot baseline, or
  only those touching lo-2..lo+5 sit in bar and the rest keep phase 0, the
  cold baseline that idles most heaters.
- Error models. Heater phase noise sigma, coupler angle noise, heater gain
  (delta = g phi), nearest-neighbour thermal crosstalk (delta_j = k sum of
  the phases of heaters on adjacent modes in adjacent ASAP columns) and a
  phase ceiling. The compiled and direct meshes respond oppositely to noise
  and to power-proportional errors, so one job holding both identifies the
  class from the counts.

--write DIR writes results/quandela/cases/belenos_mesh/ from retained cases
and runs; --check DIR recomputes every derived number from the retained
phases and sources; --rca OUT writes the leakage root-cause record of the
qpu:belenos bright-block run and --check-rca OUT replays it; --self-test
requires architecture, phase, source, baseline and RCA mutations to be
rejected and cross-checks the decoder and BS convention against exqalibur
and Perceval where they import.

Usage: "$PYTHON" scripts/qd_belenos_mesh.py (--write DIR | --check DIR | --rca OUT | --check-rca OUT | --self-test)
"""

from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import json
import math
import re
import struct
import sys
import zlib
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import parallel  # noqa: E402
from cd_core import cd_multiply, cd_sign  # noqa: E402

CATALOGUE = ROOT / "docs/evidence/quandela/catalogue.json"
CASES = ROOT / "results/quandela/cases"
RUNS = ROOT / "results/quandela/runs"
RCA = ROOT / "docs/evidence/quandela/belenos_leakage_rca.json"
CHIP = "qpu:belenos"
MODES = 24
FAMILY = "belenos_mesh"
CASES_SCHEMA = "qd-belenos-mesh-cases-v1"
CIRCUIT_SCHEMA = "qd-mesh-circuit-v1"
RCA_SCHEMA = "qd-belenos-leakage-rca-v1"
ANALYSIS_SCHEMA = "qd-belenos-mesh-analysis-v1"
TRANSPILE_TOLERANCE = 1e-9
LIKELIHOOD_FLOOR = 1e-6
SAMPLES_PER_SETTING = 1_500
SHOT_HEADROOM = 2
MAX_DURATION = 300
MARGIN = 2
FIT_TRIALS = 12
FIT_GOAL = 5e-4
FIT_TOLERANCE = 2e-3
BLOCK_SIZES = (6, 8, 10)
BAR_TOLERANCE = 1e-3
NUMERIC_TOLERANCE = 1e-7
NOISE_REPLICATES = 200
SEED = 20261017
# (name, kind, magnitude); noise kinds average NOISE_REPLICATES seeded replicates, and a
# source model sends the photon into the input mode magnitude away, a demultiplexer misroute.
MODELS = (
    ("phase_noise_0.1", "phase_noise", 0.1),
    ("phase_noise_0.2", "phase_noise", 0.2),
    ("phase_noise_0.4", "phase_noise", 0.4),
    ("theta_noise_0.05", "theta_noise", 0.05),
    ("gain_-0.1", "gain", -0.1),
    ("gain_-0.3", "gain", -0.3),
    ("crosstalk_0.05", "crosstalk", 0.05),
    ("crosstalk_0.155", "crosstalk", 0.155),
    ("ceiling_4.94", "ceiling", 4.94),
    ("source_-2", "source", -2),
    ("source_+2", "source", 2),
    ("source_-4", "source", -4),
)
Q1_RUN = "2026-10-17T213646Z-qpu_belenos-box_kite_photonic_single-job-04"
DARK_SIM_RUN = "2026-10-17T213306Z-sim_belenos-box_kite_photonic_single-job-05"
SOURCES = {
    "bright": "box_kite_photonic_single/job-04",
    "dark": "box_kite_photonic_single/job-05",
    "edge": "belenos_fringe/job-00",
    "strut": "belenos_fringe/job-01",
}
FRINGE_QUARTERS = (0, 2, 4, 6)
CENSUS = ROOT / "docs/evidence/box_kite_census/census.json"
SINGLE = "box_kite_photonic_single"
# The one-photon two-label configurations every box-kite edge product uses:
# its zero sign choice (dark) and the flipped y sign (bright control).
ZERO_DIVISOR_JOBS = {"dark": (5, 6, 8, 11, 16, 19, 21, 22), "bright": (4, 7, 9, 10, 17, 18, 20, 23)}
SOURCES.update({f"{k}-{n:02d}": f"{SINGLE}/job-{n:02d}" for k, numbers in ZERO_DIVISOR_JOBS.items() for n in numbers})
SINGLE_SETTING = "cold-bright-20"

Element = tuple[str, int, Any]


class MeshError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise MeshError(message)


# --- protobuf wire decoding (standard library) ---------------------------------------------


def _varint(data: bytes, i: int) -> tuple[int, int]:
    shift = value = 0
    while True:
        require(i < len(data), "truncated varint")
        byte = data[i]
        i += 1
        value |= (byte & 0x7F) << shift
        if byte < 0x80:
            return value, i
        shift += 7


def wire(data: bytes) -> list[tuple[int, Any]]:
    """(field number, value) pairs of one message: varints as int, fixed64 as double, length-delimited as bytes."""
    out: list[tuple[int, Any]] = []
    i = 0
    while i < len(data):
        key, i = _varint(data, i)
        number, kind = key >> 3, key & 7
        value: Any
        if kind == 0:
            value, i = _varint(data, i)
        elif kind == 1:
            require(i + 8 <= len(data), "truncated fixed64")
            value = struct.unpack_from("<d", data, i)[0]
            i += 8
        elif kind == 2:
            size, i = _varint(data, i)
            require(i + size <= len(data), "truncated length-delimited field")
            value = data[i : i + size]
            i += size
        elif kind == 5:
            value = struct.unpack_from("<f", data, i)[0]
            i += 4
        else:
            raise MeshError(f"wire type {kind} is not in the circuit schema")
        out.append((number, value))
    return out


def _parameter(data: bytes) -> float | str:
    fields = dict(wire(data))
    if 2 in fields:
        return bytes(fields[2]).decode()
    return float(fields.get(1, 0.0))


def _components(messages: list[bytes], base: int, out: list[Element]) -> None:
    for message in messages:
        fields = wire(message)
        start = base + next((v for n, v in fields if n == 1), 0)
        kinds = [n for n, _ in fields if n >= 10]
        require(len(kinds) == 1, f"component carries fields {kinds}")
        body = next(v for n, v in fields if n >= 10)
        if kinds[0] == 10:
            _components([v for n, v in wire(body) if n == 4], start, out)
        elif kinds[0] == 11:
            out.append(("ps", start, _parameter(dict(wire(body))[1])))
        elif kinds[0] == 12:
            bs = dict(wire(body))
            require(bs.get(1, 0) == 0, f"beam splitter convention {bs.get(1)} is not Rx")
            angles = tuple(_parameter(bs[n]) if n in bs else 0.0 for n in (2, 3, 4, 5, 6))
            require(all(isinstance(a, float) for a in angles), "a beam splitter angle is symbolic")
            out.append(("bs", start, angles))
        elif kinds[0] != 22:
            raise MeshError(f"component field {kinds[0]} is outside the Belenos mesh")


def unzip(text: str) -> str:
    if text.startswith(":PCVL:zip:"):
        return zlib.decompress(base64.b64decode(text[len(":PCVL:zip:") :])).decode()
    return text


def decode(text: str) -> list[Element]:
    """Elements of a ':PCVL:ACircuit:' (computed_circuit) or ':PCVL:Experiment:' (architecture) string."""
    text = unzip(text)
    for tag, field in ((":PCVL:ACircuit:", 4), (":PCVL:Experiment:", 9)):
        if text.startswith(tag):
            fields = wire(base64.b64decode(text[len(tag) :]))
            out: list[Element] = []
            _components([v for n, v in fields if n == field], 0, out)
            return out
    raise MeshError(f"{text[:24]!r} is not a serialized circuit or experiment")


def architecture(catalogue: dict[str, Any]) -> list[Element]:
    elements = decode(catalogue["processors"][CHIP]["specs"]["architecture"])
    symbols = [p for k, _, p in elements if k == "ps"]
    require(all(isinstance(s, str) for s in symbols), "an architecture phase is numeric")
    require(len(set(symbols)) == len(symbols), "an architecture phase symbol repeats")
    require(all(p[1:] == (0.0, 0.0, 0.0, 0.0) for k, _, p in elements if k == "bs"), "a coupler carries a phase")
    return elements


def load_catalogue() -> dict[str, Any]:
    value: dict[str, Any] = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    return value


def same_mesh(arch: list[Element], mesh: list[Element]) -> bool:
    """Equal topology and coupler angles: the architecture with numbers in place of its phase symbols."""
    if len(arch) != len(mesh):
        return False
    return all(
        a[0] == b[0] and a[1] == b[1] and (a[0] == "ps" or a[2] == b[2]) for a, b in zip(arch, mesh, strict=True)
    )


def mesh_phases(arch: list[Element], mesh: list[Element]) -> list[float]:
    require(same_mesh(arch, mesh), "the compiled mesh differs from the architecture")
    return [float(p) % (2 * math.pi) for k, _, p in mesh if k == "ps"]


def raw_result(run: Path) -> dict[str, Any]:
    outer: dict[str, Any] = json.loads((run / "raw/result.json").read_text(encoding="utf-8"))
    inner: dict[str, Any] = json.loads(outer["results"])
    return inner


def computed_circuits(run: Path) -> list[str]:
    inner = raw_result(run)
    if "results_list" in inner:
        return [entry["computed_circuit"] for entry in inner["results_list"]]
    return [inner["computed_circuit"]]


def bscount(text: str) -> dict[tuple[int, ...], int]:
    out: dict[tuple[int, ...], int] = {}
    for state, n in re.findall(r"\|([0-9,]+)>=(\d+)", unzip(text)):
        key = tuple(int(x) for x in state.split(","))
        out[key] = out.get(key, 0) + int(n)
    return out


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q2(entry: list[str]) -> float:
    return float(Fraction(entry[0])) + float(Fraction(entry[1])) * math.sqrt(2.0)


# --- numerical mesh (numpy) ----------------------------------------------------------------


def coupler(theta: float, tl: float = 0.0, bl: float = 0.0, tr: float = 0.0, br: float = 0.0) -> Any:
    """Perceval's Rx beam splitter, output = B @ input on (top, bottom)."""
    import numpy as np

    c, s = math.cos(theta / 2), math.sin(theta / 2)
    return np.array(
        [
            [np.exp(1j * (tl + tr)) * c, 1j * np.exp(1j * (tr + bl)) * s],
            [1j * np.exp(1j * (tl + br)) * s, np.exp(1j * (br + bl)) * c],
        ]
    )


def phase_slots(arch: list[Element]) -> list[int]:
    return [j for j, (k, _, _) in enumerate(arch) if k == "ps"]


def unitary(arch: list[Element], phases: list[float]) -> Any:
    import numpy as np

    u = np.eye(MODES, dtype=complex)
    t = 0
    for kind, m, p in arch:
        if kind == "bs":
            u[m : m + 2, :] = coupler(*p) @ u[m : m + 2, :]
        else:
            u[m, :] *= np.exp(1j * phases[t])
            t += 1
    return u


def propagate(arch: list[Element], phases: list[float], source: int, dphi: Any = None, dtheta: Any = None) -> Any:
    """|amplitude|^2 per mode of one photon entering source, over replicate rows of phase and angle errors."""
    import numpy as np

    reps = 1 if dphi is None and dtheta is None else len(dphi if dphi is not None else dtheta)
    psi = np.zeros((reps, MODES), dtype=complex)
    psi[:, source] = 1
    ip = ib = 0
    base = np.asarray(phases)
    for kind, m, p in arch:
        if kind == "bs":
            theta = p[0] + (dtheta[:, ib] if dtheta is not None else 0.0)
            ib += 1
            c, s = np.cos(np.asarray(theta) / 2), np.sin(np.asarray(theta) / 2)
            top, bottom = psi[:, m].copy(), psi[:, m + 1].copy()
            psi[:, m] = c * top + 1j * s * bottom
            psi[:, m + 1] = 1j * s * top + c * bottom
        else:
            psi[:, m] *= np.exp(1j * (base[ip] + (dphi[:, ip] if dphi is not None else 0.0)))
            ip += 1
    return np.abs(psi) ** 2


def mzis(arch: list[Element]) -> list[dict[str, Any]]:
    """MZIs as {m, bs: (j1, j2), ps: (slot_a, slot_b), col}, phase slots indexing the 574 phases."""
    slot = {j: t for t, j in enumerate(phase_slots(arch))}
    out: list[dict[str, Any]] = []
    state: dict[int, dict[str, Any]] = {}
    column = column_index(arch)
    for j, (kind, m, _) in enumerate(arch):
        if kind == "bs":
            if m in state and len(state[m]["ps"]) == 2:
                first = state.pop(m)
                out.append({"m": m, "bs": (first["bs"], j), "ps": tuple(first["ps"]), "col": column[first["bs"]]})
            else:
                require(m not in state, f"coupler on mode {m} closes no MZI")
                state[m] = {"bs": j, "ps": []}
        else:
            hit = [low for low in state if low in (m, m - 1) and len(state[low]["ps"]) < 2]
            if hit:
                state[hit[0]]["ps"].append(slot[j])
    require(not state, "an MZI is left open")
    return out


def column_index(arch: list[Element]) -> list[int]:
    front = [0] * (MODES + 1)
    out = []
    for kind, m, _ in arch:
        low, high = (m, m + 2) if kind == "bs" else (m, m + 1)
        c = max(front[low:high])
        out.append(c)
        for k in range(low, high):
            front[k] = c + 1
    return out


def mzi_matrix(arch: list[Element], z: dict[str, Any], a: float, b: float) -> Any:
    import numpy as np

    slots = phase_slots(arch)
    d = np.eye(2, dtype=complex)
    for value, t in ((a, z["ps"][0]), (b, z["ps"][1])):
        d[arch[slots[t]][1] - z["m"], arch[slots[t]][1] - z["m"]] *= np.exp(1j * value)
    first, second = (arch[j][2] for j in z["bs"])
    return coupler(*second) @ d @ coupler(*first)


def bar_delta(arch: list[Element], z: dict[str, Any]) -> tuple[float, float]:
    """The second phase that minimizes the MZI's off-diagonal power with the first at 0, and that power."""
    from scipy.optimize import minimize_scalar

    def leak(delta: float) -> float:
        return float(abs(mzi_matrix(arch, z, 0.0, delta)[0, 1]) ** 2)

    grid = [-math.pi + k * math.pi / 36 for k in range(72)]
    start = min(grid, key=leak)
    found = minimize_scalar(leak, bracket=(start - 0.1, start, start + 0.1), tol=1e-12)
    return float(found.x) % (2 * math.pi), float(found.fun)


def baseline(arch: list[Element], region: range | None) -> list[float]:
    """Bar phases on every MZI (region None) or on the MZIs touching region; every other phase 0."""
    phases = [0.0] * len(phase_slots(arch))
    for z in mzis(arch):
        if region is None or {z["m"], z["m"] + 1} & set(region):
            phases[z["ps"][1]] = bar_delta(arch, z)[0]
    return phases


def block_mzis(arch: list[Element], low: int, width: int, count: int) -> list[dict[str, Any]]:
    """The first count MZIs inside modes low..low+width-1 in column order: a rectangular sub-mesh."""
    inside = [z for z in mzis(arch) if low <= z["m"] and z["m"] + 1 < low + width]
    inside.sort(key=lambda z: (z["col"], z["m"]))
    require(len(inside) >= count, f"modes {low}..{low + width - 1} hold {len(inside)} MZIs")
    return inside[:count]


class BlockFit:
    """Phases of the block MZIs that put D_out T D_in on modes low..low+k-1, from a fixed baseline.

    Each sub-mesh size of BLOCK_SIZES runs FIT_TRIALS seeded starts; the first
    size whose best start reaches FIT_GOAL wins, and among its starts within
    FIT_GOAL the one with the least summed block phase is kept, since heater
    gain and thermal crosstalk errors scale with the driven phase.
    """

    def __init__(self, arch: list[Element]) -> None:
        self.arch = arch

    def __call__(self, job: tuple[list[list[complex]], int, list[float], int]) -> dict[str, Any]:
        target_rows, low, start, seed = job
        for count in BLOCK_SIZES:
            slots = [t for z in block_mzis(self.arch, low, len(target_rows), count) for t in z["ps"]]
            fit = self.fit(target_rows, low, start, slots, seed)
            if fit["error"] <= FIT_GOAL:
                break
        return {"block_mzis": count, **{k: v for k, v in fit.items() if k != "error"}}

    def fit(
        self, target_rows: list[list[complex]], low: int, start: list[float], slots: list[int], seed: int
    ) -> dict[str, Any]:
        import numpy as np
        from scipy.optimize import least_squares

        target = np.array(target_rows, dtype=complex)
        k = len(target)
        segments, order = self._segments(start, set(slots))

        def block(x: Any) -> Any:
            values = dict(zip(slots, x[: len(slots)], strict=True))
            u = segments[0]
            for t, m, segment in order:
                u = u.copy()
                u[m, :] *= np.exp(1j * values[t])
                u = segment @ u
            return u[low : low + k, low : low + k]

        def residual(x: Any) -> Any:
            frame_out = np.exp(1j * x[len(slots) : len(slots) + k])
            frame_in = np.exp(1j * x[len(slots) + k :])
            r = frame_out[:, None] * target * frame_in[None, :] - block(x)
            return np.concatenate([r.real.ravel(), r.imag.ravel()])

        rng = np.random.default_rng(seed)
        found = []
        for _ in range(FIT_TRIALS):
            r = least_squares(residual, rng.uniform(-math.pi, math.pi, len(slots) + 2 * k), xtol=1e-13, ftol=1e-13)
            error = float(np.max(np.abs(residual(r.x))))
            heat = float(np.sum(np.mod(r.x[: len(slots)], 2 * math.pi)))
            found.append((error, heat, r.x))
        exact = [f for f in found if f[0] <= FIT_GOAL]
        error, _, x = min(exact, key=lambda f: f[1]) if exact else min(found, key=lambda f: f[0])
        phases = list(start)
        for t, value in zip(slots, x[: len(slots)], strict=True):
            phases[t] = float(value) % (2 * math.pi)
        return {
            "error": error,
            "phases": phases,
            "frame_out": [float(v) % (2 * math.pi) for v in x[len(slots) : len(slots) + k]],
            "frame_in": [float(v) % (2 * math.pi) for v in x[len(slots) + k :]],
        }

    def _segments(self, start: list[float], variable: set[int]) -> tuple[list[Any], list[tuple[int, int, Any]]]:
        import numpy as np

        first = None
        order: list[tuple[int, int, Any]] = []
        u = np.eye(MODES, dtype=complex)
        pending: tuple[int, int] | None = None
        t = 0
        for kind, m, p in self.arch:
            if kind == "ps" and t in variable:
                if pending is None:
                    first = u
                else:
                    order.append((pending[0], pending[1], u))
                pending = (t, m)
                u = np.eye(MODES, dtype=complex)
                t += 1
                continue
            if kind == "bs":
                u[m : m + 2, :] = coupler(*p) @ u[m : m + 2, :]
            else:
                u[m, :] *= np.exp(1j * start[t])
                t += 1
        assert pending is not None and first is not None
        order.append((pending[0], pending[1], u))
        return [first], order


def block_error(arch: list[Element], phases: list[float], target: Any, low: int, setting: dict[str, Any]) -> float:
    import numpy as np

    k = len(target)
    u = unitary(arch, phases)[low : low + k, low : low + k]
    frame_out = np.exp(1j * np.array(setting["frame_out"]))
    frame_in = np.exp(1j * np.array(setting["frame_in"]))
    return float(np.max(np.abs(frame_out[:, None] * target * frame_in[None, :] - u)))


def neighbours(arch: list[Element]) -> list[list[int]]:
    column = column_index(arch)
    slots = phase_slots(arch)
    where = [(arch[j][1], column[j]) for j in slots]
    return [
        [b for b, (mb, cb) in enumerate(where) if b != a and abs(mb - ma) <= 1 and abs(cb - ca) <= 1]
        for a, (ma, ca) in enumerate(where)
    ]


def predict(arch: list[Element], phases: list[float], source: int, nbr: list[list[int]]) -> dict[str, list[float]]:
    """Per-mode detection probability of each error model, from seeded replicates where the model is random."""
    import numpy as np

    phi = np.asarray(phases) % (2 * math.pi)
    out: dict[str, list[float]] = {"ideal": propagate(arch, list(phi), source)[0].tolist()}
    for index, (name, kind, size) in enumerate(MODELS):
        rng = np.random.default_rng([SEED, index])
        if kind == "phase_noise":
            p = propagate(arch, list(phi), source, dphi=rng.normal(0, size, (NOISE_REPLICATES, len(phi)))).mean(0)
        elif kind == "theta_noise":
            n_bs = sum(1 for e in arch if e[0] == "bs")
            p = propagate(arch, list(phi), source, dtheta=rng.normal(0, size, (NOISE_REPLICATES, n_bs))).mean(0)
        elif kind == "gain":
            p = propagate(arch, list(phi + size * phi), source)[0]
        elif kind == "crosstalk":
            heat = np.array([phi[n].sum() for n in nbr])
            p = propagate(arch, list(phi + size * heat), source)[0]
        elif kind == "ceiling":
            p = propagate(arch, list(np.minimum(phi, size)), source)[0]
        else:
            p = propagate(arch, list(phi), min(max(source + int(size), 0), MODES - 1))[0]
        out[name] = p.tolist()
    return {name: [round(float(v), 9) for v in values] for name, values in out.items()}


def peak_occupancy(arch: list[Element], phases: list[float], source: int) -> list[float]:
    import numpy as np

    psi = np.zeros(MODES, dtype=complex)
    psi[source] = 1
    peak = np.abs(psi) ** 2
    t = 0
    for kind, m, p in arch:
        if kind == "bs":
            psi[m : m + 2] = coupler(*p) @ psi[m : m + 2]
        else:
            psi[m] *= np.exp(1j * phases[t])
            t += 1
        peak = np.maximum(peak, np.abs(psi) ** 2)
    return [round(float(v), 6) for v in peak]


# --- case family ---------------------------------------------------------------------------


def source_target(name: str, quarter: int | None) -> tuple[Any, dict[str, Any]]:
    """The 4x4 case unitary of a retained box-kite case, times the fringe preparation at phi = quarter pi/4."""
    import numpy as np

    case = CASES / SOURCES[name]
    manifest = json.loads((case / "cases.json").read_text(encoding="utf-8"))
    circuit_path = case / manifest["circuit"]["file"]
    require(sha256(circuit_path) == manifest["circuit"]["sha256"], f"{case}: circuit differs from its digest")
    circuit = json.loads(circuit_path.read_text(encoding="utf-8"))
    (component,) = circuit["components"]
    u = np.array([[q2(e) for e in row] for row in component["unitary"]], dtype=complex)
    if quarter is not None:
        require("prep_phase" in component, f"{case} carries no preparation phase")
        phase = np.exp(1j * quarter * math.pi / 4)
        prep = np.eye(4, dtype=complex)
        prep[:2, :2] = np.array([[1, 1], [phase, -phase]]) / math.sqrt(2)
        u = u @ prep
    ref: dict[str, Any] = {
        "case": SOURCES[name],
        "cases_sha256": sha256(case / "cases.json"),
        "circuit_sha256": sha256(circuit_path),
    }
    if quarter is not None:
        ref["phi_quarter_pi"] = quarter
    return u, ref


def edge_coverage() -> dict[str, Any]:
    """Every box-kite edge's zero products and bright controls, certified by cd_core and mapped to their circuit.

    An edge (e_i + s e_j)(e_k + t e_l) of the census has two zero sign
    choices (s, t); flipping t gives the bright control. Each product's sign
    block M with the y sign selects one single-series configuration, whose
    retained block carries the same (M, t).
    """
    census = json.loads(CENSUS.read_text(encoding="utf-8"))
    configs = {}
    for kind, numbers in ZERO_DIVISOR_JOBS.items():
        for n in numbers:
            (block,) = json.loads((CASES / SINGLE / f"job-{n:02d}" / "cases.json").read_text(encoding="utf-8"))[
                "blocks"
            ]
            configs[(json.dumps(block["m"]), block["t"])] = f"{kind}-{n:02d}"
    uses: dict[str, int] = dict.fromkeys(configs.values(), 0)
    edges = 0
    for kite in census["kites"]:
        for edge in kite["edges"]:
            edges += 1
            (i, j), (k, el) = edge["pair"]
            for s, t in edge["zero_signs"]:
                for y_sign, kind in ((t, "dark"), (-t, "bright")):
                    x, y = [0.0] * 16, [0.0] * 16
                    x[i], x[j], y[k], y[el] = 1.0, float(s), 1.0, float(y_sign)
                    norm = sum(v * v for v in cd_multiply(16, x, y))
                    require(norm == (0 if kind == "dark" else 8), f"edge {edge['pair']} ({s}, {y_sign}): |xy|^2 {norm}")
                    m = [[cd_sign(16, i, k), s * cd_sign(16, j, el)], [s * cd_sign(16, j, k), cd_sign(16, i, el)]]
                    name = configs.get((json.dumps(m), y_sign), "")
                    require(name.startswith(kind), f"edge {edge['pair']}: no {kind} configuration")
                    uses[name] += 1
    return {
        "edges": edges,
        "dark_products": sum(v for k, v in uses.items() if k.startswith("dark")),
        "bright_products": sum(v for k, v in uses.items() if k.startswith("bright")),
        "uses": uses,
    }


def plan_zero_divisor_settings() -> list[dict[str, Any]]:
    """The 84/84 job: every configuration the box-kite edge products use, one iteration each, at modes 20-23."""
    return [
        {"name": f"cold-{kind}-{n:02d}-20", "mesh": "cold", "target": f"{kind}-{n:02d}", "low": 20}
        for kind in ("dark", "bright")
        for n in ZERO_DIVISOR_JOBS[kind]
    ]


def plan_settings() -> list[dict[str, Any]]:
    """The discrimination job: the same blocks under the compiled, hot and cold meshes, plus fringes."""
    out: list[dict[str, Any]] = [
        {"name": "compiled-bright-20", "mesh": "compiled", "target": "bright", "low": 20, "run": Q1_RUN},
        {"name": "hot-identity-20", "mesh": "hot", "target": "identity", "low": 20},
        {"name": "cold-identity-20", "mesh": "cold", "target": "identity", "low": 20},
        {"name": "hot-bright-20", "mesh": "hot", "target": "bright", "low": 20},
        {"name": "cold-bright-20", "mesh": "cold", "target": "bright", "low": 20},
        {"name": "compiled-dark-20", "mesh": "compiled", "target": "dark", "low": 20, "run": DARK_SIM_RUN},
        {"name": "cold-dark-20", "mesh": "cold", "target": "dark", "low": 20},
        {"name": "cold-bright-0", "mesh": "cold", "target": "bright", "low": 0},
    ]
    for kind in ("edge", "strut"):
        for quarter in FRINGE_QUARTERS:
            out.append(
                {"name": f"cold-{kind}-20-q{quarter}", "mesh": "cold", "target": kind, "low": 20, "quarter": quarter}
            )
    return out


def region(low: int, width: int = 4) -> range:
    return range(max(0, low - MARGIN), min(MODES, low + width + MARGIN))


def realize(arch: list[Element], plans: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Phases, frames and source references of every planned setting; block fits run on the process pool."""
    baselines: dict[Any, list[float]] = {}
    jobs, owners = [], []
    settings = []
    for index, plan in enumerate(plans):
        setting: dict[str, Any] = {key: plan[key] for key in ("name", "mesh", "target", "low")}
        if plan["mesh"] == "compiled":
            run = RUNS / plan["run"]
            setting["source_run"] = {"run": plan["run"], "result_sha256": sha256(run / "raw/result.json")}
            (text,) = computed_circuits(run)
            setting["phases"] = mesh_phases(arch, decode(text))
            setting["frame_out"] = setting["frame_in"] = None
        else:
            key = None if plan["mesh"] == "hot" else plan["low"]
            if key not in baselines:
                baselines[key] = baseline(arch, None if key is None else region(plan["low"]))
            start = baselines[key]
            if plan["target"] == "identity":
                setting["phases"] = list(start)
                setting["frame_out"] = setting["frame_in"] = None
            else:
                target, _ = source_target(plan["target"], plan.get("quarter"))
                rows = [[complex(v) for v in row] for row in target]
                jobs.append((rows, plan["low"], start, SEED + index))
                owners.append(index)
        if plan["target"] != "identity":
            setting["source"] = source_target(plan["target"], plan.get("quarter"))[1]
        settings.append(setting)
    for index, fit in zip(owners, parallel.ordered_map(BlockFit(arch), jobs, min_items=2), strict=True):
        settings[index].update(fit)
    return settings


def derived(arch: list[Element], setting: dict[str, Any], nbr: list[list[int]]) -> dict[str, Any]:
    """Every number a setting's sent phases determine: design distribution, fit error, occupancy, heat."""
    import numpy as np

    low = setting["low"]
    out: dict[str, Any] = {}
    if setting["target"] != "identity":
        target, _ = source_target(setting["target"], setting["source"].get("phi_quarter_pi"))
        if setting["mesh"] != "compiled":
            out["block_error"] = round(block_error(arch, setting["phases"], target, low, setting), 9)
        out["case_ideal"] = [round(float(v), 9) for v in np.abs(target[:, 0]) ** 2]
    out["design_distribution"] = [round(float(v), 9) for v in propagate(arch, setting["phases"], low)[0]]
    out["peak_occupancy"] = peak_occupancy(arch, setting["phases"], low)
    out["heater_phase_sum"] = round(sum(setting["phases"]), 6)
    return out


class Derive:
    def __init__(self, arch: list[Element], nbr: list[list[int]]) -> None:
        self.arch, self.nbr = arch, nbr

    def __call__(self, setting: dict[str, Any]) -> dict[str, Any]:
        return derived(self.arch, setting, self.nbr)


def documents(
    arch: list[Element], settings: list[dict[str, Any]], catalogue_sha: str, job: str, coverage: Any = None
) -> tuple[str, str]:
    nbr = neighbours(arch)
    facts = parallel.ordered_map(Derive(arch, nbr), settings, min_items=2)
    circuit = {
        "schema": CIRCUIT_SCHEMA,
        "modes": MODES,
        "architecture": {
            "catalogue_sha256": catalogue_sha,
            "symbols": [p for k, _, p in arch if k == "ps"],
            "couplers": [[m, p[0]] for k, m, p in arch if k == "bs"],
        },
        "settings": [
            {"name": s["name"], "input_mode": s["low"], "phases": [round(v, 12) for v in s["phases"]]} for s in settings
        ],
    }
    circuit_text = json.dumps(circuit, separators=(",", ":")) + "\n"
    rows = []
    for s, f in zip(settings, facts, strict=True):
        row = {k: s[k] for k in ("name", "mesh", "target", "low")}
        for key in ("source", "source_run", "block_mzis", "frame_out", "frame_in"):
            if s.get(key) is not None:
                row[key] = [round(v, 12) for v in s[key]] if key.startswith("frame") else s[key]
        row.update(f)
        rows.append(row)
    steps = len(settings)
    manifest = {
        "schema": CASES_SCHEMA,
        "family": FAMILY,
        "job": job,
        "platforms": ["sim:belenos", CHIP],
        "command": "sample_count",
        "gate_form": "mesh",
        "min_detected_photons": 1,
        "iterations": steps,
        "max_samples": SAMPLES_PER_SETTING * steps,
        "max_shots": SAMPLES_PER_SETTING * steps * SHOT_HEADROOM,
        "max_duration": MAX_DURATION,
        "circuit": {"file": "circuit.json", "sha256": hashlib.sha256(circuit_text.encode()).hexdigest()},
        "models": [{"name": n, "kind": k, "size": v} for n, k, v in MODELS],
        "noise_replicates": NOISE_REPLICATES,
        "seed": SEED,
        "settings": rows,
        **({"coverage": coverage} if coverage is not None else {}),
        "preregistered": {
            "transpilation": "the service re-transpiles every iteration, so each model's prediction is computed "
            "on the computed_circuit the iteration returns; the same body compiles to the same meshes on "
            "sim:belenos and qpu:belenos while the couplers are unchanged",
            "classes": "phase noise, coupler noise, heater gain, thermal crosstalk, a phase ceiling and a "
            "demultiplexer misroute (source models) each predict a different histogram per returned mesh",
            "decision": "the model with the highest efficiency-weighted multinomial log-likelihood summed over all "
            "settings names the chip's error class; the identity settings read the misroute directly",
        },
    }
    return json.dumps(manifest, indent=1) + "\n", circuit_text


def write(directory: Path) -> None:
    catalogue = load_catalogue()
    arch = architecture(catalogue)
    settings = realize(arch, plan_settings())
    write_job(directory, arch, "job-00", settings)
    write_job(directory, arch, "job-01", [s for s in settings if s["name"] == SINGLE_SETTING])
    write_job(directory, arch, "job-02", realize(arch, plan_zero_divisor_settings()), edge_coverage())


def write_job(
    directory: Path, arch: list[Element], name: str, settings: list[dict[str, Any]], coverage: Any = None
) -> None:
    """One case directory; a one-setting job sends its phases as numbers, the guide's pre-compiled form."""
    manifest, circuit = documents(arch, settings, sha256(CATALOGUE), name, coverage)
    job = directory / FAMILY / name
    job.mkdir(parents=True, exist_ok=True)
    (job / "circuit.json").write_text(circuit, encoding="utf-8")
    (job / "cases.json").write_text(manifest, encoding="utf-8")
    print(f"{job}: {len(settings)} settings")


def close(a: Any, b: Any, path: str = "") -> None:
    """Recursive equality with NUMERIC_TOLERANCE on floats."""
    if isinstance(a, float) or isinstance(b, float):
        require(isinstance(a, int | float) and isinstance(b, int | float), f"{path}: {a!r} against {b!r}")
        require(abs(a - b) <= NUMERIC_TOLERANCE, f"{path}: {a!r} differs from {b!r}")
    elif isinstance(a, dict):
        require(isinstance(b, dict) and set(a) == set(b), f"{path}: keys differ")
        for key in a:
            close(a[key], b[key], f"{path}.{key}")
    elif isinstance(a, list):
        require(isinstance(b, list) and len(a) == len(b), f"{path}: lengths differ")
        for i, (x, y) in enumerate(zip(a, b, strict=True)):
            close(x, y, f"{path}[{i}]")
    else:
        require(a == b, f"{path}: {a!r} differs from {b!r}")


def admit(job: Path, catalogue: dict[str, Any] | None = None) -> None:
    """Recompute every derived number of a mesh case from its retained phases, architecture and sources."""
    catalogue = load_catalogue() if catalogue is None else catalogue
    arch = architecture(catalogue)
    manifest = json.loads((job / "cases.json").read_text(encoding="utf-8"))
    circuit_text = (job / "circuit.json").read_text(encoding="utf-8")
    require(hashlib.sha256(circuit_text.encode()).hexdigest() == manifest["circuit"]["sha256"], "circuit digest")
    circuit = json.loads(circuit_text)
    require(circuit["schema"] == CIRCUIT_SCHEMA and manifest["schema"] == CASES_SCHEMA, "schema")
    spec = circuit["architecture"]
    require(spec["symbols"] == [p for k, _, p in arch if k == "ps"], "architecture phase symbols differ")
    require(spec["couplers"] == [[m, p[0]] for k, m, p in arch if k == "bs"], "architecture couplers differ")
    require(len(circuit["settings"]) == len(manifest["settings"]) == manifest["iterations"], "setting count")
    rebuilt = []
    for row, sent in zip(manifest["settings"], circuit["settings"], strict=True):
        require(row["name"] == sent["name"] and sent["input_mode"] == row["low"], f"{row['name']}: setting order")
        require(len(sent["phases"]) == len(spec["symbols"]), f"{row['name']}: phase count")
        setting = {**row, "phases": sent["phases"]}
        if row["mesh"] == "compiled":
            run = RUNS / row["source_run"]["run"]
            require(sha256(run / "raw/result.json") == row["source_run"]["result_sha256"], f"{row['name']}: source run")
            (text,) = computed_circuits(run)
            close(mesh_phases(arch, decode(text)), sent["phases"], f"{row['name']}.phases")
        else:
            check_baseline(arch, row, sent["phases"])
        if row["target"] != "identity":
            _, ref = source_target(row["target"], row["source"].get("phi_quarter_pi"))
            require(ref == row["source"], f"{row['name']}: source case digests differ")
        rebuilt.append(setting)
    nbr = neighbours(arch)
    facts = parallel.ordered_map(Derive(arch, nbr), rebuilt, min_items=2)
    for row, fact in zip(manifest["settings"], facts, strict=True):
        close({k: row[k] for k in fact}, fact, row["name"])
        if "block_error" in fact:
            require(fact["block_error"] <= FIT_TOLERANCE, f"{row['name']}: block error {fact['block_error']}")


def check_baseline(arch: list[Element], row: dict[str, Any], phases: list[float]) -> None:
    """Every MZI outside the block is in bar where the mesh form puts it there and idles at phase 0 elsewhere."""
    keep = None if row["mesh"] == "hot" else set(region(row["low"]))
    block_slots = (
        set()
        if row["target"] == "identity"
        else {t for z in block_mzis(arch, row["low"], 4, row["block_mzis"]) for t in z["ps"]}
    )
    for z in mzis(arch):
        if any(t in block_slots for t in z["ps"]):
            continue
        if keep is None or {z["m"], z["m"] + 1} & keep:
            off = float(abs(mzi_matrix(arch, z, phases[z["ps"][0]], phases[z["ps"][1]])[0, 1]) ** 2)
            require(off <= BAR_TOLERANCE, f"{row['name']}: MZI on {z['m']} column {z['col']} leaks {off:.2e}")
        else:
            require(phases[z["ps"][0]] == phases[z["ps"][1]] == 0.0, f"{row['name']}: idle MZI on {z['m']} is driven")
    edge = set(range(len(phases))) - {t for z in mzis(arch) for t in z["ps"]}
    require(all(phases[t] == 0.0 for t in edge), f"{row['name']}: an edge phase is driven")


def check(directory: Path) -> None:
    jobs = sorted(p for p in (directory / FAMILY).iterdir() if p.is_dir())
    require(
        [p.name for p in jobs] == ["job-00", "job-01", "job-02"], f"{directory / FAMILY} holds {[p.name for p in jobs]}"
    )
    for job in jobs:
        admit(job)
        print(f"{job}: mesh case admitted")
    manifest = json.loads((directory / FAMILY / "job-02" / "cases.json").read_text(encoding="utf-8"))
    coverage = edge_coverage()
    require(manifest.get("coverage") == coverage, "job-02 coverage differs from the census")
    require(
        [r["target"] for r in manifest["settings"]] == list(coverage["uses"]),
        "job-02 settings differ from its coverage",
    )
    products = f"{coverage['dark_products']} zero products, {coverage['bright_products']} controls"
    print(f"job-02 covers {coverage['edges']} edges: {products}")


# --- leakage root-cause record ---------------------------------------------------------------


def observed(run: Path) -> tuple[Any, dict[str, Any]]:
    """Dark-subtracted one-click distribution of a one-photon run and its raw facts."""
    import numpy as np

    inner = raw_result(run)
    counts = bscount(inner["results"])
    single = np.zeros(MODES)
    multi = 0
    for state, n in counts.items():
        if sum(state) == 1:
            single[state.index(1)] += n
        else:
            multi += n
    submission = json.loads((run / "submission.json").read_text(encoding="utf-8"))
    perfs = submission["perfs_at_plan"]
    duration = json.loads((run / "raw/result.json").read_text(encoding="utf-8"))["duration"]
    dark = np.array(perfs["Dark counts (detection/s)"], dtype=float) * duration
    corrected = np.clip(single - dark, 0, None)
    eta = np.array(perfs["Transmission per mode (%)"]["t_out"], dtype=float)
    facts = {
        "single_click": [int(v) for v in single],
        "other_events": multi,
        "duration_s": duration,
        "dark_expected": [round(float(v), 3) for v in dark],
        "t_out": [float(v) for v in eta],
        "computed_input": inner["computed_input"],
    }
    return corrected / corrected.sum(), {"facts": facts, "eta": eta}


def shot_floor(p: Any, n: int) -> float:
    """Expected total variation of an n-sample multinomial histogram from its own distribution p."""
    return round(sum(math.sqrt(float(v) * (1 - float(v)) / (2 * math.pi * n)) for v in p), 6)


def tvd(p: Any, q: Any) -> float:
    return round(0.5 * float(abs(p - q).sum()), 6)


def rca(out: Path) -> None:
    out.write_text(json.dumps(rca_record(), indent=1) + "\n", encoding="utf-8")
    print(f"{out}: written")


def rca_record() -> dict[str, Any]:
    import numpy as np

    catalogue = load_catalogue()
    arch = architecture(catalogue)
    run = RUNS / Q1_RUN
    obs, extra = observed(run)
    eta = extra["eta"]

    def seen(p: Any) -> Any:
        weighted = np.asarray(p) * eta
        return weighted / weighted.sum()

    (text,) = computed_circuits(run)
    compiled = mesh_phases(arch, decode(text))
    u = unitary(arch, compiled)
    columns = np.abs(u) ** 2
    for path in sorted(RUNS.iterdir()):
        if (path / "raw/result.json").is_file():
            for entry in computed_circuits(path):
                require(same_mesh(arch, decode(entry)), f"{path.name} returned a mesh outside the architecture")
    sources = catalogue["processors"][CHIP]["specs"]["connected_input_modes"]
    slots = phase_slots(arch)
    nbr = neighbours(arch)
    phi = np.asarray(compiled)

    def fit(kind: str, grid: list[float]) -> dict[str, Any]:
        scores = []
        for value in grid:
            if kind == "gain":
                trial = phi + value * phi
            elif kind == "crosstalk":
                trial = phi + value * np.array([phi[n].sum() for n in nbr])
            else:
                trial = np.minimum(phi, value)
            scores.append((tvd(seen(propagate(arch, list(trial), 20)[0]), obs), value))
        best = min(scores)
        return {"best": round(best[1], 6), "tvd": best[0]}

    noise = {}
    for sigma in (0.2, 0.3, 0.4, 0.5):
        rng = np.random.default_rng([SEED, int(sigma * 10)])
        p = propagate(arch, compiled, 20, dphi=rng.normal(0, sigma, (NOISE_REPLICATES, len(slots)))).mean(0)
        noise[f"{sigma}"] = tvd(seen(p), obs)
    variants = {
        "U": columns[:, 20],
        "U^T": np.abs(u.T[:, 20]) ** 2,
        "mirrored modes": np.abs(unitary(_mirror(arch), compiled)[:, 20]) ** 2,
    }
    return {
        "schema": RCA_SCHEMA,
        "run": Q1_RUN,
        "result_sha256": sha256(run / "raw/result.json"),
        "catalogue_sha256": sha256(CATALOGUE),
        "observed": {**extra["facts"], "dark_subtracted_distribution": [round(float(v), 6) for v in obs]},
        "compiled_mesh": {
            "column_20": [round(float(v), 6) for v in columns[:, 20]],
            "retained_meshes_matching_architecture": "all",
            "peak_occupancy_from_20": peak_occupancy(arch, compiled, 20),
            "heater_phase_sum": round(float(phi.sum()), 6),
        },
        "hypotheses": {
            "ideal_compiled_mesh": tvd(seen(columns[:, 20]), obs),
            "single_wrong_source": {str(k): tvd(seen(columns[:, k]), obs) for k in sources},
            "conventions": {name: tvd(seen(p), obs) for name, p in variants.items()},
            "gain": fit("gain", [round(-0.6 + 0.01 * k, 2) for k in range(121)]),
            "crosstalk": fit("crosstalk", [round(-0.2 + 0.005 * k, 3) for k in range(81)]),
            "ceiling": fit("ceiling", [round(3.0 + 0.05 * k, 2) for k in range(66)]),
            "phase_noise": noise,
            "shot_noise_floor": shot_floor(obs, sum(extra["facts"]["single_click"])),
        },
    }


def _mirror(arch: list[Element]) -> list[Element]:
    return [("bs", MODES - 2 - m, p) if k == "bs" else ("ps", MODES - 1 - m, p) for k, m, p in arch]


def check_rca(path: Path) -> None:
    retained = json.loads(path.read_text(encoding="utf-8"))
    close(retained, rca_record(), "rca")
    print(f"{path}: replays")


# --- run analysis (standard library) ----------------------------------------------------------


def circular_gap(a: float, b: float) -> float:
    d = (a - b) % (2 * math.pi)
    return min(d, 2 * math.pi - d)


def loglik(counts: list[int], model: list[float], eta: list[float], dark: list[float]) -> float:
    """Multinomial log-likelihood of one-click counts under lambda_m = A p_m eta_m + d_m with sum lambda = N."""
    n = sum(counts)
    weighted = [p * e for p, e in zip(model, eta, strict=True)]
    scale = max(n - sum(dark), 0.0) / max(sum(weighted), 1e-300)
    rates = [max(scale * w + d, LIKELIHOOD_FLOOR * n) for w, d in zip(weighted, dark, strict=True)]
    total = sum(rates)
    return sum(c * math.log(r / total) for c, r in zip(counts, rates, strict=True) if c)


def analyze_run(run: Path, manifest: dict[str, Any], circuit: dict[str, Any]) -> dict[str, Any]:
    """Per setting: transpilation check, one-click histogram, dark-corrected block share and model likelihoods."""
    arch = architecture(load_catalogue())
    inner = raw_result(run)
    entries = inner.get("results_list") or [inner]
    require(
        len(entries) == len(circuit["settings"]),
        f"{run.name}: {len(entries)} results for {len(circuit['settings'])} settings",
    )
    submission = json.loads((run / "submission.json").read_text(encoding="utf-8"))
    perfs = submission.get("perfs_at_plan", {})
    rates = perfs.get("Dark counts (detection/s)") or [0.0] * MODES
    eta = (perfs.get("Transmission per mode (%)") or {}).get("t_out") or [1.0] * MODES
    duration = float(json.loads((run / "raw/result.json").read_text(encoding="utf-8")).get("duration") or 0)
    shots = [int(e.get("nb_shots_used") or 0) for e in entries]
    names = ["ideal"] + [m["name"] for m in manifest["models"]]
    require(manifest["models"] == [{"name": n, "kind": k, "size": v} for n, k, v in MODELS], "the case's models differ")
    nbr = neighbours(arch)
    settings = []
    totals = dict.fromkeys(names, 0.0)
    for entry, row, sent, used in zip(entries, manifest["settings"], circuit["settings"], shots, strict=True):
        mesh = decode(entry["computed_circuit"])
        require(same_mesh(arch, mesh), f"{run.name}: {row['name']} returned a mesh outside the architecture")
        gap = (
            max((circular_gap(a, b) for a, b in zip(mesh_phases(arch, mesh), sent["phases"], strict=True)), default=0.0)
            if same_mesh(arch, mesh)
            else None
        )
        counts = bscount(entry["results"])
        single = [0] * MODES
        other = 0
        for state, n in counts.items():
            if sum(state) == 1:
                single[state.index(1)] += n
            else:
                other += n
        share = used / sum(shots) if sum(shots) else 0.0
        dark = [r * duration * share for r in rates]
        corrected = [max(c - d, 0.0) for c, d in zip(single, dark, strict=True)]
        low = row["low"]
        n = sum(single)
        block = sum(single[low : low + 4])
        predictions = predict(arch, mesh_phases(arch, mesh), low, nbr)
        likelihoods = {name: round(loglik(single, predictions[name], eta, dark), 6) for name in names}
        for name in names:
            totals[name] += likelihoods[name]
        ideal = predictions["ideal"]
        labels = single[low] + single[low + 1]
        algebra = (
            {
                "a": round(labels / block, 6) if block else None,
                "a_wilson95": wilson(labels, block),
                "a_ideal": round(sum(row["case_ideal"][:2]), 9),
            }
            if "case_ideal" in row
            else {}
        )
        seen = [p * e for p, e in zip(ideal, eta, strict=True)]
        settings.append(
            {
                "name": row["name"],
                "transpiled": gap is None or gap > TRANSPILE_TOLERANCE,
                "max_phase_gap": None if gap is None else round(gap, 12),
                "mesh_sha256": hashlib.sha256(unzip(entry["computed_circuit"]).encode()).hexdigest(),
                "mesh_heater_phase_sum": round(sum(mesh_phases(arch, mesh)), 6),
                "computed_input": entry.get("computed_input"),
                "single_click": single,
                "other_events": other,
                "nb_shots_used": used,
                "in_block": round(block / n, 6) if n else None,
                "in_block_wilson95": wilson(block, n),
                "in_block_dark_corrected": round(sum(corrected[low : low + 4]) / sum(corrected), 6)
                if sum(corrected)
                else None,
                "tvd_from_ideal": round(
                    0.5 * sum(abs(c / sum(corrected) - s / sum(seen)) for c, s in zip(corrected, seen, strict=True)), 6
                )
                if sum(corrected)
                else None,
                "log_likelihood": likelihoods,
                **algebra,
            }
        )
    best = max(names, key=lambda name: totals[name])
    shares = {
        kind: [s["a"] for s, row in zip(settings, manifest["settings"], strict=True) if row["target"].startswith(kind)]
        for kind in ("dark", "bright")
    }
    contrast = (
        {kind: round(sum(v) / len(v), 6) for kind, v in shares.items()}
        if all(v and None not in v for v in shares.values())
        else None
    )
    return {
        "schema": ANALYSIS_SCHEMA,
        "run": run.name,
        "job_id": json.loads((run / "raw/result.json").read_text(encoding="utf-8")).get("job_id"),
        "duration_s": duration,
        "settings": settings,
        "transpiled_iterations": sum(1 for s in settings if s["transpiled"]),
        "log_likelihood_total": {name: round(v, 6) for name, v in totals.items()},
        "best_model": best,
        "a_mean_by_kind": contrast,
    }


def wilson(successes: int, trials: int) -> list[float] | None:
    if not trials:
        return None
    z = 1.959963984540054
    p = successes / trials
    centre = (p + z * z / (2 * trials)) / (1 + z * z / trials)
    half = z * math.sqrt(p * (1 - p) / trials + z * z / (4 * trials * trials)) / (1 + z * z / trials)
    return [round(centre - half, 6), round(centre + half, 6)]


# --- self-test -------------------------------------------------------------------------------


def self_test() -> int:
    import numpy as np

    catalogue = load_catalogue()
    arch = architecture(catalogue)
    require(len(arch) == 1126 and len(mzis(arch)) == 276, "Belenos mesh shape")
    rejected = 0
    try:
        import exqalibur.serialization.circuit_pb2 as pb

        text = unzip(catalogue["processors"][CHIP]["specs"]["architecture"])
        message = pb.Experiment.FromString(base64.b64decode(text[len(":PCVL:Experiment:") :]))
        symbols = []

        def flat(components: Any) -> None:
            for c in components:
                if c.HasField("circuit"):
                    flat(c.circuit.components)
                elif c.HasField("phase_shifter"):
                    symbols.append(c.phase_shifter.phi.symbol)

        flat(message.components)
        require(symbols == [p for k, _, p in arch if k == "ps"], "the wire decoder disagrees with exqalibur")
    except ImportError:
        print("exqalibur absent: decoder cross-check not run")
    try:
        import perceval as pcvl

        phases = [0.37 * k % (2 * math.pi) for k in range(len(phase_slots(arch)))]
        chip = pcvl.Circuit(MODES)
        t = 0
        for kind, m, p in arch:
            if kind == "bs":
                chip.add(m, pcvl.BS(theta=p[0]))
            else:
                chip.add(m, pcvl.PS(phases[t]))
                t += 1
        gap = float(np.max(np.abs(np.array(chip.compute_unitary()) - unitary(arch, phases))))
        require(gap < 1e-12, f"the mesh unitary differs from Perceval's by {gap:.2e}")
    except ImportError:
        print("perceval absent: convention cross-check not run")
    job = CASES / FAMILY / "job-00"
    mutations: list[tuple[str, Any]] = [
        ("coupler angle", lambda c, m: c["architecture"]["couplers"][3].__setitem__(1, 1.5)),
        ("block phase", lambda c, m: _bump(c, "hot-bright-20", block_slot(arch, 20))),
        ("bar phase", lambda c, m: _bump(c, "hot-identity-20", mzis(arch)[0]["ps"][1])),
        ("idle phase", lambda c, m: _bump(c, "cold-identity-20", next(z for z in mzis(arch) if z["m"] < 10)["ps"][0])),
        ("compiled phase", lambda c, m: _bump(c, "compiled-bright-20", 7)),
        ("source digest", lambda c, m: m["settings"][3]["source"].__setitem__("cases_sha256", "0" * 64)),
        ("design distribution", lambda c, m: m["settings"][4]["design_distribution"].__setitem__(21, 0.9)),
    ]
    import shutil
    import tempfile

    with tempfile.TemporaryDirectory() as scratch:
        for name, mutate in mutations:
            target = Path(scratch) / name.replace(" ", "_")
            shutil.copytree(job, target)
            circuit = json.loads((target / "circuit.json").read_text(encoding="utf-8"))
            manifest = json.loads((target / "cases.json").read_text(encoding="utf-8"))
            mutate(circuit, manifest)
            text = json.dumps(circuit, separators=(",", ":")) + "\n"
            manifest["circuit"]["sha256"] = hashlib.sha256(text.encode()).hexdigest()
            (target / "circuit.json").write_text(text, encoding="utf-8")
            (target / "cases.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
            try:
                admit(target, catalogue)
            except MeshError:
                rejected += 1
                continue
            raise SystemExit(f"self-test: the {name} mutation was admitted")
    record = json.loads(RCA.read_text(encoding="utf-8"))
    bad = copy.deepcopy(record)
    bad["hypotheses"]["gain"]["tvd"] = 0.01
    try:
        close(bad, record, "rca")
    except MeshError:
        rejected += 1
    else:
        raise SystemExit("self-test: an altered RCA verdict replayed")
    print(f"self-test: {rejected} mutations rejected")
    return 0


def block_slot(arch: list[Element], low: int) -> int:
    slot: int = block_mzis(arch, low, 4, BLOCK_SIZES[0])[2]["ps"][1]
    return slot


def _bump(circuit: dict[str, Any], name: str, slot: int) -> None:
    (setting,) = [s for s in circuit["settings"] if s["name"] == name]
    setting["phases"][slot] = round((setting["phases"][slot] + 0.3) % (2 * math.pi), 12)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", type=Path)
    group.add_argument("--check", type=Path)
    group.add_argument("--rca", type=Path)
    group.add_argument("--check-rca", type=Path)
    group.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        if args.self_test:
            return self_test()
        if args.write:
            write(args.write)
        elif args.check:
            check(args.check)
        elif args.rca:
            rca(args.rca)
        else:
            check_rca(args.check_rca)
    except MeshError as error:
        raise SystemExit(str(error)) from None
    return 0


if __name__ == "__main__":
    sys.exit(main())
