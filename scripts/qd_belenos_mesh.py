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

--efficiency OUT RUN... writes the reanalysis of one calibration session's
mesh runs with relative per-mode detection efficiencies fitted jointly with
every error class and with the static offsets, each run held out in turn and
no dark term; --check-efficiency OUT RUN... replays it, and
--self-test-efficiency requires an efficiency-only truth to read ideal
without static offsets, efficiencies plus offsets to be declared and
recovered, and a flat truth scored with the receipt's t_out to read "no
class fits". --followup OUT PREREGISTRATION JOB02 REPEAT ORIGINAL reads the
preregistered follow-up: job-02's median in_block against the predicted 5th
percentile under the session's efficiencies and FOLLOWUP_RMS heater offsets
(job specific) and FOLLOWUP_SPARSE_FAIL (sparse targets fail), and the summed
per-setting G^2 homogeneity of a repeated job against its original;
--check-followup replays it. --pair OUT PREREGISTRATION FORM ENSEMBLE JOB02
reads the one-circuit form test (job-08: Q1's case at compilation_seed 1)
and the seed ensemble (job-07: job-02 at seeds 1 and 2); --check-pair
replays it.
--bridge OUT PREREGISTRATION BRIDGE reads the form-mesh bridge (job-09: Q1's
case iterated over compilation seeds) against Q1's one-circuit meshes;
--check-bridge replays it and --self-test-bridge reads every preregistered
branch from synthetic iterations. --dwell OUT PREREGISTRATION D1 D3 LADDER
reads the form-versus-dwell series (job-10, job-11, job-12); --check-dwell
replays it and --self-test-dwell reads its branches on synthetic results.

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
ANALYSIS_TOLERANCE = 1e-6
TIE_NATS = 1e-6
TRANSPILE_TOLERANCE = 1e-9
LIKELIHOOD_FLOOR = 1e-6
SCAN_SIGMAS = tuple(round(0.05 * k, 2) for k in range(17))
SCAN_GAINS = tuple(round(-0.6 + 0.05 * k, 2) for k in range(25))
SCAN_CROSSTALK = tuple(round(-0.2 + 0.02 * k, 2) for k in range(21))
SCAN_FRACTIONS = tuple(round(0.1 * k, 1) for k in range(11))
MISROUTE_OFFSETS = (-4, -2, 2)
FIT_P_MIN = 1e-3
POOL_MIN = 5.0
STATIC_FOLDS = 4
STATIC_TAUS = (0.1, 0.3)
STATIC_GAIN_MIN = 10.0
STATIC_SCHEMA = "qd-belenos-static-offsets-v1"
STATIC_REPLAY_TOLERANCE = 1e-3
# L-BFGS stops short of a unique optimum on a 574-offset fit the data do not identify, so its endpoint follows the
# BLAS build: the C1 session's held-out gains differ by up to 3.2 % between AOCL and OpenBLAS, the efficiency
# record's by 0.4 %. Optimizer endpoints replay within this relative bound; deterministic fields stay exact.
STATIC_FIT_REPLAY_TOLERANCE = 0.1
EFFICIENCY_SCHEMA = "qd-belenos-mesh-efficiency-v1"
EFFICIENCY_SWEEPS = 5000
EFFICIENCY_TOLERANCE = 1e-10
EFFICIENCY_STATIC_ITERATIONS = 600
FOLLOWUP_SCHEMA = "qd-belenos-followup-v1"
FOLLOWUP_RMS = 0.08
FOLLOWUP_DRAWS = 200
# followup-preregistration.json fixes the offset draws to the stream [SEED, 21].
FOLLOWUP_STREAM = 21
FOLLOWUP_SPARSE_FAIL = 0.65
PAIR_SCHEMA = "qd-belenos-form-ensemble-v1"
BRIDGE_SCHEMA = "qd-belenos-form-mesh-bridge-v1"
DWELL_SCHEMA = "qd-belenos-form-dwell-v1"
FIT_TVD_RATIO = 3.0
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
SEED = 20261017
# (name, kind, magnitude); a noise kind is the exact ensemble of `channel`, and a source
# model sends the photon into the input mode magnitude away, a demultiplexer misroute.
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
S3_RUN = "2026-10-17T232626Z-sim_belenos-belenos_mesh-job-00"
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
CAMPAIGN_JOBS = (3, 4, 5, 6)
# job-07 repeats job-02's settings at these compilation seeds; job-08 sends Q1's case as one circuit at FORM_SEED.
ENSEMBLE_JOB = "job-07"
ENSEMBLE_SEEDS = (1, 2)
FORM_JOB = "job-08"
FORM_SEED = 1
FORM_SOURCE = "box_kite_photonic_single/job-04"
# job-09 sends Q1's case iterated over BRIDGE_SEEDS, 1500 samples each, so Q1's one-circuit meshes can recur in
# the iterated form (29dc6ef8 at seed 20, e296b6a9 at seed 1); seeds 0 and 1 open and close the job, and each
# repeated seed bounds drift within the job.
BRIDGE_JOB = "job-09"
BRIDGE_SEEDS = (*range(22), 0, 1)
BRIDGE_SAMPLES = 1500
BRIDGE_SHOTS = 3000
# The form-versus-dwell series: D1 (job-10) is Q1's single job at dwell 1500, D3 (job-11) Q1's single job at an
# ANU-drawn seed, and job-12 carries D2 (dwell ladder at seed 20, Q1's mesh in the iterated form) and D4 (the
# ANU seed's ladder) as iterations of one job. Every iteration keeps two shots per sample, Q1's ratio.
DWELL_D1_JOB, DWELL_D3_JOB, DWELL_LADDER_JOB = "job-10", "job-11", "job-12"
DWELL_D1_SAMPLES = 1500
ANU_DRAWS = ROOT / "docs/evidence/anu_qrng"
DWELL_ANU = {"draw": "draw-2026-10-18T083548Z.json", "index": 0, "use": "D3 and D4 fresh mesh"}
DWELL_D2_LADDER = (1500, 10000, 1500, 40000, 1500, 60000)
DWELL_D4_LADDER = (1500, 10000, 40000)
DWELL_Q1_SEED = 20
# job-13 is Q1's single job at seed 20, the seed that serves Q1's mesh 29dc6ef8 in the iterated form: every
# unseeded single job on 29dc6ef8 lost light inside the photon's cone and every seeded cell kept it, so a
# seeded single job at Q1's budget on Q1's mesh separates the unseeded path from form and budget.
SEEDED_SINGLE_JOB = "job-13"
# job-14 to job-16 hold Q1's circuit at seed 20 and 10000 samples per entry and change only the payload class:
# a ComputationIterator with one entry (job-14), a single Computation (job-15, job-13 again as the time
# control) and an iterator with two entries (job-16), so the single-path failure on 29dc6ef8 is read against the
# wrapper with the budget, seed and mesh held.
WRAPPER_ITERATOR_JOB, WRAPPER_SINGLE_JOB, WRAPPER_PAIR_JOB = "job-14", "job-15", "job-16"
WRAPPER_SAMPLES = 10000
CONNECTED = (0, 2, 4, 6, 8, 9, 12, 13, 16, 18, 20, 22)

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


def run_architecture(mesh: list[Element]) -> list[Element]:
    """The architecture a returned mesh was compiled on: its topology and couplers, its phases as symbols.

    A computed_circuit carries the couplers of the calibration it ran under, so a retained run replays
    against its own chip rather than against a catalogue refreshed after a recalibration.
    """
    out: list[Element] = []
    t = 0
    for kind, m, p in mesh:
        if kind == "bs":
            out.append((kind, m, p))
        else:
            out.append(("ps", m, f"phi{t}"))
            t += 1
    return out


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


def channel(arch: list[Element], phases: list[float], source: int, sigma: float = 0.0, sigma_theta: float = 0.0) -> Any:
    """Exact one-photon detection probabilities under independent Gaussian heater and coupler noise.

    The photon's 24 x 24 density matrix crosses the mesh. A phase shifter on
    mode q with noise N(0, sigma^2) multiplies every coherence rho_qk (k != q)
    by e^{i phi} e^{-sigma^2 / 2}; a coupler B = c I + i s X with angle noise
    N(0, sigma_theta^2) maps the pair block M to E[c^2] M + E[s^2] X M X +
    i E[cs] (X M - M X) and the pair-to-rest blocks by E[B], with
    E[c^2] = (1 + cos(theta) e^{-st^2/2}) / 2, E[cs] = sin(theta) e^{-st^2/2} / 2
    and E[c] = cos(theta / 2) e^{-st^2/8}. sigma = sigma_theta = 0 is the
    unitary propagation of `propagate`.
    """
    import numpy as np

    rho = np.zeros((MODES, MODES), dtype=complex)
    rho[source, source] = 1
    damp = math.exp(-(sigma**2) / 2)
    t = 0
    x = np.array([[0, 1], [1, 0]], dtype=complex)
    for kind, m, p in arch:
        if kind == "bs":
            theta = p[0]
            fade = math.exp(-(sigma_theta**2) / 2)
            ec2, es2 = (1 + math.cos(theta) * fade) / 2, (1 - math.cos(theta) * fade) / 2
            ecs = math.sin(theta) * fade / 2
            fade8 = math.exp(-(sigma_theta**2) / 8)
            mean = np.array(
                [[math.cos(theta / 2), 1j * math.sin(theta / 2)], [1j * math.sin(theta / 2), math.cos(theta / 2)]]
            )
            mean = mean * fade8
            pair = slice(m, m + 2)
            block = rho[pair, pair].copy()
            rest = [k for k in range(MODES) if k not in (m, m + 1)]
            rho[pair, rest] = mean @ rho[pair, rest]
            rho[rest, pair] = rho[rest, pair] @ mean.conj().T
            rho[pair, pair] = ec2 * block + es2 * (x @ block @ x) + 1j * ecs * (x @ block - block @ x)
        else:
            phase = np.exp(1j * phases[t]) * damp
            t += 1
            diag = rho[m, m]
            rho[m, :] *= phase
            rho[:, m] *= np.conj(phase)
            rho[m, m] = diag
    return np.real(np.diag(rho)).clip(0)


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
    """Per-mode detection probability of each error model; the noise kinds are exact ensembles (`channel`)."""
    import numpy as np

    phi = np.asarray(phases) % (2 * math.pi)
    out: dict[str, list[float]] = {"ideal": propagate(arch, list(phi), source)[0].tolist()}
    for name, kind, size in MODELS:
        if kind == "phase_noise":
            p = channel(arch, list(phi), source, sigma=size)
        elif kind == "theta_noise":
            p = channel(arch, list(phi), source, sigma_theta=size)
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


def plan_characterization_settings(job: int) -> list[dict[str, Any]]:
    """One job of the C1 campaign: 16 seeded uniform-random meshes, inputs rotating over the connected modes.

    Uniform phases are the transpiler's own statistics, so each setting's occupied column is a random
    column that spreads the photon over the chip; four such jobs identify shared static offsets.
    """
    start = (job - CAMPAIGN_JOBS[0]) * 16
    return [
        {
            "name": f"random-{job:02d}-{k:02d}",
            "mesh": "random",
            "target": "random",
            "low": CONNECTED[(start + k) % len(CONNECTED)],
            "seed": [SEED, 303, job, k],
        }
        for k in range(16)
    ]


def random_phases(seed: list[int], count: int) -> list[float]:
    import numpy as np

    return [round(float(v), 12) for v in np.random.default_rng(seed).uniform(0, 2 * math.pi, count)]


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
        if plan["mesh"] == "random":
            setting["seed"] = plan["seed"]
            setting["phases"] = random_phases(plan["seed"], len(phase_slots(arch)))
            setting["frame_out"] = setting["frame_in"] = None
        elif plan["mesh"] == "compiled":
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
        if plan["target"] not in ("identity", "random"):
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
    if setting["target"] not in ("identity", "random"):
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
    arch: list[Element],
    settings: list[dict[str, Any]],
    catalogue_sha: str,
    job: str,
    coverage: Any = None,
    preregistered: dict[str, str] | None = None,
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
            {
                "name": s["name"],
                "input_mode": s["low"],
                "phases": [round(v, 12) for v in s["phases"]],
                **({"compilation_seed": s["compilation_seed"]} if "compilation_seed" in s else {}),
            }
            for s in settings
        ],
    }
    circuit_text = json.dumps(circuit, separators=(",", ":")) + "\n"
    rows = []
    for s, f in zip(settings, facts, strict=True):
        row = {k: s[k] for k in ("name", "mesh", "target", "low")}
        for key in ("source", "source_run", "seed", "compilation_seed", "block_mzis", "frame_out", "frame_in"):
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
        "seed": SEED,
        "settings": rows,
        **({"coverage": coverage} if coverage is not None else {}),
        "preregistered": preregistered
        or {
            "transpilation": "the service re-transpiles every iteration, so each model's prediction is computed "
            "on the computed_circuit the iteration returns; the same body compiles to the same meshes on "
            "sim:belenos and qpu:belenos while the couplers are unchanged",
            "classes": "phase noise, coupler noise, heater gain, thermal crosstalk, a phase ceiling and a "
            "demultiplexer misroute (source models) each predict a different histogram per returned mesh",
            "decision": "each class's magnitude scan (exact dephasing channel, heater gain, thermal "
            "crosstalk, misroute plus noise) is scored by efficiency-weighted multinomial likelihood on the "
            "returned meshes; the best class fits only when the chi-square p-value of its deviance, with "
            "bins expected below 5 counts pooled into one rest bin floored at one count once it saw a click, "
            "is at least 0.001 at its degrees of freedom and the median ratio of setting TVD to its "
            "shot-noise floor is at most 3, and otherwise the job reads 'no class fits'; a best point at "
            "every class's null magnitude reads 'ideal'; static heater offsets (static.json) are declared "
            "when one shared offset vector, fitted by MAP on three folds of settings, beats the dephasing "
            "channel fitted on the same folds by more than 10 nats on the fourth and its held-out median TVD "
            "stays within 3 shot-noise floors; a misroute is read from the source models on the returned "
            "meshes, whose unused columns are transpiler draws",
        },
    }
    return json.dumps(manifest, indent=1) + "\n", circuit_text


def write(directory: Path) -> None:
    catalogue = load_catalogue()
    arch = architecture(catalogue)
    settings = realize(arch, plan_settings())
    write_job(directory, arch, "job-00", settings)
    write_job(directory, arch, "job-01", [s for s in settings if s["name"] == SINGLE_SETTING])
    zero_divisor = realize(arch, plan_zero_divisor_settings())
    write_job(directory, arch, "job-02", zero_divisor, edge_coverage())
    for job in CAMPAIGN_JOBS:
        write_job(directory, arch, f"job-{job:02d}", realize(arch, plan_characterization_settings(job)))
    write_job(directory, arch, ENSEMBLE_JOB, ensemble_settings(zero_divisor), None, ENSEMBLE_PREREGISTERED)
    write_seeded(directory)


