# Brief: run the portable least-squares precision sweep on remote hosts

Spawn no subagents. Submit no provider job. Edit no tracked file in any repository. Do not commit or push. Change no
SSH, system or account configuration on any host; install only into a venv under the remote home directory.

Local worktree: `W=<worktree>`.
Bundle: `$W/docs/local/bundle/gq-sweep.tar.gz` (the sweep scripts plus the producer inputs; extracts to a
repository-shaped tree). Build-host inputs: `$W/docs/local/fp-inputs.npz`.

## Per Linux or macOS host (SSH alias given in your prompt; LABEL given in your prompt)

1. `ssh ALIAS 'mkdir -p ~/fp-sweep'`, then `scp` the bundle and fp-inputs.npz there (rename the npz
   `build-host-inputs.npz`), and `ssh ALIAS 'cd ~/fp-sweep && tar -xzf gq-sweep.tar.gz'`.
2. Record `uname -a`, `nproc`, `free -m` (macOS: `sysctl hw.memsize hw.ncpu machdep.cpu.brand_string`),
   `cat /proc/loadavg`, and on Linux `grep -o -m1 -w 'avx512f\|avx2\|asimd' /proc/cpuinfo | sort -u`.
3. venv: `python3 -m venv ~/fp-venv && ~/fp-venv/bin/python -m pip install numpy==2.5.4 scipy==1.18.1
   python-flint==0.9.0 numpy-quaddtype==1.0.0 threadpoolctl==3.7.0 qiskit==2.6.2 sympy==1.14.0 rustworkx==0.18.1`.
   If a pin has no wheel for the host, retry that one package unpinned, and report the version that installed.
   If numpy-quaddtype will not install, continue without it (its rows skip).
4. Independent inputs: `cd ~/fp-sweep && ~/fp-venv/bin/python docs/evidence/least-squares-precision/fp_export.py
   host-inputs.npz --host-label LABEL > export.log 2>&1`. Then compare its five `inputs_sha256` digests with the
   build host's: `~/fp-venv/bin/python -c "import numpy,json,sys;[print(f, json.dumps(numpy.load(f,
   allow_pickle=True)['provenance'].item(), sort_keys=True)) for f in sys.argv[1:]]" host-inputs.npz
   build-host-inputs.npz`. Report equal or which digests differ. If export fails, report the last 20 lines of
   export.log and use build-host-inputs.npz for the sweep.
5. Sweep, in the background on the host so an SSH drop does not kill it:
   `nohup sh -c 'D=docs/evidence/least-squares-precision; P=~/fp-venv/bin/python; $P -u $D/fp_sweep.py
   host-inputs.npz $D/hosts/LABEL-quick.jsonl --host-label LABEL --quick --idle-wait > quick.log 2>&1;
   $P -u $D/fp_sweep.py host-inputs.npz $D/hosts/LABEL-full.jsonl --host-label LABEL --idle-wait > full.log 2>&1;
   echo done > done.flag' > /dev/null 2>&1 &`
   On a host whose prompt says quick-only, run only the first line. Poll `ls ~/fp-sweep/done.flag` every few
   minutes with short SSH commands (each `ssh -o ConnectTimeout=15`). Hard deadline: given in your prompt.
6. Copy `docs/evidence/least-squares-precision/hosts/LABEL-*.jsonl` and `export.log` back into
   `$W/docs/evidence/least-squares-precision/hosts/` (rename export.log to `LABEL-export.log`).
7. Leave the remote ~/fp-sweep and ~/fp-venv in place.

## Windows native (only when your prompt names it)

Use `ssh ALIAS powershell -NoProfile -Command ...`. Python must already exist (`py -0p` or `python --version`); if it
does not, report that and stop for that host. Use the build-host-inputs.npz (fp_export cannot run on Windows), and
`--cap none`. Same venv packages minus qiskit, sympy, rustworkx.

## Report (your final message)

Per host: label, CPU model, ISA flags, cores, memory, installed versions, export result and digest comparison, row
counts of each jsonl, skipped configurations with reasons, any error, wall time of the sweep, and load average range.
