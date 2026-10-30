"""Export the E8bar->VB Rees system over F_p with sqrt(-1) in F_p and eliminate the Rees variable with msolve."""
import json, sys, subprocess, time
from pathlib import Path
import sympy
W = Path.home() / "worktrees/IBMQuantum/a5-kernel-attachments/docs/evidence/a5-kernel-attachments"
sys.path.insert(0, str(W))
import higher_order_holomorphic_gauss_fibers as h  # noqa: E402  (trashed; replaced below)
