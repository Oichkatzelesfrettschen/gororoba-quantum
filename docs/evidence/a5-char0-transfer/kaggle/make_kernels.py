"""Write the Kaggle CPU kernels that run the characteristic-0 checks of X- -> N- off the build host.

Each kernel is runner.py with its configuration in CONFIG_B64: it clones the public repository at the integration
branch, runs quadric_lift.py or truncation_check.py at N = 22 unchanged inside a 12-hour CPU session, copies the
driver's record and exits 1 unless the driver exited 0 with a verdict. Run from the repository root:
"$PYTHON" docs/evidence/a5-char0-transfer/kaggle/make_kernels.py
"""

import base64
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OWNER = "probablyeric"
BRANCH = "integration/gororoba-quantum-ultrareview"
REPO = "https://github.com/Oichkatzelesfrettschen/gororoba-quantum"

JOBS = {
    "a5-char0-xm-quadrics": (
        ["docs/evidence/a5-char0-transfer/quadric_lift.py", "--slug", "xm-nm", "--timeout", "41000"],
        "quadrics-xm-nm.json",
    ),
    "a5-char0-xm-truncation-n22": (
        [
            "docs/evidence/a5-char0-transfer/truncation_check.py",
            "--slug",
            "xm-nm",
            "--order",
            "22",
            "--timeout",
            "20000",
        ],
        "truncation-xm-nm-n22.json",
    ),
}


def kernel(slug: str, args: list[str], record: str, out: Path = HERE) -> None:
    """Write OUT/SLUG/SLUG.py (runner.py with its configuration in CONFIG_B64) and its kernel-metadata.json."""
    d = out / slug
    d.mkdir(parents=True, exist_ok=True)
    config = {"branch": BRANCH, "repo": REPO, "args": args, "record": record}
    blob = base64.b64encode(json.dumps(config).encode()).decode()
    chunks = "".join(f'    "{blob[i : i + 100]}"\n' for i in range(0, len(blob), 100))
    runner = (HERE / "runner.py").read_text()
    if runner.count('CONFIG_B64 = ""\n') != 1:
        raise SystemExit("runner.py must hold exactly one CONFIG_B64 placeholder")
    (d / f"{slug}.py").write_text(runner.replace('CONFIG_B64 = ""\n', f"CONFIG_B64 = (\n{chunks})\n"))
    meta = {
        "id": f"{OWNER}/{slug}",
        "title": slug,
        "code_file": f"{slug}.py",
        "language": "python",
        "kernel_type": "script",
        "is_private": True,
        "enable_gpu": False,
        "enable_internet": True,
        "dataset_sources": [],
        "kernel_sources": [],
        "competition_sources": [],
    }
    (d / "kernel-metadata.json").write_text(json.dumps(meta, indent=1) + "\n")


def main(out: Path = HERE) -> None:
    for slug, (args, record) in JOBS.items():
        kernel(slug, args, record, out)


if __name__ == "__main__":
    main()