ENSEMBLE_PREREGISTERED = {
    "transpilation": "every iteration names its compilation_seed: job-02's sixteen configurations at seeds 1 and "
    "2, the two seeds of a configuration adjacent; each prediction is computed on the computed_circuit the "
    "iteration returns, and the QPU need not return the simulator's meshes for an iterated body",
    "decision": "per configuration and seed the algebra share a and in_block with Wilson intervals; the "
    "bright-minus-dark contrast of a over all 32 iterations; compilation_seed selects the served mesh when "
    "the two seeds of every configuration return different meshes; the spread between seeds 0 (job-02), 1 "
    "and 2 is reported per configuration; the class scans and fit test are those of job-02",
}
FORM_PREREGISTERED = {
    "transpilation": "Q1's case sent as one circuit with compilation_seed 1, the only change against Q1's body "
    "besides its job name and Perceval's process_id",
    "decision": "a returned mesh other than Q1's (29dc6ef8) with in_block at most 0.65 reads 'one-circuit form', "
    "at least 0.90 reads 'Q1 mesh', between reads 'intermediate'; Q1's mesh again reads 'seed ignored'",
}


BRIDGE_PREREGISTERED = {
    "transpilation": "Q1's case sent unchanged as 24 iterations of 1500 samples at compilation seeds 0 to 21, then "
    "0 and 1 again; the per-iteration seed is the only parameter an iteration sets, and each iteration's mesh is "
    "the sha256 of its unzipped computed_circuit, the identity under which Q1 returned 29dc6ef8",
    "decision": "bridge-preregistration.json in the session directory holds the branches and thresholds; a "
    "'form' reading on Q1's mesh confounds the one-circuit job form with its 10000-sample dwell per setting "
    "against 1500 here, and reads 'form or dwell'",
}


