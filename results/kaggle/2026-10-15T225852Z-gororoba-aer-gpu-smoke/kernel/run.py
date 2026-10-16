
import base64, hashlib, io, json, os, platform, subprocess, sys, time, zipfile
from pathlib import Path

PINS = ['qiskit==2.5.2', 'qiskit-aer-gpu-cu11==0.17.2']
ENTRY = None
ARGS = []
SMOKE = True
SMOKE_QUBITS = 14
BUNDLE = "UEsFBgAAAAAAAAAAAAAAAAAAAAAAAA=="

out = Path("/kaggle/working/output")
out.mkdir(parents=True, exist_ok=True)
pip = subprocess.run([sys.executable, "-m", "pip", "install", "-q", *PINS], capture_output=True, text=True)
(out / "pip.txt").write_text(pip.stdout + pip.stderr)
if pip.returncode:
    raise SystemExit(f"pip install failed: {pip.returncode}")
repo = Path("/kaggle/working/repo")
zipfile.ZipFile(io.BytesIO(base64.b64decode(BUNDLE))).extractall(repo)
before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in repo.rglob("*") if p.is_file()}

from importlib.metadata import version
import qiskit_aer
env = {
    "python": platform.python_version(),
    "packages": {name: version(name) for name in ("qiskit", "qiskit-aer-gpu-cu11", "numpy", "scipy")},
    "aer_devices": list(qiskit_aer.AerSimulator().available_devices()),
    "gpu": subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"],
                          capture_output=True, text=True).stdout.strip().splitlines(),
}
(out / "environment.json").write_text(json.dumps(env, indent=1) + "\n")
print(json.dumps(env), flush=True)

if SMOKE:
    from qiskit import QuantumCircuit, transpile
    from qiskit_aer import AerSimulator
    qc = QuantumCircuit(SMOKE_QUBITS)
    qc.h(0)
    for q in range(SMOKE_QUBITS - 1):
        qc.cx(q, q + 1)
    qc.measure_all()
    sim = AerSimulator(method="density_matrix", device="GPU")
    start = time.time()
    counts = sim.run(transpile(qc, sim), shots=1024, seed_simulator=7).result().get_counts()
    smoke = {"qubits": SMOKE_QUBITS, "method": "density_matrix", "device": "GPU",
              "wall_seconds": round(time.time() - start, 3), "counts": counts}
    (out / "smoke.json").write_text(json.dumps(smoke, indent=1, sort_keys=True) + "\n")
    print(json.dumps(smoke), flush=True)
    raise SystemExit(0)

run_env = dict(os.environ, GOROROBA_AER_DEVICE="GPU", PYTHON=sys.executable)
proc = subprocess.run([sys.executable, "-B", ENTRY, *ARGS], cwd=repo, env=run_env, capture_output=True, text=True)
(out / "stdout.txt").write_text(proc.stdout)
(out / "stderr.txt").write_text(proc.stderr)
print(proc.stdout[-4000:], proc.stderr[-4000:], sep="\n", flush=True)
for path in repo.rglob("*"):
    if path.is_file() and before.get(path) != hashlib.sha256(path.read_bytes()).hexdigest():
        target = out / "repo" / path.relative_to(repo)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
(out / "exit.json").write_text(json.dumps({"returncode": proc.returncode}) + "\n")
raise SystemExit(proc.returncode)