def ensemble_settings(zero_divisor: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """job-02's realized settings at each of ENSEMBLE_SEEDS, the seeds of one configuration adjacent."""
    return [
        {**s, "name": f"{s['name']}-s{seed}", "compilation_seed": seed} for s in zero_divisor for seed in ENSEMBLE_SEEDS
    ]


def seeded_manifest(source: dict[str, Any], source_sha: str) -> dict[str, Any]:
    """The one-circuit form case: the source case's manifest with only its name, seed and preregistration changed."""
    return {
        **source,
        "family": FAMILY,
        "job": FORM_JOB,
        "compilation_seed": FORM_SEED,
        "seeded_from": {"case": FORM_SOURCE, "cases_sha256": source_sha},
        "preregistered": FORM_PREREGISTERED,
    }


def bridge_manifest(source: dict[str, Any], source_sha: str) -> dict[str, Any]:
    """The bridge case: the source case iterated over BRIDGE_SEEDS, one compilation seed per iteration.

    Only the job name, the iteration count, the per-iteration budgets, the seed list and the preregistration
    differ from the source; the circuit is the source's numeric unitary, so every iteration sends one program.
    """
    return {
        **source,
        "family": FAMILY,
        "job": BRIDGE_JOB,
        "iterations": len(BRIDGE_SEEDS),
        "max_samples": BRIDGE_SAMPLES * len(BRIDGE_SEEDS),
        "max_shots": BRIDGE_SHOTS * len(BRIDGE_SEEDS),
        "settings": [{"name": f"q1-{k:02d}-s{seed}", "compilation_seed": seed} for k, seed in enumerate(BRIDGE_SEEDS)],
        "seeded_from": {"case": FORM_SOURCE, "cases_sha256": source_sha},
        "preregistered": BRIDGE_PREREGISTERED,
    }


DWELL_PREREGISTERED = {
    "series": "form versus dwell on Q1's circuit (strategy.md section 7 item 10); dwell-preregistration.json in "
    "the session directory holds the thresholds and branches",
}
SEEDED_SINGLE_PREREGISTERED = {
    "series": "seeded single job on Q1's mesh (strategy.md section 7 item 12)",
    "statistic": "in_block over one-click samples inside source 20's light cone of the served mesh "
    "(scripts/qd_belenos_cone.py)",
    "void_unless_mesh_sha256_prefix": "29dc6ef8",
    "unseeded_path_at_least": 0.95,
    "single_job_budget_at_most": 0.65,
    "readings": "at least 0.95: the leak follows the unseeded single-job path; at most 0.65: the leak needs the "
    "single-job form at Q1's budget on 29dc6ef8 whatever the seed; between: intermediate, no attribution",
}


def anu_seed(spec: dict[str, Any]) -> dict[str, Any]:
    """The retained ANU draw value a case takes as its compilation seed, with the draw's identity."""
    record = json.loads((ANU_DRAWS / spec["draw"]).read_text(encoding="utf-8"))
    return {**spec, "raw_sha256": record["raw_sha256"], "value": record["values"][spec["index"]]}


def dwell_d1_manifest(source: dict[str, Any], source_sha: str) -> dict[str, Any]:
    """D1: Q1's single job unchanged but for its dwell, unseeded so the service serves Q1's mesh again."""
    return {
        **source,
        "family": FAMILY,
        "job": DWELL_D1_JOB,
        "max_samples": DWELL_D1_SAMPLES,
        "max_shots": 2 * DWELL_D1_SAMPLES,
        "seeded_from": {"case": FORM_SOURCE, "cases_sha256": source_sha},
        "preregistered": DWELL_PREREGISTERED,
    }


def dwell_d3_manifest(source: dict[str, Any], source_sha: str) -> dict[str, Any]:
    """D3: Q1's single job unchanged but for a compilation seed drawn from the ANU QRNG."""
    seed = anu_seed(DWELL_ANU)
    return {
        **source,
        "family": FAMILY,
        "job": DWELL_D3_JOB,
        "compilation_seed": seed["value"],
        "seed_source": seed,
        "seeded_from": {"case": FORM_SOURCE, "cases_sha256": source_sha},
        "preregistered": DWELL_PREREGISTERED,
    }


def dwell_ladder_manifest(source: dict[str, Any], source_sha: str) -> dict[str, Any]:
    """D2 and D4: Q1's circuit iterated over two dwell ladders, at seed 20 (Q1's mesh) and at D3's ANU seed."""
    seed = anu_seed(DWELL_ANU)
    rows = [("d2", DWELL_Q1_SEED, n) for n in DWELL_D2_LADDER] + [("d4", seed["value"], n) for n in DWELL_D4_LADDER]
    settings = [
        {"name": f"{tag}-{k:02d}-s{value}-n{n}", "compilation_seed": value, "max_samples": n, "max_shots": 2 * n}
        for k, (tag, value, n) in enumerate(rows)
    ]
    return {
        **source,
        "family": FAMILY,
        "job": DWELL_LADDER_JOB,
        "iterations": len(settings),
        "max_samples": sum(s["max_samples"] for s in settings),
        "max_shots": sum(s["max_shots"] for s in settings),
        "settings": settings,
        "seed_source": seed,
        "seeded_from": {"case": FORM_SOURCE, "cases_sha256": source_sha},
        "preregistered": DWELL_PREREGISTERED,
    }


def seeded_single_manifest(source: dict[str, Any], source_sha: str) -> dict[str, Any]:
    """Q1's single job unchanged but for compilation seed 20, the seed serving Q1's mesh 29dc6ef8."""
    return {
        **source,
        "family": FAMILY,
        "job": SEEDED_SINGLE_JOB,
        "compilation_seed": DWELL_Q1_SEED,
        "seeded_from": {"case": FORM_SOURCE, "cases_sha256": source_sha},
        "preregistered": SEEDED_SINGLE_PREREGISTERED,
    }


WRAPPER_PREREGISTERED = {
    "series": "single computation versus iterator payload on Q1's mesh (strategy.md section 7 item 13)",
    "statistic": "tvd_cone_from_ideal per entry: total variation of the one-click histogram inside source 20's "
    "noise-bounded light cone from the served mesh's ideal propagation (scripts/qd_belenos_cone.py)",
    "void_unless_mesh_sha256_prefix": "29dc6ef8",
    "pass_at_most": 0.2,
    "fail_at_least": 0.5,
    "payload_entries": {WRAPPER_ITERATOR_JOB: 1, WRAPPER_SINGLE_JOB: 0, WRAPPER_PAIR_JOB: 2},
    "order": "job-14 runs first; job-15 follows a job-14 pass and job-16 a job-14 fail; a void or intermediate "
    "job-14 ends the series",
    "readings": "job-14 pass, job-15 fail: the failure follows the single-computation payload class; job-14 pass, "
    "job-15 pass: no single-path failure in this block, the payload class is not isolated; job-14 fail, job-16 "
    "fail then pass: the first 10000-sample entry of a job fails whatever its wrapper; job-14 fail, job-16 pass "
    "twice: one entry fails as a single computation does, two entries hold; job-14 fail, job-16 fail twice: "
    "10000-sample entries fail without D2's leading 1500-sample entry; any other pattern, a void entry (other "
    "mesh, or a result whose results_list length differs from payload_entries) or an intermediate entry: no "
    "attribution",
}


def wrapper_iterator_manifest(source: dict[str, Any], source_sha: str) -> dict[str, Any]:
    """Arm B: Q1's case as a ComputationIterator holding one entry at seed 20 and 10000 samples."""
    return {
        **source,
        "family": FAMILY,
        "job": WRAPPER_ITERATOR_JOB,
        "iterator": True,
        "iterations": 1,
        "max_samples": WRAPPER_SAMPLES,
        "max_shots": 2 * WRAPPER_SAMPLES,
        "settings": [{"name": f"b-s{DWELL_Q1_SEED}-n{WRAPPER_SAMPLES}", "compilation_seed": DWELL_Q1_SEED}],
        "seeded_from": {"case": FORM_SOURCE, "cases_sha256": source_sha},
        "preregistered": WRAPPER_PREREGISTERED,
    }


def wrapper_single_manifest(source: dict[str, Any], source_sha: str) -> dict[str, Any]:
    """Arm A: job-13's single computation again, the time control of a job-14 pass."""
    return {
        **seeded_single_manifest(source, source_sha),
        "job": WRAPPER_SINGLE_JOB,
        "preregistered": WRAPPER_PREREGISTERED,
    }


# The pair's two seed-20 entries open job-16 unchanged; PAIR_EXTENSION_BLOCKS blocks of (14a96ca6, 29dc6ef8) at
# 10000 samples follow, so every later seed-20 entry is the first acquisition of 29dc6ef8 after a mesh load and
# every 14a96ca6 entry is a reference read in the same job. Each entry costs about 7 s of the 300 s limit whatever
# its budget, and the shot cap of 2 x samples prices the job at 1 + 480000e-6 credits.
PAIR_EXTENSION_BLOCKS = 11
PAIR_EXTENSION_PREREGISTERED = {
    "question": "does a 10000-sample 29dc6ef8 entry fail when it is the first acquisition of that mesh after a "
    "load of 14a96ca6, and does 14a96ca6 hold in the same job",
    "first_entry": 2,
    "blocks": PAIR_EXTENSION_BLOCKS,
    "expected_mesh_sha256_prefix": {str(DWELL_Q1_SEED): "29dc6ef8", "46667": "14a96ca6"},
    "pass_at_most": 0.2,
    "fail_at_least": 0.5,
    "reload_fails_at_least_share": 0.8,
    "minimum_read_entries": 9,
    "order": "results_list order is taken as execution order; no result entry carries a timestamp",
    "readings": "any 14a96ca6 entry failing: the fault reaches beyond 29dc6ef8 in this job, mesh specificity is "
    "not supported; otherwise, of the post-load 29dc6ef8 entries that read pass or fail (at least 9 needed, "
    "else inconclusive), at least 0.8 failing: a large 29dc6ef8 acquisition fails after a mesh load; none "
    "failing: post-load acquisitions hold; between: intermittent, reported as a share with its Wilson "
    "interval. Each is read beside the pair's two entries: a passing first entry implicates the job's entry "
    "count or path, a passing second entry with failing post-load entries implicates the load, a failing "
    "second entry with holding post-load entries implicates repetition of the job's first mesh.",
}


def wrapper_pair_manifest(source: dict[str, Any], source_sha: str) -> dict[str, Any]:
    """Arm C: Q1's case as two identical iterator entries at seed 20 and 10000 samples each, then the
    extension's alternating reference and post-load entries."""
    seed = anu_seed(DWELL_ANU)
    rows = [("c", DWELL_Q1_SEED)] * 2 + [("r", seed["value"]), ("t", DWELL_Q1_SEED)] * PAIR_EXTENSION_BLOCKS
    settings = [
        {"name": f"{tag}{k}-s{value}-n{WRAPPER_SAMPLES}", "compilation_seed": value}
        for k, (tag, value) in enumerate(rows)
    ]
    return {
        **source,
        "family": FAMILY,
        "job": WRAPPER_PAIR_JOB,
        "iterations": len(settings),
        "max_samples": len(settings) * WRAPPER_SAMPLES,
        "max_shots": 2 * len(settings) * WRAPPER_SAMPLES,
        "settings": settings,
        "seed_source": seed,
        "seeded_from": {"case": FORM_SOURCE, "cases_sha256": source_sha},
        "preregistered": WRAPPER_PREREGISTERED,
        "extension_preregistered": PAIR_EXTENSION_PREREGISTERED,
    }


SEEDED_JOBS = {
    FORM_JOB: seeded_manifest,
    BRIDGE_JOB: bridge_manifest,
    DWELL_D1_JOB: dwell_d1_manifest,
    DWELL_D3_JOB: dwell_d3_manifest,
    DWELL_LADDER_JOB: dwell_ladder_manifest,
    SEEDED_SINGLE_JOB: seeded_single_manifest,
    WRAPPER_ITERATOR_JOB: wrapper_iterator_manifest,
    WRAPPER_SINGLE_JOB: wrapper_single_manifest,
    WRAPPER_PAIR_JOB: wrapper_pair_manifest,
}


def write_seeded(directory: Path) -> None:
    source = directory / FORM_SOURCE
    for name, build in SEEDED_JOBS.items():
        manifest = build(json.loads((source / "cases.json").read_text(encoding="utf-8")), sha256(source / "cases.json"))
        job = directory / FAMILY / name
        job.mkdir(parents=True, exist_ok=True)
        (job / "circuit.json").write_bytes((source / "circuit.json").read_bytes())
        (job / "cases.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
        seeds = [s["compilation_seed"] for s in manifest.get("settings", [])] or [manifest.get("compilation_seed")]
        print(f"{job}: {FORM_SOURCE} at compilation seeds {seeds}, {manifest['max_samples']} samples")


def admit_seeded(job: Path) -> None:
    """A seeded case equals its source case byte for byte in its circuit and field for field elsewhere."""
    manifest = json.loads((job / "cases.json").read_text(encoding="utf-8"))
    source = CASES / manifest["seeded_from"]["case"]
    require(manifest["seeded_from"]["case"] == FORM_SOURCE, f"{job.name}: source case {manifest['seeded_from']}")
    require(sha256(source / "cases.json") == manifest["seeded_from"]["cases_sha256"], f"{job.name}: source digest")
    require((job / "circuit.json").read_bytes() == (source / "circuit.json").read_bytes(), f"{job.name}: circuit bytes")
    require(manifest.get("job") in SEEDED_JOBS, f"{job.name}: {manifest.get('job')!r} is no seeded case")
    expected = SEEDED_JOBS[manifest["job"]](
        json.loads((source / "cases.json").read_text(encoding="utf-8")), sha256(source / "cases.json")
    )
    require(
        manifest == expected, f"{job.name}: manifest differs from its source beyond name, seeds and preregistration"
    )
    if "seed_source" in manifest:
        import anu_qrng

        draw = manifest["seed_source"]
        record = json.loads((ANU_DRAWS / draw["draw"]).read_text(encoding="utf-8"))
        try:
            anu_qrng.admit(record)
        except anu_qrng.DrawError as error:
            raise MeshError(f"{job.name}: ANU draw {draw['draw']}: {error}") from None
        require(record["values"][draw["index"]] == draw["value"], f"{job.name}: ANU value differs from its draw")


def write_job(
    directory: Path,
    arch: list[Element],
    name: str,
    settings: list[dict[str, Any]],
    coverage: Any = None,
    preregistered: dict[str, str] | None = None,
) -> None:
    """One case directory; a one-setting job sends its phases as numbers, the guide's pre-compiled form."""
    manifest, circuit = documents(arch, settings, sha256(CATALOGUE), name, coverage, preregistered)
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


def close_relative(a: Any, b: Any, path: str = "") -> None:
    """Recursive equality with floats within ANALYSIS_TOLERANCE relative (at least that absolute).

    A mesh analysis sums likelihoods over 24 x 24 complex products whose last bits differ between BLAS
    builds, so its replay compares numbers to a tolerance and every string, flag and integer exactly.
    """
    if isinstance(a, float) or isinstance(b, float):
        require(isinstance(a, int | float) and isinstance(b, int | float), f"{path}: {a!r} against {b!r}")
        require(abs(a - b) <= ANALYSIS_TOLERANCE * max(1.0, abs(b)), f"{path}: {a!r} differs from {b!r}")
    elif isinstance(a, dict):
        require(isinstance(b, dict) and set(a) == set(b), f"{path}: keys differ")
        for key in a:
            close_relative(a[key], b[key], f"{path}.{key}")
    elif isinstance(a, list):
        require(isinstance(b, list) and len(a) == len(b), f"{path}: lengths differ")
        for i, (x, y) in enumerate(zip(a, b, strict=True)):
            close_relative(x, y, f"{path}[{i}]")
    else:
        require(a == b, f"{path}: {a!r} differs from {b!r}")


def admit(job: Path, catalogue: dict[str, Any] | None = None) -> None:
    """Recompute every derived number of a mesh case from its retained phases, architecture and sources."""
    catalogue = load_catalogue() if catalogue is None else catalogue
    arch = architecture(catalogue)
    manifest = json.loads((job / "cases.json").read_text(encoding="utf-8"))
    if "seeded_from" in manifest:
        admit_seeded(job)
        return
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
        require(row.get("compilation_seed") == sent.get("compilation_seed"), f"{row['name']}: compilation seed")
        require(len(sent["phases"]) == len(spec["symbols"]), f"{row['name']}: phase count")
        setting = {**row, "phases": sent["phases"]}
        if row["mesh"] == "random":
            require(sent["phases"] == random_phases(row["seed"], len(spec["symbols"])), f"{row['name']}: seeded phases")
        elif row["mesh"] == "compiled":
            run = RUNS / row["source_run"]["run"]
            require(sha256(run / "raw/result.json") == row["source_run"]["result_sha256"], f"{row['name']}: source run")
            (text,) = computed_circuits(run)
            close(mesh_phases(arch, decode(text)), sent["phases"], f"{row['name']}.phases")
        else:
            check_baseline(arch, row, sent["phases"])
        if row["target"] not in ("identity", "random"):
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
        [p.name for p in jobs]
        == ["job-00", "job-01", "job-02"]
        + [f"job-{j:02d}" for j in CAMPAIGN_JOBS]
        + [ENSEMBLE_JOB, FORM_JOB, BRIDGE_JOB, DWELL_D1_JOB, DWELL_D3_JOB, DWELL_LADDER_JOB, SEEDED_SINGLE_JOB]
        + [WRAPPER_ITERATOR_JOB, WRAPPER_SINGLE_JOB, WRAPPER_PAIR_JOB],
        f"{directory / FAMILY} holds {[p.name for p in jobs]}",
    )
    uses: dict[tuple[str, int], set[str]] = {}
    for job in jobs:
        admit(job)
        source = json.loads((job / "cases.json").read_text(encoding="utf-8")).get("seed_source")
        if source is not None:
            uses.setdefault((source["draw"], source["index"]), set()).add(source["use"])
        print(f"{job}: mesh case admitted")
    # One ANU value names one fresh mesh: cases that share it declare one use, the pairing they share.
    require(all(len(u) == 1 for u in uses.values()), f"an ANU value serves more than one use: {uses}")
    manifest = json.loads((directory / FAMILY / "job-02" / "cases.json").read_text(encoding="utf-8"))
    coverage = edge_coverage()
    require(manifest.get("coverage") == coverage, "job-02 coverage differs from the census")
    require(
        [r["target"] for r in manifest["settings"]] == list(coverage["uses"]),
        "job-02 settings differ from its coverage",
    )
    circuit = json.loads((directory / FAMILY / "job-02" / "circuit.json").read_text(encoding="utf-8"))
    ensemble = json.loads((directory / FAMILY / ENSEMBLE_JOB / "circuit.json").read_text(encoding="utf-8"))
    require(
        [(s["name"], s["input_mode"], s["phases"]) for s in ensemble["settings"]]
        == [
            (f"{s['name']}-s{seed}", s["input_mode"], s["phases"])
            for s in circuit["settings"]
            for seed in ENSEMBLE_SEEDS
        ]
        and [s["compilation_seed"] for s in ensemble["settings"]] == list(ENSEMBLE_SEEDS) * len(circuit["settings"]),
        f"{ENSEMBLE_JOB} is not job-02 at seeds {ENSEMBLE_SEEDS}",
    )
    products = f"{coverage['dark_products']} zero products, {coverage['bright_products']} controls"
    print(f"job-02 covers {coverage['edges']} edges: {products}")


# --- leakage root-cause record ---------------------------------------------------------------


def observed(run: Path) -> tuple[Any, dict[str, Any]]:
    """Dark-subtracted one-click distribution of a one-photon run and its raw facts."""
    import numpy as np
    from qd_box_kite_analysis import acquisition_seconds

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
    seconds = acquisition_seconds(int(single.sum() + multi), inner.get("physical_perf"), perfs.get("Clock (MHz)"))
    if seconds is None:
        raise MeshError(f"{run.name}: no physical_perf or clock to time the acquisition")
    dark = np.array(perfs["Dark counts (detection/s)"], dtype=float) * seconds
    corrected = np.clip(single - dark, 0, None)
    eta = np.array(perfs["Transmission per mode (%)"]["t_out"], dtype=float)
    facts = {
        "single_click": [int(v) for v in single],
        "other_events": multi,
        "duration_s": duration,
        "acquisition_s_estimate": round(float(seconds), 6),
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


def rca_record(sources: list[int] | None = None) -> dict[str, Any]:
    """The leakage root-cause record of the qpu:belenos bright block, on the couplers its own mesh carries.

    sources lists the connected input modes the wrong-source hypothesis tries; the retained record's own
    list replays it, so a refreshed catalogue changes nothing a retained run determines.
    """
    import numpy as np

    run = RUNS / Q1_RUN
    (text,) = computed_circuits(run)
    arch = run_architecture(decode(text))
    if sources is None:
        sources = load_catalogue()["processors"][CHIP]["specs"]["connected_input_modes"]
    obs, extra = observed(run)
    eta = extra["eta"]

    def seen(p: Any) -> Any:
        weighted = np.asarray(p) * eta
        return weighted / weighted.sum()

    compiled = mesh_phases(arch, decode(text))
    u = unitary(arch, compiled)
    columns = np.abs(u) ** 2
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

    noise = {f"{sigma}": tvd(seen(channel(arch, compiled, 20, sigma=sigma)), obs) for sigma in (0.2, 0.3, 0.4, 0.5)}
    variants = {
        "U": columns[:, 20],
        "U^T": np.abs(u.T[:, 20]) ** 2,
        "mirrored modes": np.abs(unitary(_mirror(arch), compiled)[:, 20]) ** 2,
    }
    return {
        "schema": RCA_SCHEMA,
        "run": Q1_RUN,
        "result_sha256": sha256(run / "raw/result.json"),
        "observed": {**extra["facts"], "dark_subtracted_distribution": [round(float(v), 6) for v in obs]},
        "compiled_mesh": {
            "column_20": [round(float(v), 6) for v in columns[:, 20]],
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
    sources = [int(k) for k in retained["hypotheses"]["single_wrong_source"]]
    close(retained, rca_record(sources), "rca")
    print(f"{path}: replays")


# --- run analysis (standard library) ----------------------------------------------------------


def circular_gap(a: float, b: float) -> float:
    d = (a - b) % (2 * math.pi)
    return min(d, 2 * math.pi - d)


def loglik(counts: list[int], model: list[float], eta: list[float], dark: list[float]) -> float:
    """Multinomial log-likelihood of one-click counts under lambda_m = A p_m eta_m + d_m with sum lambda = N."""
    return sum(c * math.log(r) for c, r in zip(counts, rates(counts, model, eta, dark), strict=True) if c)


def rates(counts: list[int], model: list[float], eta: list[float], dark: list[float]) -> list[float]:
    """Per-mode detection probabilities: efficiency-weighted model light plus dark clicks, floored and normalized."""
    n = sum(counts)
    weighted = [p * e for p, e in zip(model, eta, strict=True)]
    scale = max(n - sum(dark), 0.0) / max(sum(weighted), 1e-300)
    raw = [max(scale * w + d, LIKELIHOOD_FLOOR * n) for w, d in zip(weighted, dark, strict=True)]
    total = sum(raw)
    return [r / total for r in raw]


def capped_dark(singles: list[list[int]], receipt: list[list[float]]) -> list[list[float]]:
    """Expected dark clicks per setting and mode: the receipt's rate times the setting's time share, capped by the
    mode's lowest click fraction over the job's settings, since a dark rate cannot exceed the least light a mode saw."""
    floors = [min(s[m] / max(sum(s), 1) for s in singles) for m in range(MODES)]
    return [[min(d[m], floors[m] * sum(s)) for m in range(MODES)] for s, d in zip(singles, receipt, strict=True)]


def first_best(values: list[float]) -> int:
    """Index of the first value within TIE_NATS of the maximum. Every class holds the ideal mesh at its null
    magnitude and the misroute classes hold the dephasing channel at fraction 0, so nested points tie up to
    float paths that differ between BLAS builds; callers order candidates simplest first."""
    top = max(values)
    return next(i for i, v in enumerate(values) if v >= top - TIE_NATS)


def pooled_deviance(counts: list[int], probabilities: list[float]) -> tuple[float, int]:
    """Poisson deviance and bin count after Cochran pooling.

    Bins expected below POOL_MIN counts merge into one rest bin. When the rest bin saw clicks, its
    expectation is floored at one count, the resolution of an N-sample histogram, so a stray click where the
    mesh predicts 1e-7 costs what one unexplained count costs and an empty rest bin costs nothing.
    """
    n = sum(counts)
    bins = [(c, n * p) for c, p in zip(counts, probabilities, strict=True) if n * p >= POOL_MIN]
    rest = [(c, n * p) for c, p in zip(counts, probabilities, strict=True) if n * p < POOL_MIN]
    if rest:
        seen = sum(c for c, _ in rest)
        bins.append((seen, max(sum(e for _, e in rest), min(1.0, seen))))
    deviance = 2 * sum((c * math.log(c / e) if c else 0.0) - (c - e) for c, e in bins)
    return deviance, len(bins)


class Scan:
    """Every class's summed likelihood over its magnitude grid on one setting's returned mesh.

    Phase noise and the misroute-plus-noise mixtures use the exact dephasing
    channel, so a scan is a deterministic function of the mesh.
    """

    def __init__(self, arch: list[Element], nbr: list[list[int]]) -> None:
        self.arch, self.nbr = arch, nbr

    def __call__(self, job: tuple[list[float], int]) -> dict[str, list[list[float]]]:
        import numpy as np

        phases, low = job
        phi = np.asarray(phases) % (2 * math.pi)
        arch = self.arch
        out: dict[str, list[list[float]]] = {}
        noisy: dict[tuple[float, int], Any] = {}
        sources = [low] + [min(max(low + k, 0), MODES - 1) for k in MISROUTE_OFFSETS]
        for sigma in SCAN_SIGMAS:
            for src in sources:
                noisy[(sigma, src)] = channel(arch, list(phi), src, sigma=sigma)
        out["phase_noise"] = [noisy[(sigma, low)].tolist() for sigma in SCAN_SIGMAS]
        out["gain"] = [propagate(arch, list(phi + g * phi), low)[0].tolist() for g in SCAN_GAINS]
        heat = np.array([phi[n].sum() for n in self.nbr])
        out["crosstalk"] = [propagate(arch, list(phi + k * heat), low)[0].tolist() for k in SCAN_CROSSTALK]
        for offset, src in zip(MISROUTE_OFFSETS, sources[1:], strict=True):
            out[f"misroute_{offset:+d}"] = [
                ((1 - f) * noisy[(sigma, low)] + f * noisy[(sigma, src)]).tolist()
                for sigma in SCAN_SIGMAS
                for f in SCAN_FRACTIONS
            ]
        return out


def jacobians(arch: list[Element], phases: Any, sources: list[int]) -> tuple[Any, Any]:
    """Detection probabilities p (S x 24) and dp / dphi (S x 24 x 574) of S one-photon settings, by adjoint.

    A forward pass keeps each phase shifter's output amplitude; a backward pass
    carries G, the product of the elements after the current one, so
    d psi_out / d phi_j = G[:, q] i psi_after_j[q] for the shifter on mode q.
    """
    import numpy as np

    count = len(sources)
    psi = np.zeros((count, MODES), dtype=complex)
    psi[np.arange(count), sources] = 1
    after = []
    t = 0
    for kind, m, p in arch:
        if kind == "bs":
            psi[:, m : m + 2] = psi[:, m : m + 2] @ coupler(*p).T
        else:
            psi[:, m] *= np.exp(1j * phases[:, t])
            after.append(psi[:, m].copy())
            t += 1
    g = np.broadcast_to(np.eye(MODES, dtype=complex), (count, MODES, MODES)).copy()
    d = np.zeros((count, MODES, t), dtype=complex)
    for kind, m, p in reversed(arch):
        if kind == "bs":
            g[:, :, m : m + 2] = g[:, :, m : m + 2] @ coupler(*p)
        else:
            t -= 1
            d[:, :, t] = g[:, :, m] * (1j * after[t])[:, None]
            g[:, :, m] *= np.exp(1j * phases[:, t])[:, None]
    return np.abs(psi) ** 2, 2 * np.real(np.conj(psi)[:, :, None] * d)


class Dephased:
    """Exact dephasing-channel detection probabilities of one (phases, source, sigma) job on one architecture."""

    def __init__(self, arch: list[Element]) -> None:
        self.arch = arch

    def __call__(self, job: tuple[list[float], int, float]) -> list[float]:
        phases, source, sigma = job
        out: list[float] = channel(self.arch, phases, source, sigma=sigma).tolist()
        return out


def floored_likelihood(weighted: Any, counts: Any, dark: Any) -> tuple[float, Any]:
    """The multinomial log-likelihood `loglik` scores, summed over settings, and its gradient in the weighted light.

    Per setting lambda_m = max(A w_m / S + d_m, LIKELIHOOD_FLOOR N) with A = N - sum d and S = sum w, normalized
    to lambda_m / Lambda as `rates` does; a floored bin is constant in w, so with r_m = n_m / lambda_m - N / Lambda
    on the unfloored bins and 0 elsewhere, d/dw_j = (A / S) r_j - (A / S^2) sum_m r_m w_m.
    """
    import numpy as np

    total = counts.sum(1, keepdims=True)
    norm = np.maximum(weighted.sum(1, keepdims=True), 1e-300)
    light = np.maximum(total - dark.sum(1, keepdims=True), 0)
    free = light * weighted / norm + dark
    floor = LIKELIHOOD_FLOOR * total
    lam = np.maximum(free, floor)
    whole = lam.sum(1, keepdims=True)
    value = float((counts * np.log(lam / whole)).sum())
    r = np.where(free >= floor, counts / lam - total / whole, 0.0)
    dw = light / norm * r - light / norm**2 * (r * weighted).sum(1, keepdims=True)
    return value, dw


class StaticFit:
    """MAP estimate of one heater-offset vector shared by every setting, under a Gaussian prior of width tau."""

    def __init__(self, arch: list[Element], meshes: Any, sources: list[int], counts: Any, eta: Any, dark: Any) -> None:
        import numpy as np

        self.arch, self.meshes, self.sources = arch, np.asarray(meshes), list(sources)
        self.counts, self.eta, self.dark = np.asarray(counts, float), np.asarray(eta, float), np.asarray(dark, float)

    def loglik(self, delta: Any, keep: Any) -> tuple[float, Any]:
        """Summed log-likelihood of the kept settings at offsets delta, and its gradient in delta."""
        import numpy as np

        p, jac = jacobians(self.arch, self.meshes[keep] + delta, [self.sources[i] for i in keep])
        value, dw = floored_likelihood(p * self.eta, self.counts[keep], self.dark[keep])
        return value, np.einsum("sm,smj->j", dw * self.eta, jac)

    def fit(self, keep: Any, tau: float) -> Any:
        import numpy as np
        from scipy.optimize import minimize

        def objective(delta: Any) -> tuple[float, Any]:
            value, grad = self.loglik(delta, keep)
            return -(value - float((delta**2).sum()) / (2 * tau**2)), -(grad - delta / tau**2)

        found = minimize(
            objective, np.zeros(self.meshes.shape[1]), jac=True, method="L-BFGS-B", options={"maxiter": 400}
        )
        return found.x


def static_cross_validation(
    arch: list[Element],
    meshes: Any,
    sources: list[int],
    counts: Any,
    eta: Any,
    dark: Any,
    taus: tuple[float, ...],
    folds: list[int] | None = None,
) -> dict[str, Any]:
    """Held-out log-likelihood gain of shared static heater offsets over the best dephasing ensemble.

    Settings split into the given folds (one per run in a campaign), or STATIC_FOLDS folds by index. On
    each fold the baseline is the exact dephasing
    channel at the sigma of SCAN_SIGMAS that best fits the other folds, and the static model is the MAP
    offset vector fitted on the other folds; both are scored on the fold. The static class is declared
    when the summed gain exceeds STATIC_GAIN_MIN nats and the median held-out TVD over the shot-noise
    floor stays at most FIT_TVD_RATIO, so an offset vector that only spreads light where the nominal mesh
    puts none, or that fits nothing, is not a static calibration error.
    """
    import numpy as np

    fitter = StaticFit(arch, meshes, sources, counts, eta, dark)
    rows = [list(map(int, c)) for c in np.asarray(counts)]
    darks = [list(map(float, d)) for d in np.asarray(dark)]
    effs = list(map(float, np.asarray(eta)))
    flat = parallel.ordered_map(
        Dephased(arch),
        [(list(ph), src, sg) for ph, src in zip(meshes, sources, strict=True) for sg in SCAN_SIGMAS],
        min_items=2,
    )
    noisy = [flat[i * len(SCAN_SIGMAS) : (i + 1) * len(SCAN_SIGMAS)] for i in range(len(sources))]
    index = np.arange(len(sources))
    label = np.asarray(folds) if folds is not None else index % STATIC_FOLDS
    out: dict[str, Any] = {}
    for tau in taus:
        gain, ratios = 0.0, []
        for fold in sorted(set(label.tolist())):
            test, train = index[label == fold], index[label != fold]
            sigma = max(
                range(len(SCAN_SIGMAS)),
                key=lambda k: sum(loglik(rows[i], noisy[i][k], effs, darks[i]) for i in train),
            )
            baseline = sum(loglik(rows[i], noisy[i][sigma], effs, darks[i]) for i in test)
            delta = fitter.fit(train, tau)
            gain += fitter.loglik(delta, test)[0] - baseline
            p, _ = jacobians(arch, np.asarray(meshes)[test] + delta, [sources[i] for i in test])
            for i, row in zip(test, p, strict=True):
                q = rates(rows[i], list(row), effs, darks[i])
                tvd_i = 0.5 * sum(abs(c / sum(rows[i]) - v) for c, v in zip(rows[i], q, strict=True))
                ratios.append(tvd_i / max(shot_floor(q, sum(rows[i])), 1e-12))
        ratios.sort()
        out[f"{tau}"] = {
            "gain_over_dephasing": round(gain, 3),
            "median_tvd_over_floor": round(ratios[len(ratios) // 2], 3),
        }
    best = max(out, key=lambda k: out[k]["gain_over_dephasing"])
    declared = (
        out[best]["gain_over_dephasing"] > STATIC_GAIN_MIN and out[best]["median_tvd_over_floor"] <= FIT_TVD_RATIO
    )
    return {"by_tau": out, "best_tau": float(best), "static_declared": bool(declared)}


def static_record(runs: list[Path]) -> dict[str, Any]:
    """The static-offset cross-validation of retained mesh runs of one calibration session.

    Every run must carry the same couplers (one session); with two or more runs each run is a fold, so the
    offsets fitted on the other runs must predict a whole run they never saw.
    """
    meshes: list[list[float]] = []
    lows: list[int] = []
    singles: list[list[int]] = []
    dark: list[list[float]] = []
    folds: list[int] = []
    arch: list[Element] = []
    eta: list[float] = []
    for k, run in enumerate(runs):
        manifest = json.loads((run / "cases.json").read_text(encoding="utf-8"))
        analysis = json.loads((run / "analysis.json").read_text(encoding="utf-8"))
        texts = computed_circuits(run)
        mine = run_architecture(decode(texts[0]))
        require(
            not arch or mine == arch, f"{run.name}: couplers differ from {runs[0].name}, another calibration session"
        )
        arch = mine
        meshes += [mesh_phases(arch, decode(t)) for t in texts]
        perfs = json.loads((run / "submission.json").read_text(encoding="utf-8")).get("perfs_at_plan", {})
        eta = (perfs.get("Transmission per mode (%)") or {}).get("t_out") or [1.0] * MODES
        singles += [s["single_click"] for s in analysis["settings"]]
        dark += analysis["dark_expected"]
        lows += [row["low"] for row in manifest["settings"]]
        folds += [k] * len(texts)
    return {
        "schema": STATIC_SCHEMA,
        "runs": [run.name for run in runs],
        "analysis_sha256": [sha256(run / "analysis.json") for run in runs],
        "settings": len(lows),
        **static_cross_validation(
            arch, meshes, lows, singles, eta, dark, STATIC_TAUS, folds if len(runs) > 1 else None
        ),
    }


def fit_endpoints_close(a: dict[str, Any], b: dict[str, Any], owner: str) -> None:
    """Static-fit blocks replay when their verdicts match and every endpoint agrees within
    STATIC_FIT_REPLAY_TOLERANCE relative (at least one nat); the best prior width must match whenever the
    retained gains of the widths lie further apart than that tolerance, so a near tie may resolve either way."""
    require(a["static_declared"] == b["static_declared"], f"{owner}: static verdict differs")
    require(set(a["by_tau"]) == set(b["by_tau"]), f"{owner}: prior widths differ")
    for tau, row in a["by_tau"].items():
        require(set(row) == set(b["by_tau"][tau]), f"{owner}: {tau} fields differ")
        for key, value in row.items():
            other = b["by_tau"][tau][key]
            require(abs(value - other) <= max(1.0, STATIC_FIT_REPLAY_TOLERANCE * abs(other)), f"{owner}: {tau} {key}")
    gains = sorted(row["gain_over_dephasing"] for row in a["by_tau"].values())
    separated = all(
        hi - lo > STATIC_FIT_REPLAY_TOLERANCE * max(abs(hi), abs(lo), 1.0)
        for lo, hi in zip(gains, gains[1:], strict=False)
    )
    require(not separated or a["best_tau"] == b["best_tau"], f"{owner}: best prior width differs")


def static_close(a: dict[str, Any], b: dict[str, Any]) -> None:
    """A static record replays when its digests and settings match exactly and its fit block replays."""
    require(
        {k: a[k] for k in ("schema", "runs", "analysis_sha256", "settings")}
        == {k: b[k] for k in ("schema", "runs", "analysis_sha256", "settings")},
        f"{a.get('runs')}: static record differs",
    )
    fit_endpoints_close(a, b, str(a["runs"]))


# --- fitted detection efficiencies -----------------------------------------------------------


def fit_efficiency(p: Any, counts: Any) -> Any:
    """Relative per-mode detection efficiencies, geometric mean 1, maximizing the multinomial likelihood.

    p is (..., S, 24) model detection probabilities and counts (S, 24). The fit is the iterative
    proportional fit of lambda_sm = A_s eta_m p_sm, whose profile over the free scales A_s is the
    multinomial of each setting's one-click histogram: a sweep sets every A_s to the setting's clicks over
    its weighted light and every eta_m to the mode's clicks over its scaled light. Leading axes batch
    independent fits (one per scan point). A mode that receives no model light in any setting keeps 1.
    """
    import numpy as np

    p = np.asarray(p, float)
    n = np.asarray(counts, float)
    eta = np.ones(p.shape[:-2] + (MODES,))
    clicks = n.sum(-2)
    for _ in range(EFFICIENCY_SWEEPS):
        scale = n.sum(-1) / np.maximum((p * eta[..., None, :]).sum(-1), 1e-300)
        light = (scale[..., None] * p).sum(-2)
        new = np.where(light > 0, (clicks + 1e-12) / np.maximum(light, 1e-300), 1.0)
        new = new / np.exp(np.log(new).mean(-1, keepdims=True))
        if np.max(np.abs(new - eta)) < EFFICIENCY_TOLERANCE:
            return new
        eta = new
    return eta


def held_out_fit(rows: list[tuple[list[int], list[float]]]) -> dict[str, Any]:
    """Pooled deviance p-value and median TVD over the shot-noise floor of held-out settings."""
    from scipy.stats import chi2

    pooled = [pooled_deviance(c, q) for c, q in rows]
    g2 = sum(d for d, _ in pooled)
    dof = max(sum(k - 1 for _, k in pooled), 1)
    ratios = sorted(
        float(0.5 * sum(abs(v / sum(c) - x) for v, x in zip(c, q, strict=True)) / max(shot_floor(q, sum(c)), 1e-12))
        for c, q in rows
    )
    p_value = float(f"{chi2.sf(g2, dof):.6g}")
    median = ratios[len(ratios) // 2]
    return {
        "g2_per_dof": round(g2 / dof, 6),
        "p_value": p_value,
        "median_tvd_over_floor": round(median, 6),
        "fits": bool(p_value >= FIT_P_MIN and median <= FIT_TVD_RATIO),
    }


def efficiency_classes(
    scans: list[dict[str, list[list[float]]]], singles: list[list[int]], folds: list[int]
) -> dict[str, Any]:
    """Every class scanned with per-mode efficiencies fitted jointly, scored on settings held out by fold.

    For each fold and each scan point the efficiencies are fitted on the other folds; the point with the
    best training likelihood, its efficiencies and the class's prediction then score the fold. A class fits
    when the held-out pooled deviance has p >= FIT_P_MIN and the held-out median TVD stays within
    FIT_TVD_RATIO shot-noise floors; the verdict is the best held-out class when it fits ("ideal" when its
    every chosen point is the null magnitude), otherwise "no class fits".
    """
    import numpy as np

    zeros = [0.0] * MODES
    index = np.arange(len(singles))
    label = np.asarray(folds)
    counts = np.asarray(singles, float)
    classes: dict[str, dict[str, Any]] = {}
    for name, points in scan_axes().items():
        p = np.asarray([[scans[i][name][j] for i in index] for j in range(len(points))])
        held, chosen, rows = 0.0, [], []
        for fold in sorted(set(folds)):
            test, train = index[label == fold], index[label != fold]
            eta = fit_efficiency(p[:, train], counts[train])
            trained = [
                sum(loglik(singles[i], list(p[j, i]), list(eta[j]), zeros) for i in train) for j in range(len(points))
            ]
            j = first_best(trained)
            chosen.append(points[j])
            for i in test:
                held += loglik(singles[i], list(p[j, i]), list(eta[j]), zeros)
                rows.append((singles[i], rates(singles[i], list(p[j, i]), list(eta[j]), zeros)))
        classes[name] = {"chosen": chosen, "held_out_log_likelihood": round(float(held), 6), **held_out_fit(rows)}
    order = list(classes)
    best = order[first_best([classes[k]["held_out_log_likelihood"] for k in order])]
    null = all(not any(point.values()) for point in classes[best]["chosen"])
    return {
        "classes": classes,
        "best_class": best,
        "verdict": ("ideal" if null else best) if classes[best]["fits"] else "no class fits",
    }


class StaticEfficiencyFit(StaticFit):
    """MAP estimate of shared heater offsets (Gaussian prior of width tau) and relative per-mode efficiencies.

    The efficiencies are exp(u - mean u), so their geometric mean is 1 and u carries no prior; the
    multinomial of each setting is invariant to a common efficiency scale.
    """

    def __init__(self, arch: list[Element], meshes: Any, sources: list[int], counts: Any) -> None:
        import numpy as np

        super().__init__(arch, meshes, sources, counts, np.ones(MODES), np.zeros((len(sources), MODES)))

    def joint(self, delta: Any, u: Any, keep: Any) -> tuple[float, Any, Any]:
        """Summed log-likelihood of the kept settings and its gradients in delta and u."""
        import numpy as np

        eta = np.exp(u - u.mean())
        p, jac = jacobians(self.arch, self.meshes[keep] + delta, [self.sources[i] for i in keep])
        value, dw = floored_likelihood(p * eta, self.counts[keep], self.dark[keep])
        g = (dw * p).sum(0) * eta
        return value, np.einsum("sm,smj->j", dw * eta, jac), g - g.mean()

    def fit_joint(self, keep: Any, tau: float) -> tuple[Any, Any]:
        import numpy as np
        from scipy.optimize import minimize

        size = self.meshes.shape[1]
        start = np.log(
            fit_efficiency(
                jacobians(self.arch, self.meshes[keep], [self.sources[i] for i in keep])[0], self.counts[keep]
            )
        )

        def objective(x: Any) -> tuple[float, Any]:
            delta, u = x[:size], x[size:]
            value, gd, gu = self.joint(delta, u, keep)
            return -(value - float((delta**2).sum()) / (2 * tau**2)), -np.concatenate([gd - delta / tau**2, gu])

        found = minimize(
            objective,
            np.concatenate([np.zeros(size), start]),
            jac=True,
            method="L-BFGS-B",
            options={"maxiter": EFFICIENCY_STATIC_ITERATIONS},
        )
        return found.x[:size], np.exp(found.x[size:] - found.x[size:].mean())


def efficiency_static(
    arch: list[Element], meshes: Any, sources: list[int], counts: Any, taus: tuple[float, ...], folds: list[int]
) -> dict[str, Any]:
    """Held-out gain of shared static offsets with fitted efficiencies over fitted efficiencies and dephasing.

    On each fold the baseline is the exact dephasing channel at the sigma of SCAN_SIGMAS (0 included) whose
    efficiency fit best explains the other folds, and the static model fits offsets and efficiencies jointly
    on the other folds; both score the fold. Static offsets are declared when the summed gain exceeds
    STATIC_GAIN_MIN nats and the held-out median TVD stays within FIT_TVD_RATIO shot-noise floors, so an
    efficiency correction alone never passes for a static calibration error.
    """
    import numpy as np

    fitter = StaticEfficiencyFit(arch, meshes, sources, counts)
    rows = [list(map(int, c)) for c in np.asarray(counts)]
    zeros = [0.0] * MODES
    noisy = np.asarray(
        parallel.ordered_map(
            Dephased(arch),
            [(list(ph), src, sg) for sg in SCAN_SIGMAS for ph, src in zip(meshes, sources, strict=True)],
            min_items=2,
        )
    ).reshape(len(SCAN_SIGMAS), len(sources), MODES)
    index = np.arange(len(sources))
    label = np.asarray(folds)
    out: dict[str, Any] = {}
    for tau in taus:
        gain, ratios = 0.0, []
        for fold in sorted(set(folds)):
            test, train = index[label == fold], index[label != fold]
            etas = fit_efficiency(noisy[:, train], np.asarray(rows, float)[train])
            k = first_best(
                [
                    sum(loglik(rows[i], list(noisy[s, i]), list(etas[s]), zeros) for i in train)
                    for s in range(len(SCAN_SIGMAS))
                ]
            )
            baseline = sum(loglik(rows[i], list(noisy[k, i]), list(etas[k]), zeros) for i in test)
            delta, eta = fitter.fit_joint(train, tau)
            p, _ = jacobians(arch, np.asarray(meshes)[test] + delta, [sources[i] for i in test])
            for i, row in zip(test, p, strict=True):
                q = rates(rows[i], list(row), list(eta), zeros)
                gain += loglik(rows[i], list(row), list(eta), zeros)
                tvd_i = 0.5 * sum(abs(c / sum(rows[i]) - v) for c, v in zip(rows[i], q, strict=True))
                ratios.append(float(tvd_i / max(shot_floor(q, sum(rows[i])), 1e-12)))
            gain -= baseline
        ratios.sort()
        out[f"{tau}"] = {
            "gain_over_dephasing": round(float(gain), 3),
            "median_tvd_over_floor": round(ratios[len(ratios) // 2], 3),
        }
    best = max(out, key=lambda key: out[key]["gain_over_dephasing"])
    declared = (
        out[best]["gain_over_dephasing"] > STATIC_GAIN_MIN and out[best]["median_tvd_over_floor"] <= FIT_TVD_RATIO
    )
    return {"by_tau": out, "best_tau": float(best), "static_declared": bool(declared)}


def campaign(runs: list[Path]) -> dict[str, Any]:
    """Meshes, sources, one-click counts and folds of the retained mesh runs of one calibration session."""
    meshes: list[list[float]] = []
    lows: list[int] = []
    singles: list[list[int]] = []
    folds: list[int] = []
    arch: list[Element] = []
    t_out: list[list[float]] = []
    for k, run in enumerate(runs):
        manifest = json.loads((run / "cases.json").read_text(encoding="utf-8"))
        analysis = json.loads((run / "analysis.json").read_text(encoding="utf-8"))
        texts = computed_circuits(run)
        mine = run_architecture(decode(texts[0]))
        require(
            not arch or mine == arch, f"{run.name}: couplers differ from {runs[0].name}, another calibration session"
        )
        arch = mine
        meshes += [mesh_phases(arch, decode(t)) for t in texts]
        singles += [s["single_click"] for s in analysis["settings"]]
        lows += [row["low"] for row in manifest["settings"]]
        folds += [k] * len(texts)
        perfs = json.loads((run / "submission.json").read_text(encoding="utf-8")).get("perfs_at_plan", {})
        t_out.append((perfs.get("Transmission per mode (%)") or {}).get("t_out") or [1.0] * MODES)
    return {"arch": arch, "meshes": meshes, "lows": lows, "singles": singles, "folds": folds, "t_out": t_out}


def efficiency_record(runs: list[Path]) -> dict[str, Any]:
    """The fitted-efficiency reanalysis of the mesh runs of one calibration session, each run one fold.

    It replaces the receipt's t_out efficiencies and dark rates, which the runs themselves refute, by
    relative per-mode efficiencies fitted with every class and with the static offsets, and no dark term.
    """
    import numpy as np

    require(len(runs) > 1, "the fitted-efficiency reanalysis holds out whole runs, so it needs two or more")
    data = campaign(runs)
    arch, meshes, lows, singles = data["arch"], data["meshes"], data["lows"], data["singles"]
    scans = parallel.ordered_map(Scan(arch, neighbours(arch)), list(zip(meshes, lows, strict=True)), min_items=2)
    ideal = np.asarray([scan["phase_noise"][0] for scan in scans])
    eta = fit_efficiency(ideal, np.asarray(singles, float))
    return {
        "schema": EFFICIENCY_SCHEMA,
        "runs": [run.name for run in runs],
        "analysis_sha256": [sha256(run / "analysis.json") for run in runs],
        "settings": len(lows),
        "t_out_at_plan": data["t_out"],
        "efficiency_under_ideal": [round(float(v), 6) for v in eta],
        **efficiency_classes(scans, singles, data["folds"]),
        "static": efficiency_static(arch, meshes, lows, singles, STATIC_TAUS, data["folds"]),
    }


def efficiency_close(a: dict[str, Any], b: dict[str, Any]) -> None:
    """A fitted-efficiency record replays when its digests, verdicts, classes and efficiencies match (numbers within
    STATIC_REPLAY_TOLERANCE relative, at least one nat on likelihood sums) and its static fit block replays."""
    keys = ("schema", "runs", "analysis_sha256", "settings", "best_class", "verdict")
    require({k: a[k] for k in keys} == {k: b[k] for k in keys}, f"{a.get('runs')}: fitted-efficiency verdict differs")
    require(set(a) == set(b) and set(a["static"]) == set(b["static"]), f"{a['runs']}: record fields differ")
    require(set(a["static"]["by_tau"]) == set(b["static"]["by_tau"]), f"{a['runs']}: prior widths differ")
    require(set(a["classes"]) == set(b["classes"]), f"{a['runs']}: scanned classes differ")
    for name, row in a["classes"].items():
        require(set(row) == set(b["classes"][name]), f"{name}: fields differ")
        require(row["chosen"] == b["classes"][name]["chosen"] and row["fits"] == b["classes"][name]["fits"], name)
        p_retained, p_replayed = row["p_value"], b["classes"][name]["p_value"]
        require(
            abs(p_retained - p_replayed) <= max(1e-12, STATIC_REPLAY_TOLERANCE * abs(p_replayed)), f"{name} p_value"
        )
        for key in ("held_out_log_likelihood", "g2_per_dof", "median_tvd_over_floor"):
            other = b["classes"][name][key]
            require(
                abs(row[key] - other)
                <= max(1.0 if key == "held_out_log_likelihood" else 1e-3, STATIC_REPLAY_TOLERANCE * abs(other)),
                f"{name} {key}",
            )
    fit_endpoints_close(a["static"], b["static"], str(a["runs"]))
    close_relative(a["efficiency_under_ideal"], b["efficiency_under_ideal"], "efficiency_under_ideal")
    require(a["t_out_at_plan"] == b["t_out_at_plan"], "t_out_at_plan differs")


class OffsetShare:
    """in_block and algebra share a of one block mesh at drawn heater phases, weighted by fitted efficiencies."""

    def __init__(self, arch: list[Element], eta: list[float]) -> None:
        self.arch, self.eta = arch, eta

    def __call__(self, job: tuple[list[float], int]) -> tuple[float, float]:
        import numpy as np

        phases, low = job
        p = propagate(self.arch, phases, low)[0]
        w = p * np.asarray(self.eta)
        w = w / w.sum()
        block = float(w[low : low + 4].sum())
        return block, float(w[low : low + 2].sum()) / block


def offset_draws(phases: Any, low: int, rms: float, rng: Any) -> list[tuple[list[float], int]]:
    """FOLLOWUP_DRAWS independent heater-offset draws of one block mesh, in the generator's order."""
    return [(list(phases + rng.normal(0, rms, phases.size)), low) for _ in range(FOLLOWUP_DRAWS)]


def offset_summary(shares: list[tuple[float, float]]) -> dict[str, Any]:
    """Mean and 5th and 95th percentiles of in_block and a over a configuration's offset draws."""
    import numpy as np

    draws = np.asarray(shares)

    def summary(column: Any) -> dict[str, float]:
        return {
            k: round(float(f(column)), 4)
            for k, f in (
                ("mean", np.mean),
                ("p05", lambda c: np.percentile(c, 5)),
                ("p95", lambda c: np.percentile(c, 95)),
            )
        }

    return {"in_block": summary(draws[:, 0]), "a": summary(draws[:, 1])}


def homogeneity(a: list[int], b: list[int]) -> tuple[float, int]:
    """G^2 of two one-click histograms against their pooled shape and its degrees of freedom; modes whose
    expected count falls below POOL_MIN in either run merge into one rest column."""
    na, nb = sum(a), sum(b)
    pooled = [(x + y) / (na + nb) for x, y in zip(a, b, strict=True)]
    keep = [m for m in range(MODES) if min(na, nb) * pooled[m] >= POOL_MIN]
    rest = [m for m in range(MODES) if m not in keep]
    columns = [([a[m]], [b[m]], pooled[m]) for m in keep]
    if rest and sum(pooled[m] for m in rest) > 0:
        columns.append(([a[m] for m in rest], [b[m] for m in rest], sum(pooled[m] for m in rest)))
    g2 = 0.0
    for xs, ys, q in columns:
        for observed, n in ((sum(xs), na), (sum(ys), nb)):
            if observed:
                g2 += 2 * observed * math.log(observed / (n * q))
    return g2, len(columns) - 1


def followup_record(preregistration: Path, job02: Path, repeat: Path, original: Path) -> dict[str, Any]:
    """The preregistered readout of the job-02 discriminator and the C1 job-03 repeat."""
    import numpy as np
    from scipy.stats import chi2

    prereg = json.loads(preregistration.read_text(encoding="utf-8"))
    rows = prereg["job_02"]["per_configuration"]
    analysis = json.loads((job02 / "analysis.json").read_text(encoding="utf-8"))
    eta = np.asarray(
        json.loads((preregistration.parent / "efficiency.json").read_text(encoding="utf-8"))["efficiency_under_ideal"]
    )
    texts = computed_circuits(job02)
    arch = run_architecture(decode(texts[0]))
    manifest = json.loads((job02 / "cases.json").read_text(encoding="utf-8"))
    rng = np.random.default_rng([SEED, FOLLOWUP_STREAM])
    # Every recomputed configuration draws its offsets in the stream's order before the pool propagates them,
    # so pooled and serial runs predict the same numbers.
    jobs: dict[str, list[tuple[list[float], int]]] = {}
    for row, setting, text, case in zip(rows, analysis["settings"], texts, manifest["settings"], strict=True):
        require(row["name"] == setting["name"], f"{job02.name}: {setting['name']} out of order")
        if setting["mesh_sha256"] != row["mesh_sha256_s5"]:
            phases = np.asarray(mesh_phases(arch, decode(text)))
            jobs[setting["name"]] = offset_draws(phases, case["low"], FOLLOWUP_RMS, rng)
    flat = parallel.ordered_map(
        OffsetShare(arch, list(map(float, eta))), [j for v in jobs.values() for j in v], min_items=2
    )
    shares = {name: flat[k * FOLLOWUP_DRAWS : (k + 1) * FOLLOWUP_DRAWS] for k, name in enumerate(jobs)}
    configurations = []
    for row, setting in zip(rows, analysis["settings"], strict=True):
        same = setting["name"] not in shares
        predicted = row["in_block_at_0.08"] if same else offset_summary(shares[setting["name"]])["in_block"]
        configurations.append(
            {
                "name": setting["name"],
                "mesh_equals_s5": same,
                "in_block": setting["in_block"],
                "in_block_wilson95": setting["in_block_wilson95"],
                "a": setting.get("a"),
                "a_wilson95": setting.get("a_wilson95"),
                "predicted_in_block_at_0.08": predicted,
            }
        )
    median = float(np.median([c["in_block"] for c in configurations]))
    threshold = float(np.median([c["predicted_in_block_at_0.08"]["p05"] for c in configurations]))
    verdict = (
        "job_specific"
        if median >= threshold
        else "sparse_targets_fail"
        if median <= FOLLOWUP_SPARSE_FAIL
        else "intermediate"
    )
    first = json.loads((original / "analysis.json").read_text(encoding="utf-8"))["settings"]
    again = json.loads((repeat / "analysis.json").read_text(encoding="utf-8"))["settings"]
    tests = [homogeneity(x["single_click"], y["single_click"]) for x, y in zip(first, again, strict=True)]
    g2, dof = sum(g for g, _ in tests), sum(d for _, d in tests)
    p_value = float(f"{chi2.sf(g2, max(dof, 1)):.6g}")
    tvds = sorted(
        0.5
        * sum(
            abs(u / sum(x["single_click"]) - v / sum(y["single_click"]))
            for u, v in zip(x["single_click"], y["single_click"], strict=True)
        )
        for x, y in zip(first, again, strict=True)
    )
    return {
        "schema": FOLLOWUP_SCHEMA,
        "preregistration_sha256": sha256(preregistration),
        "job_02": {
            "run": job02.name,
            "configurations": configurations,
            "median_in_block": round(median, 6),
            "job_specific_threshold": round(threshold, 4),
            "sparse_fail_threshold": FOLLOWUP_SPARSE_FAIL,
            "verdict": verdict,
            "a_mean_by_kind": analysis.get("a_mean_by_kind"),
        },
        "job_03_repeat": {
            "runs": [original.name, repeat.name],
            "meshes_identical": [x["mesh_sha256"] == y["mesh_sha256"] for x, y in zip(first, again, strict=True)],
            "g2": round(g2, 6),
            "dof": dof,
            "p_value": p_value,
            "median_tvd_between_runs": round(tvds[len(tvds) // 2], 6),
            "verdict": "reproducible" if p_value >= FIT_P_MIN else "drift",
        },
    }


def mesh_sha(text: str) -> str:
    return hashlib.sha256(unzip(text).encode()).hexdigest()


def pair_record(preregistration: Path, form: Path, ensemble: Path, job02: Path) -> dict[str, Any]:
    """The preregistered readout of the one-circuit form test and the 32-iteration seed ensemble."""
    import numpy as np

    prereg = json.loads(preregistration.read_text(encoding="utf-8"))
    rule = prereg["form"]
    block = json.loads((form / "analysis.json").read_text(encoding="utf-8"))["blocks"][0]
    (text,) = computed_circuits(form)
    returned = mesh_sha(text)
    if returned == rule["q1_mesh_sha256"]:
        form_verdict = "seed ignored"
    elif block["in_block"] <= rule["one_circuit_form_at_most"]:
        form_verdict = "one-circuit form"
    elif block["in_block"] >= rule["q1_mesh_at_least"]:
        form_verdict = "Q1 mesh"
    else:
        form_verdict = "intermediate"
    analysis = json.loads((ensemble / "analysis.json").read_text(encoding="utf-8"))
    zero = {s["name"]: s for s in json.loads((job02 / "analysis.json").read_text(encoding="utf-8"))["settings"]}
    rows: dict[str, dict[str, Any]] = {}
    for s in analysis["settings"]:
        name, seed = s["name"].rsplit("-s", 1)
        row = rows.setdefault(
            name, {"name": name, "seed_0": {k: zero[name][k] for k in ("a", "in_block", "mesh_sha256")}}
        )
        row[f"seed_{seed}"] = {k: s[k] for k in ("a", "in_block", "mesh_sha256")}
    configurations = []
    for row in rows.values():
        seeds = [row[f"seed_{k}"] for k in (0, *ENSEMBLE_SEEDS)]
        a = [s["a"] for s in seeds]
        configurations.append(
            {
                **row,
                "meshes_distinct": len({s["mesh_sha256"] for s in seeds}) == len(seeds),
                "a_spread": round(float(max(a) - min(a)), 6),
                "in_block_spread": round(
                    float(max(s["in_block"] for s in seeds) - min(s["in_block"] for s in seeds)), 6
                ),
            }
        )
    window = prereg["ensemble"]["duration_s"]
    return {
        "schema": PAIR_SCHEMA,
        "preregistration_sha256": sha256(preregistration),
        "form": {
            "run": form.name,
            "mesh_sha256": returned,
            "in_block": block["in_block"],
            "in_block_wilson95": block["in_block_wilson95"],
            "a": block["a"],
            "a_wilson95": block["a_wilson95"],
            "verdict": form_verdict,
        },
        "ensemble": {
            "run": ensemble.name,
            "configurations": configurations,
            "seed_selects_mesh": all(c["meshes_distinct"] for c in configurations),
            "a_mean_by_kind": analysis["a_mean_by_kind"],
            "median_a_spread": round(float(np.median([c["a_spread"] for c in configurations])), 6),
            "duration_s": analysis["duration_s"],
            "duration_within_prediction": window["low"] <= analysis["duration_s"] <= window["high"],
        },
    }


def pooled_in_block(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """in_block over the one-click samples of rows that share a mesh, with its Wilson interval."""
    from qd_box_kite_analysis import wilson

    inside = sum(sum(r["one_click_by_mode"]) for r in rows)
    outside = sum(r["one_click_outside_block"] for r in rows)
    return {
        "iterations": [r["name"] for r in rows],
        "in_block": round(inside / (inside + outside), 9) if inside + outside else None,
        "in_block_wilson95": wilson(inside, inside + outside),
    }


def bridge_verdict(rule: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    """The preregistered reading of Q1's circuit iterated over compilation seeds.

    Repeated seeds that return one mesh bound drift within the job by their largest in_block difference d; with no
    such repeat d is the cross-job scale on one mesh (cross_job_scale), the Q1 and replay difference. On
    Q1's mesh, in_block + d <= mesh_at_most reads "mesh" and in_block - d >= form_at_least reads "form or dwell"
    (the one-circuit job also dwelt longer per setting); between reads "intermediate". Over the distinct meshes, at
    least representation_fraction at or below mesh_at_most reads "representation", otherwise a median at or above
    iteration_median reads "iteration", otherwise "intermediate".
    """
    by_mesh: dict[str, list[dict[str, Any]]] = {}
    by_seed: dict[int, list[dict[str, Any]]] = {}
    for row in rows:
        by_mesh.setdefault(row["mesh_sha256"], []).append(row)
        by_seed.setdefault(row["compilation_seed"], []).append(row)
    repeats = []
    for seed, group in sorted(by_seed.items()):
        if len(group) > 1:
            values = [r["in_block"] for r in group]
            repeats.append(
                {
                    "compilation_seed": seed,
                    "same_mesh": len({r["mesh_sha256"] for r in group}) == 1,
                    "in_block": values,
                    "in_block_spread": round(max(values) - min(values), 9),
                }
            )
    measured = [r["in_block_spread"] for r in repeats if r["same_mesh"]]
    drift = max(measured) if measured else rule["cross_job_scale"]
    meshes = {sha: pooled_in_block(group) for sha, group in by_mesh.items()}
    values = sorted(m["in_block"] for m in meshes.values())
    median = (
        values[len(values) // 2] if len(values) % 2 else (values[len(values) // 2 - 1] + values[len(values) // 2]) / 2
    )
    leaky = sum(v <= rule["mesh_at_most"] for v in values) / len(values)
    family = (
        "representation"
        if leaky >= rule["representation_fraction"]
        else "iteration"
        if median >= rule["iteration_median"]
        else "intermediate"
    )
    bridges = {}
    for key in ("q1", "form"):
        reference = rule["one_circuit"][key]
        hit = meshes.get(reference["mesh_sha256"])
        entry: dict[str, Any] = {"mesh_sha256": reference["mesh_sha256"], "one_circuit_in_block": reference["in_block"]}
        if hit is not None:
            entry["iterated"] = hit
            if key == "q1":
                value = hit["in_block"]
                entry["verdict"] = (
                    "mesh"
                    if value + drift <= rule["mesh_at_most"]
                    else "form or dwell"
                    if value - drift >= rule["form_at_least"]
                    else "intermediate"
                )
        bridges[key] = entry
    branch = (
        "seed ignored"
        if len(meshes) == 1
        else "bridge on q1 mesh"
        if "iterated" in bridges["q1"]
        else "bridge on form mesh"
        if "iterated" in bridges["form"]
        else "bridge fails"
    )
    return {
        "branch": branch,
        "bridges": bridges,
        "drift_bound": round(drift, 9),
        "drift_measured": bool(measured),
        "repeated_seeds": repeats,
        "distinct_meshes": len(meshes),
        "meshes": dict(sorted(meshes.items())),
        "median_in_block_over_meshes": round(median, 9),
        "fraction_at_or_below_mesh_threshold": round(leaky, 9),
        "family_verdict": family,
    }


def bridge_record(preregistration: Path, bridge: Path) -> dict[str, Any]:
    """The preregistered readout of the bridge run (job-09) against Q1's one-circuit meshes."""
    prereg = json.loads(preregistration.read_text(encoding="utf-8"))
    analysis = json.loads((bridge / "analysis.json").read_text(encoding="utf-8"))
    rows = analysis["blocks"]
    require(
        [r["compilation_seed"] for r in rows] == prereg["compilation_seeds"],
        f"{bridge.name}: iterations ran seeds {[r['compilation_seed'] for r in rows]}",
    )
    rule = prereg["rule"]
    for key, reference in rule["one_circuit"].items():
        for name in reference["runs"]:
            (block,) = json.loads((RUNS / name / "analysis.json").read_text(encoding="utf-8"))["blocks"]
            (text,) = computed_circuits(RUNS / name)
            require(mesh_sha(text) == reference["mesh_sha256"], f"{name}: mesh differs from the {key} reference")
            require(block["in_block"] in reference["in_block"], f"{name}: in_block differs from the {key} reference")
    duration = json.loads((bridge / "results.json").read_text(encoding="utf-8"))["status"]["duration"]
    window = prereg["duration_s"]
    return {
        "schema": BRIDGE_SCHEMA,
        "preregistration_sha256": sha256(preregistration),
        "run": bridge.name,
        "job_id": analysis["job_id"],
        "per_iteration": [
            {k: r[k] for k in ("name", "compilation_seed", "mesh_sha256", "in_block", "in_block_wilson95", "a")}
            for r in rows
        ],
        **bridge_verdict(rule, rows),
        "duration_s": duration,
        "duration_within_prediction": window["low"] <= duration <= window["high"],
    }


def single_reading(rule: dict[str, Any], value: float, low: str, high: str) -> str:
    """A single-job in_block against the two thresholds, each widened by the cross-job scale."""
    margin = rule["cross_job_scale"]
    if value + margin <= rule["leak_at_most"]:
        return low
    if value - margin >= rule["holds_at_least"]:
        return high
    return "intermediate"


def ladder_reading(rule: dict[str, Any], rows: list[dict[str, Any]], mesh: str | None) -> dict[str, Any]:
    """An iterated dwell ladder on one mesh: pooled short-dwell against pooled long-dwell in_block.

    Every iteration must return one mesh (equal to mesh when named). The short iterations' in_block spread d
    bounds drift; a drop of at least ladder_drop + d from short to long reads "dwell", a drop of at most
    ladder_flat + d reads "flat", and anything between reads "intermediate".
    """
    served = {r["mesh_sha256"] for r in rows}
    if len(served) != 1 or (mesh is not None and served != {mesh}):
        return {"verdict": "mesh missing", "meshes": sorted(served)}
    short = [r for r in rows if r["max_samples"] <= rule["short_at_most"]]
    long = [r for r in rows if r["max_samples"] >= rule["long_at_least"]]
    values = [r["in_block"] for r in short]
    drift = max(values) - min(values) if len(values) > 1 else rule["cross_job_scale"]
    low, high = pooled_in_block(short), pooled_in_block(long)
    drop = low["in_block"] - high["in_block"]
    verdict = (
        "dwell"
        if drop >= rule["ladder_drop"] + drift
        else "flat"
        if drop <= rule["ladder_flat"] + drift
        else "intermediate"
    )
    return {
        "verdict": verdict,
        "mesh_sha256": served.pop(),
        "short": low,
        "long": high,
        "drop": round(drop, 9),
        "drift_bound": round(drift, 9),
        "by_dwell": [{k: r[k] for k in ("name", "max_samples", "in_block", "in_block_wilson95")} for r in rows],
    }


def dwell_verdict(
    rule: dict[str, Any], d1: dict[str, Any], d3: dict[str, Any], ladder: list[dict[str, Any]]
) -> dict[str, Any]:
    """The preregistered readings of D1, D3 and the D2 + D4 ladders, and whether D3 and D4 share a mesh."""
    q1 = rule["q1_mesh_sha256"]
    d2_rows = [r for r in ladder if r["name"].startswith("d2-")]
    d4_rows = [r for r in ladder if r["name"].startswith("d4-")]
    one = (
        {"verdict": "mesh missing", "mesh_sha256": d1["mesh_sha256"]}
        if d1["mesh_sha256"] != q1
        else {"verdict": single_reading(rule, d1["in_block"], "form", "dwell"), **d1}
    )
    # D3 asks how a mesh other than Q1's behaves, so a seed that serves Q1's mesh answers nothing.
    three = (
        {"verdict": "mesh collision", "mesh_sha256": d3["mesh_sha256"]}
        if d3["mesh_sha256"] == q1
        else {"verdict": single_reading(rule, d3["in_block"], "generic", "mesh susceptible"), **d3}
    )
    four = ladder_reading(rule, d4_rows, None)
    return {
        "d1": one,
        "d2": ladder_reading(rule, d2_rows, q1),
        "d3": three,
        "d4": four,
        "d3_d4_paired": four.get("mesh_sha256") == d3["mesh_sha256"],
    }


def dwell_single(run: Path) -> dict[str, Any]:
    (block,) = json.loads((run / "analysis.json").read_text(encoding="utf-8"))["blocks"]
    (text,) = computed_circuits(run)
    return {
        "run": run.name,
        "mesh_sha256": mesh_sha(text),
        **{k: block[k] for k in ("in_block", "in_block_wilson95", "a", "a_wilson95")},
    }


def dwell_record(preregistration: Path, d1: Path, d3: Path, ladder: Path) -> dict[str, Any]:
    """The preregistered readout of the form-versus-dwell series (job-10, job-11, job-12)."""
    prereg = json.loads(preregistration.read_text(encoding="utf-8"))
    manifest = json.loads((ladder / "cases.json").read_text(encoding="utf-8"))
    budgets = {s["name"]: s["max_samples"] for s in manifest["settings"]}
    rows = [
        {**r, "max_samples": budgets[r["name"]]}
        for r in json.loads((ladder / "analysis.json").read_text(encoding="utf-8"))["blocks"]
    ]
    durations = {
        run.name: json.loads((run / "results.json").read_text(encoding="utf-8"))["status"]["duration"]
        for run in (d1, d3, ladder)
    }
    return {
        "schema": DWELL_SCHEMA,
        "preregistration_sha256": sha256(preregistration),
        "runs": [d1.name, d3.name, ladder.name],
        **dwell_verdict(prereg["rule"], dwell_single(d1), dwell_single(d3), rows),
        "duration_s": durations,
    }


def dwell_self_test() -> int:
    """Each preregistered reading of the series on synthetic results."""
    rule = {
        "q1_mesh_sha256": "q1",
        "leak_at_most": 0.65,
        "holds_at_least": 0.9,
        "cross_job_scale": 0.034,
        "short_at_most": 1500,
        "long_at_least": 40000,
        "ladder_drop": 0.25,
        "ladder_flat": 0.05,
    }

    def it(tag: str, k: int, mesh: str, n: int, value: float) -> dict[str, Any]:
        inside = round(n * value)
        return {
            "name": f"{tag}-{k:02d}",
            "mesh_sha256": mesh,
            "max_samples": n,
            "in_block": inside / n,
            "in_block_wilson95": [0.0, 1.0],
            "one_click_by_mode": [inside, 0, 0, 0],
            "one_click_outside_block": n - inside,
        }

    def ladder(tag: str, mesh: str, short: float, long: float) -> list[dict[str, Any]]:
        return [it(tag, 0, mesh, 1500, short), it(tag, 1, mesh, 40000, long), it(tag, 2, mesh, 1500, short)]

    single = {"mesh_sha256": "q1", "in_block": 0.5}
    fresh = {"mesh_sha256": "f", "in_block": 0.95}
    cases = [
        (
            "form, no dwell",
            single,
            fresh,
            ladder("d2", "q1", 0.95, 0.95) + ladder("d4", "f", 0.95, 0.94),
            {"d1": "form", "d2": "flat", "d3": "mesh susceptible", "d4": "flat"},
            True,
        ),
        (
            "dwell",
            {**single, "in_block": 0.95},
            {**fresh, "in_block": 0.5},
            ladder("d2", "q1", 0.95, 0.5) + ladder("d4", "f", 0.95, 0.6),
            {"d1": "dwell", "d2": "dwell", "d3": "generic", "d4": "dwell"},
            True,
        ),
        (
            "edges",
            {**single, "in_block": 0.63},
            {**fresh, "in_block": 0.88},
            ladder("d2", "q1", 0.95, 0.8) + ladder("d4", "g", 0.95, 0.95),
            {"d1": "intermediate", "d2": "intermediate", "d3": "intermediate", "d4": "flat"},
            False,
        ),
        (
            "missing",
            {**single, "mesh_sha256": "x"},
            fresh,
            ladder("d2", "y", 0.95, 0.95) + [it("d4", 0, "f", 1500, 0.9), it("d4", 1, "g", 40000, 0.9)],
            {"d1": "mesh missing", "d2": "mesh missing", "d3": "mesh susceptible", "d4": "mesh missing"},
            False,
        ),
        (
            "collision",
            single,
            {**fresh, "mesh_sha256": "q1"},
            ladder("d2", "q1", 0.95, 0.95) + ladder("d4", "q1", 0.95, 0.95),
            {"d1": "form", "d2": "flat", "d3": "mesh collision", "d4": "flat"},
            True,
        ),
    ]
    for name, d1, d3, rows, want, paired in cases:
        got = dwell_verdict(rule, d1, d3, rows)
        read = {k: got[k]["verdict"] for k in want}
        if read != want or got["d3_d4_paired"] != paired:
            raise SystemExit(f"self-test: {name} reads {read}, paired {got['d3_d4_paired']}")
    print(f"dwell self-test: {len(cases)} series read as preregistered")
    return 0


def bridge_self_test() -> int:
    """Each preregistered branch on synthetic iterations: seed ignored, the Q1 bridge reading mesh, form or
    intermediate under drift, the form-mesh bridge, and a failed bridge reading representation or iteration."""
    rule = {
        "mesh_at_most": 0.65,
        "form_at_least": 0.9,
        "representation_fraction": 0.25,
        "iteration_median": 0.9,
        "cross_job_scale": 0.034,
        "one_circuit": {
            "q1": {"mesh_sha256": "q1", "in_block": [0.47, 0.5]},
            "form": {"mesh_sha256": "form", "in_block": [0.886]},
        },
    }

    def row(seed: int, mesh: str, value: float) -> dict[str, Any]:
        inside = round(1000 * value)
        return {
            "name": f"s{seed}-{mesh}",
            "compilation_seed": seed,
            "mesh_sha256": mesh,
            "in_block": inside / 1000,
            "one_click_by_mode": [inside, 0, 0, 0],
            "one_click_outside_block": 1000 - inside,
        }

    def fresh(n: int, value: float) -> list[dict[str, Any]]:
        return [row(seed, f"m{seed}", value) for seed in range(2, 2 + n)]

    cases: list[tuple[str, list[dict[str, Any]], str, str | None]] = [
        ("one mesh", [row(k % 2, "q1", 0.5) for k in range(4)], "seed ignored", "mesh"),
        ("q1 leaks", [row(0, "q1", 0.5), *fresh(4, 0.95), row(0, "q1", 0.52)], "bridge on q1 mesh", "mesh"),
        ("q1 holds", [row(0, "q1", 0.95), *fresh(4, 0.95), row(0, "q1", 0.96)], "bridge on q1 mesh", "form or dwell"),
        ("q1 drifts", [row(0, "q1", 0.6), *fresh(4, 0.95), row(0, "q1", 0.95)], "bridge on q1 mesh", "intermediate"),
        (
            "q1 once, edge",
            [row(0, "q1", 0.63), *fresh(4, 0.95), row(0, "z", 0.95)],
            "bridge on q1 mesh",
            "intermediate",
        ),
        ("q1 once, clear", [row(0, "q1", 0.5), *fresh(4, 0.95), row(0, "z", 0.95)], "bridge on q1 mesh", "mesh"),
        ("form mesh", [row(1, "form", 0.9), *fresh(4, 0.95)], "bridge on form mesh", None),
        ("leaky family", [*fresh(3, 0.95), row(9, "x", 0.5)], "bridge fails", None),
        ("holding family", fresh(5, 0.93), "bridge fails", None),
    ]
    families = {"leaky family": "representation", "holding family": "iteration"}
    for name, rows, branch, q1 in cases:
        got = bridge_verdict(rule, rows)
        if got["branch"] != branch or got["bridges"]["q1"].get("verdict") != q1:
            raise SystemExit(f"self-test: {name} reads {got['branch']}, {got['bridges']['q1'].get('verdict')}")
        if name in families and got["family_verdict"] != families[name]:
            raise SystemExit(f"self-test: {name} reads family {got['family_verdict']}")
    print(f"bridge self-test: {len(cases)} branches read as preregistered")
    return 0


def scan_axes() -> dict[str, list[dict[str, float]]]:
    mixture = [{"sigma": s, "fraction": f} for s in SCAN_SIGMAS for f in SCAN_FRACTIONS]
    return {
        "phase_noise": [{"sigma": s} for s in SCAN_SIGMAS],
        "gain": [{"gain": g} for g in SCAN_GAINS],
        "crosstalk": [{"kappa": k} for k in SCAN_CROSSTALK],
        **{f"misroute_{offset:+d}": mixture for offset in MISROUTE_OFFSETS},
    }


def score(
    arch: list[Element],
    meshes: list[list[float]],
    lows: list[int],
    singles: list[list[int]],
    eta: list[float],
    receipt_dark: list[list[float]],
) -> dict[str, Any]:
    """Fixed-model likelihoods, class scans and the goodness-of-fit verdict of one job's returned meshes and counts.

    A class fits when its best magnitude gives a chi-square p-value of G^2 at its degrees of freedom of at least
    FIT_P_MIN and the median ratio of each
    setting's total variation to its shot-noise floor <= FIT_TVD_RATIO; otherwise the job reads "no class fits".
    """
    from scipy.stats import chi2

    nbr = neighbours(arch)
    dark = capped_dark(singles, receipt_dark)
    fixed = [predict(arch, ph, low, nbr) for ph, low in zip(meshes, lows, strict=True)]
    names = list(fixed[0])
    per_setting = [
        {name: round(loglik(c, pred[name], eta, d), 6) for name in names}
        for c, pred, d in zip(singles, fixed, dark, strict=True)
    ]
    totals = {name: round(sum(ll[name] for ll in per_setting), 6) for name in names}
    scans = parallel.ordered_map(Scan(arch, nbr), list(zip(meshes, lows, strict=True)), min_items=2)
    axes = scan_axes()
    classes: dict[str, dict[str, Any]] = {}
    best_ll: dict[str, float] = {}
    for name, points in axes.items():
        summed = [
            sum(loglik(c, scans[i][name][j], eta, dark[i]) for i, c in enumerate(singles)) for j in range(len(points))
        ]
        j = first_best(summed)
        probabilities = [rates(c, scans[i][name][j], eta, dark[i]) for i, c in enumerate(singles)]
        pooled = [pooled_deviance(c, p) for c, p in zip(singles, probabilities, strict=True)]
        g2 = sum(d for d, _ in pooled)
        dof = sum(k - 1 for _, k in pooled) - len(points[j])
        ratios = sorted(
            0.5 * sum(abs(v / sum(c) - q) for v, q in zip(c, p, strict=True)) / max(shot_floor(p, sum(c)), 1e-12)
            for c, p in zip(singles, probabilities, strict=True)
        )
        median = ratios[len(ratios) // 2]
        classes[name] = {
            "best": points[j],
            "log_likelihood": round(summed[j], 6),
            "g2_per_dof": round(g2 / max(dof, 1), 6),
            "p_value": float(f"{chi2.sf(g2, max(dof, 1)):.6g}"),
            "median_tvd_over_floor": round(median, 6),
            "fits": bool(chi2.sf(g2, max(dof, 1)) >= FIT_P_MIN and median <= FIT_TVD_RATIO),
        }
        best_ll[name] = summed[j]
    # scan_axes orders classes by parameter count, so a tie resolves to the simplest nested class.
    order = list(best_ll)
    best = order[first_best([best_ll[k] for k in order])]
    fitting = [k for k, v in classes.items() if v["fits"]]
    return {
        "per_setting": per_setting,
        "fixed_totals": totals,
        "fixed_best": names[first_best([totals[k] for k in names])],
        "classes": classes,
        "best_class": best,
        # Every class contains the ideal mesh at its null magnitude; a best point there detects no error.
        "verdict": ("ideal" if not any(classes[best]["best"].values()) else best)
        if classes[best]["fits"]
        else "no class fits",
        "fitting_classes": fitting,
        "dark_expected": [[round(v, 3) for v in d] for d in dark],
    }


def analyze_run(run: Path, manifest: dict[str, Any], circuit: dict[str, Any]) -> dict[str, Any]:
    """Per setting: returned mesh, one-click histogram, dark-corrected block share, algebra share; then the score."""
    inner = raw_result(run)
    entries = inner.get("results_list") or [inner]
    arch = run_architecture(decode(entries[0]["computed_circuit"]))
    couplers_match = circuit["architecture"]["couplers"] == [[m, p[0]] for k, m, p in arch if k == "bs"]
    require(
        len(entries) == len(circuit["settings"]),
        f"{run.name}: {len(entries)} results for {len(circuit['settings'])} settings",
    )
    require(manifest["models"] == [{"name": n, "kind": k, "size": v} for n, k, v in MODELS], "the case's models differ")
    submission = json.loads((run / "submission.json").read_text(encoding="utf-8"))
    perfs = submission.get("perfs_at_plan", {})
    receipt = perfs.get("Dark counts (detection/s)") or [0.0] * MODES
    eta = (perfs.get("Transmission per mode (%)") or {}).get("t_out") or [1.0] * MODES
    duration = float(json.loads((run / "raw/result.json").read_text(encoding="utf-8")).get("duration") or 0)
    outer_shots = json.loads((run / "raw/result.json").read_text(encoding="utf-8")).get("shots")
    # A one-setting job answers without results_list; its shots are the outer result's.
    shots = [int(e.get("nb_shots_used") or 0) for e in entries] if "results_list" in inner else [int(outer_shots or 0)]
    meshes, singles, others = [], [], []
    for entry, row in zip(entries, manifest["settings"], strict=True):
        mesh = decode(entry["computed_circuit"])
        require(same_mesh(arch, mesh), f"{run.name}: {row['name']} returned a mesh outside the architecture")
        meshes.append(mesh_phases(arch, mesh))
        single = [0] * MODES
        other = 0
        for state, n in bscount(entry["results"]).items():
            if sum(state) == 1:
                single[state.index(1)] += n
            else:
                other += n
        singles.append(single)
        others.append(other)
    receipt_dark = [[r * duration * used / max(sum(shots), 1) for r in receipt] for used in shots]
    lows = [row["low"] for row in manifest["settings"]]
    scored = score(arch, meshes, lows, singles, eta, receipt_dark)
    settings = []
    for i, (entry, row, sent) in enumerate(zip(entries, manifest["settings"], circuit["settings"], strict=True)):
        single, low = singles[i], row["low"]
        corrected = [max(c - d, 0.0) for c, d in zip(single, scored["dark_expected"][i], strict=True)]
        n, block = sum(single), sum(single[low : low + 4])
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
        gap = max(circular_gap(a, b) for a, b in zip(meshes[i], sent["phases"], strict=True))
        settings.append(
            {
                "name": row["name"],
                "transpiled": gap > TRANSPILE_TOLERANCE,
                "max_phase_gap": round(gap, 12),
                "mesh_sha256": hashlib.sha256(unzip(entry["computed_circuit"]).encode()).hexdigest(),
                "mesh_heater_phase_sum": round(sum(meshes[i]), 6),
                "computed_input": entry.get("computed_input"),
                "single_click": single,
                "other_events": others[i],
                "nb_shots_used": shots[i],
                "in_block": round(block / n, 6) if n else None,
                "in_block_wilson95": wilson(block, n),
                "in_block_dark_corrected": round(sum(corrected[low : low + 4]) / sum(corrected), 6)
                if sum(corrected)
                else None,
                "log_likelihood": scored["per_setting"][i],
                **algebra,
            }
        )
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
        "couplers_match_case": couplers_match,
        "log_likelihood_total": scored["fixed_totals"],
        "best_model": scored["fixed_best"],
        "classes": scored["classes"],
        "best_class": scored["best_class"],
        "verdict": scored["verdict"],
        "fitting_classes": scored["fitting_classes"],
        "dark_expected": scored["dark_expected"],
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


def gradient_self_test() -> int:
    """Both static fits return the derivative of the likelihood they return, bins held at the floor included.

    S3's returned meshes put most modes near zero light, so clicks added where the mesh predicts below
    LIKELIHOOD_FLOOR hold those bins at the floor; central differences of the likelihood in the offsets and
    the efficiency logarithms must match the analytic gradients there.
    """
    import numpy as np

    texts = computed_circuits(RUNS / S3_RUN)
    arch = run_architecture(decode(texts[0]))
    manifest = json.loads((RUNS / S3_RUN / "cases.json").read_text(encoding="utf-8"))
    meshes = np.asarray([mesh_phases(arch, decode(t)) for t in texts[:3]])
    sources = [row["low"] for row in manifest["settings"][:3]]
    rng = np.random.default_rng([SEED, 31])
    p, jac = jacobians(arch, meshes, sources)
    counts = np.asarray([rng.multinomial(SAMPLES_PER_SETTING, row / row.sum()) for row in p], float)
    floored = [(s, int(np.argmin(p[s]))) for s in range(len(sources))]
    # The heaters that move each floored bin most are where a derivative that counts its clicks goes wrong.
    probes = {int(j) for s, m in floored for j in np.argsort(-np.abs(jac[s, m]))[:2]}
    probes |= {int(j) for j in rng.choice(meshes.shape[1], 3, replace=False)}
    for s, m in floored:
        require(p[s, m] < LIKELIHOOD_FLOOR / 10, f"gradient self-test: mode {m} of setting {s} carries light")
        counts[s, m] += 50
    keep = np.arange(len(sources))
    delta = rng.normal(0, 0.05, meshes.shape[1])
    u = rng.normal(0, 0.2, MODES)
    plain = StaticFit(arch, meshes, sources, counts, np.ones(MODES), np.zeros((len(sources), MODES)))
    joint = StaticEfficiencyFit(arch, meshes, sources, counts)
    v_plain, g_plain = plain.loglik(delta, keep)
    v_joint, g_delta, g_u = joint.joint(delta, u, keep)
    # The fitted objective is the likelihood that scores held-out folds: loglik on the same rates.
    shifted = jacobians(arch, meshes + delta, sources)[0]
    eta = np.exp(u - u.mean())
    zeros = [0.0] * MODES
    for value, weights in ((v_plain, [1.0] * MODES), (v_joint, list(eta))):
        scored = sum(loglik(list(map(int, c)), list(q), weights, zeros) for c, q in zip(counts, shifted, strict=True))
        require(
            abs(value - scored) <= 1e-9 * max(1.0, abs(scored)), f"fitted objective {value} against loglik {scored}"
        )
    step = 1e-6
    checked = 0
    for j in sorted(probes):
        e = np.zeros(meshes.shape[1])
        e[j] = step
        pairs = (
            ((plain.loglik(delta + e, keep)[0] - plain.loglik(delta - e, keep)[0]) / (2 * step), g_plain[j]),
            ((joint.joint(delta + e, u, keep)[0] - joint.joint(delta - e, u, keep)[0]) / (2 * step), g_delta[j]),
        )
        for numeric, analytic in pairs:
            require(
                abs(numeric - analytic) <= 1e-4 * max(1.0, abs(analytic)), f"offset {j}: {numeric} against {analytic}"
            )
            checked += 1
    for k in rng.choice(MODES, 4, replace=False):
        e = np.zeros(MODES)
        e[k] = step
        numeric = (joint.joint(delta, u + e, keep)[0] - joint.joint(delta, u - e, keep)[0]) / (2 * step)
        require(abs(numeric - g_u[k]) <= 1e-4 * max(1.0, abs(g_u[k])), f"efficiency {k}: {numeric} against {g_u[k]}")
        checked += 1
    return checked


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
        bridge_mutations: list[tuple[str, Any]] = [
            ("bridge seed", lambda c, m: m["settings"][22].__setitem__("compilation_seed", 22)),
            ("bridge setting parameter", lambda c, m: m["settings"][0].__setitem__("circuit_params", {"phi": 0.0})),
            ("bridge iterations", lambda c, m: m.__setitem__("iterations", 23)),
            ("bridge samples", lambda c, m: m.__setitem__("max_samples", 48000)),
            ("bridge circuit", lambda c, m: c["input_state"].reverse()),
        ]
        for name, mutate in bridge_mutations:
            target = Path(scratch) / name.replace(" ", "_")
            shutil.copytree(CASES / FAMILY / BRIDGE_JOB, target)
            circuit = json.loads((target / "circuit.json").read_text(encoding="utf-8"))
            manifest = json.loads((target / "cases.json").read_text(encoding="utf-8"))
            mutate(circuit, manifest)
            (target / "circuit.json").write_text(json.dumps(circuit, indent=1) + "\n", encoding="utf-8")
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
    checked = gradient_self_test()
    print(f"self-test: {rejected} mutations rejected, {checked} static-fit derivatives match central differences")
    return 0


def synthetic_verdicts() -> dict[str, str]:
    """The decision rule on counts drawn from known truths over the S3 meshes: in-family truths off the fixed grid
    must be found by the scans and fit, and an out-of-family truth must read "no class fits"."""
    import numpy as np

    run = RUNS / S3_RUN
    circuit = json.loads((run / "circuit.json").read_text(encoding="utf-8"))
    texts = computed_circuits(run)
    arch = run_architecture(decode(texts[0]))
    meshes = [mesh_phases(arch, decode(text)) for text in texts]
    lows = [s["input_mode"] for s in circuit["settings"]]
    eta = json.loads((RUNS / Q1_RUN / "submission.json").read_text(encoding="utf-8"))["perfs_at_plan"][
        "Transmission per mode (%)"
    ]["t_out"]
    rng = np.random.default_rng([SEED, 7])

    def draw(truths: list[Any]) -> list[list[int]]:
        out = []
        for p in truths:
            q = np.asarray(p) * np.asarray(eta)
            out.append([int(v) for v in rng.multinomial(SAMPLES_PER_SETTING, q / q.sum())])
        return out

    def noisy(phases: list[float], src: int, sigma: float) -> Any:
        return channel(arch, phases, src, sigma=sigma)

    truths = {
        "phase_noise_0.6": [noisy(ph, low, 0.6) for ph, low in zip(meshes, lows, strict=True)],
        "misroute_-2_0.3_noise_0.3": [
            0.7 * noisy(ph, low, 0.3) + 0.3 * noisy(ph, max(low - 2, 0), 0.3)
            for ph, low in zip(meshes, lows, strict=True)
        ],
        "out_of_family": [rng.dirichlet(np.full(MODES, 0.3)) for _ in meshes],
    }
    dark = [[0.0] * MODES for _ in meshes]
    return {name: score(arch, meshes, lows, draw(t), eta, dark)["verdict"] for name, t in truths.items()}


def rule_self_test() -> int:
    """The decision rule on synthetic truths over the S3 meshes (see synthetic_verdicts)."""
    verdicts = synthetic_verdicts()
    expected = {
        "phase_noise_0.6": "phase_noise",
        "misroute_-2_0.3_noise_0.3": "misroute_-2",
        "out_of_family": "no class fits",
    }
    if verdicts != expected:
        raise SystemExit(f"self-test: the decision rule read {verdicts}, not {expected}")
    print(f"rule self-test: decision rule {verdicts}")
    return 0


def static_self_test() -> int:
    """The static class is declared on a static truth and on no other.

    Uniform random phases are statistically the transpiler's output (section 7 of strategy.md), so 64 of
    them on the connected inputs stand in for a 64-setting campaign of four runs: 0.1 rad static offsets
    must be declared, and an exact dephasing ensemble at sigma 0.6 and an out-of-family distribution must
    not; the simulator's 16-setting S3 run must not either.
    """
    import numpy as np

    texts = computed_circuits(RUNS / S3_RUN)
    arch = run_architecture(decode(texts[0]))
    rng = np.random.default_rng([SEED, 11])
    connected = CONNECTED
    meshes = rng.uniform(0, 2 * math.pi, (64, len(phase_slots(arch))))
    lows = [connected[k % len(connected)] for k in range(64)]
    folds = [k // 16 for k in range(64)]
    ones = np.ones(MODES)
    dark = np.zeros((64, MODES))

    def draw(probabilities: list[Any]) -> Any:
        return np.array([rng.multinomial(SAMPLES_PER_SETTING, p / p.sum()) for p in probabilities])

    offsets = rng.normal(0, 0.1, meshes.shape[1])
    pairs = list(zip(meshes, lows, strict=True))
    truths = {
        "static_0.1": (draw([propagate(arch, list(ph + offsets), low)[0] for ph, low in pairs]), True),
        "dephasing_0.6": (draw([channel(arch, list(ph), low, sigma=0.6) for ph, low in pairs]), False),
        "out_of_family": (draw([rng.dirichlet(np.full(MODES, 0.3)) for _ in lows]), False),
    }
    seen = {}
    for name, (counts, want) in truths.items():
        record = static_cross_validation(arch, meshes, lows, counts, ones, dark, (0.1,), folds)
        seen[name] = record["by_tau"]["0.1"]
        if record["static_declared"] != want:
            raise SystemExit(f"self-test: the static class read {record} on the {name} truth")
    s3 = static_record([RUNS / S3_RUN])
    if s3["static_declared"]:
        raise SystemExit(f"self-test: the static class was declared on the simulator's S3 run: {s3}")
    print(f"static self-test: declared only on the static truth; {seen}")
    return 0


def efficiency_self_test() -> int:
    """Fitted efficiencies separate an instrument error from an optical one.

    Sixty-four uniform random meshes over the connected inputs in four folds stand in for a campaign of four
    runs. Two detector banks at different efficiency without offsets read ideal and declare no static offsets;
    the same efficiencies with 0.1 rad static offsets declare them and recover both; an ideal truth at flat
    efficiency scored with Q1's receipt t_out reads "no class fits" under the receipt-efficiency score and
    "ideal" under fitted efficiencies.
    """
    import numpy as np

    texts = computed_circuits(RUNS / S3_RUN)
    arch = run_architecture(decode(texts[0]))
    rng = np.random.default_rng([SEED, 13])
    meshes = rng.uniform(0, 2 * math.pi, (64, len(phase_slots(arch))))
    lows = [CONNECTED[k % len(CONNECTED)] for k in range(64)]
    folds = [k // 16 for k in range(64)]
    pairs = list(zip(meshes, lows, strict=True))
    truth = np.where(np.arange(MODES) < MODES // 2, 1.0, 0.5) * rng.uniform(0.8, 1.2, MODES)
    offsets = rng.normal(0, 0.1, meshes.shape[1])
    nominal = np.asarray([propagate(arch, list(ph), low)[0] for ph, low in pairs])
    shifted = np.asarray([propagate(arch, list(ph + offsets), low)[0] for ph, low in pairs])

    def draw(p: Any, eta: Any) -> list[list[int]]:
        return [list(map(int, rng.multinomial(SAMPLES_PER_SETTING, w / w.sum()))) for w in p * eta]

    instrument, both, flat = draw(nominal, truth), draw(shifted, truth), draw(nominal, np.ones(MODES))
    scans = parallel.ordered_map(Scan(arch, neighbours(arch)), pairs, min_items=2)
    seen: dict[str, Any] = {}
    read = efficiency_classes(scans, instrument, folds)
    static = efficiency_static(arch, meshes, lows, instrument, (0.1,), folds)
    seen["efficiency only"] = (read["verdict"], static["by_tau"]["0.1"])
    require(read["verdict"] == "ideal", f"self-test: an efficiency-only truth reads {read['verdict']}")
    require(not static["static_declared"], f"self-test: an efficiency-only truth declared static offsets: {static}")
    static = efficiency_static(arch, meshes, lows, both, (0.1,), folds)
    delta, eta = StaticEfficiencyFit(arch, meshes, lows, both).fit_joint(np.arange(64), 0.1)
    recovered = (float(np.corrcoef(delta, offsets)[0, 1]), float(np.corrcoef(np.log(eta), np.log(truth))[0, 1]))
    seen["efficiency and offsets"] = (static["by_tau"]["0.1"], [round(v, 3) for v in recovered])
    require(static["static_declared"], f"self-test: static offsets with efficiencies were not declared: {static}")
    require(
        recovered[0] >= 0.8 and recovered[1] >= 0.95, f"self-test: offsets and efficiencies recovered at {recovered}"
    )
    receipt = json.loads((RUNS / Q1_RUN / "submission.json").read_text(encoding="utf-8"))["perfs_at_plan"]
    t_out = receipt["Transmission per mode (%)"]["t_out"]
    preregistered = score(arch, [list(m) for m in meshes], lows, flat, t_out, [[0.0] * MODES for _ in lows])
    fitted = efficiency_classes(scans, flat, folds)
    seen["flat under t_out"] = (preregistered["verdict"], fitted["verdict"])
    require(
        preregistered["verdict"] == "no class fits",
        f"self-test: t_out scoring of a flat truth reads {preregistered['verdict']}",
    )
    require(fitted["verdict"] == "ideal", f"self-test: fitted efficiencies on a flat truth read {fitted['verdict']}")
    print(f"efficiency self-test: instrument and optical errors separate; {seen}")
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
    group.add_argument("--self-test-static", action="store_true")
    group.add_argument("--self-test-rule", action="store_true")
    group.add_argument("--static", type=Path, nargs="+", metavar=("OUT", "RUN"))
    group.add_argument("--check-static", type=Path, nargs="+", metavar=("OUT", "RUN"))
    group.add_argument("--self-test-efficiency", action="store_true")
    group.add_argument("--efficiency", type=Path, nargs="+", metavar=("OUT", "RUN"))
    group.add_argument("--check-efficiency", type=Path, nargs="+", metavar=("OUT", "RUN"))
    group.add_argument(
        "--followup", type=Path, nargs=5, metavar=("OUT", "PREREGISTRATION", "JOB02", "REPEAT", "ORIGINAL")
    )
    group.add_argument(
        "--check-followup", type=Path, nargs=5, metavar=("OUT", "PREREGISTRATION", "JOB02", "REPEAT", "ORIGINAL")
    )
    group.add_argument("--pair", type=Path, nargs=5, metavar=("OUT", "PREREGISTRATION", "FORM", "ENSEMBLE", "JOB02"))
    group.add_argument(
        "--check-pair", type=Path, nargs=5, metavar=("OUT", "PREREGISTRATION", "FORM", "ENSEMBLE", "JOB02")
    )
    group.add_argument("--self-test-bridge", action="store_true")
    group.add_argument("--self-test-dwell", action="store_true")
    group.add_argument("--dwell", type=Path, nargs=5, metavar=("OUT", "PREREGISTRATION", "D1", "D3", "LADDER"))
    group.add_argument("--check-dwell", type=Path, nargs=5, metavar=("OUT", "PREREGISTRATION", "D1", "D3", "LADDER"))
    group.add_argument("--bridge", type=Path, nargs=3, metavar=("OUT", "PREREGISTRATION", "BRIDGE"))
    group.add_argument("--check-bridge", type=Path, nargs=3, metavar=("OUT", "PREREGISTRATION", "BRIDGE"))
    args = parser.parse_args()
    try:
        if args.self_test:
            return self_test()
        if args.self_test_bridge:
            return bridge_self_test()
        if args.self_test_dwell:
            return dwell_self_test()
        if args.dwell or args.check_dwell:
            out, *inputs = args.dwell or args.check_dwell
            record = dwell_record(*inputs)
            if args.dwell:
                out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
            else:
                close_relative(json.loads(out.read_text(encoding="utf-8")), record)
            print(
                f"{out}: dwell {'written' if args.dwell else 'replays'}, "
                + ", ".join(f"{k} {record[k]['verdict']}" for k in ("d1", "d2", "d3", "d4"))
            )
            return 0
        if args.bridge or args.check_bridge:
            out, *inputs = args.bridge or args.check_bridge
            record = bridge_record(*inputs)
            if args.bridge:
                out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
            else:
                close_relative(json.loads(out.read_text(encoding="utf-8")), record)
            print(
                f"{out}: bridge {'written' if args.bridge else 'replays'}, {record['branch']}, "
                f"q1 {record['bridges']['q1'].get('verdict')}, family {record['family_verdict']}"
            )
            return 0
        if args.self_test_static:
            return static_self_test()
        if args.self_test_rule:
            return rule_self_test()
        if args.self_test_efficiency:
            return efficiency_self_test()
        if args.pair or args.check_pair:
            out, *inputs = args.pair or args.check_pair
            record = pair_record(*inputs)
            if args.pair:
                out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
            else:
                close_relative(json.loads(out.read_text(encoding="utf-8")), record)
            print(
                f"{out}: pair {'written' if args.pair else 'replays'}, form {record['form']['verdict']}, "
                f"seed selects mesh {record['ensemble']['seed_selects_mesh']}"
            )
            return 0
        if args.followup or args.check_followup:
            out, *inputs = args.followup or args.check_followup
            record = followup_record(*inputs)
            if args.followup:
                out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
            else:
                close_relative(json.loads(out.read_text(encoding="utf-8")), record)
            print(
                f"{out}: follow-up {'written' if args.followup else 'replays'}, job-02 {record['job_02']['verdict']}, "
                f"repeat {record['job_03_repeat']['verdict']}"
            )
            return 0
        if args.efficiency or args.check_efficiency:
            out, *runs = args.efficiency or args.check_efficiency
            record = efficiency_record(runs)
            if args.efficiency:
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
            else:
                efficiency_close(json.loads(out.read_text(encoding="utf-8")), record)
            print(
                f"{out}: fitted efficiencies {'written' if args.efficiency else 'replay'}, "
                f"verdict {record['verdict']}, static declared {record['static']['static_declared']}"
            )
            return 0
        if args.static or args.check_static:
            out, *runs = args.static or args.check_static
            record = static_record(runs)
            if args.static:
                out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
            else:
                static_close(json.loads(out.read_text(encoding="utf-8")), record)
            print(
                f"{out}: static offsets {'written' if args.static else 'replay'}, declared {record['static_declared']}"
            )
            return 0
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
