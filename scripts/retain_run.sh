#!/bin/sh
# Retain one collected IBM run with every register that enumerates retained jobs, in one command: the runtime seed
# rows, a fresh observation of the run's instance, that instance's retention audit, the submitted-circuit row and
# the ghost calibration index of a default-instance run, and the run's acquisition. The claim that cites the run
# stays the operator's text: every acquisition must support a claim, so research_state.py --write renders the views
# once that claim is written. research_state.py --check fails while an audit lists a run awaiting observation, so a
# run retained without this sequence cannot pass the registry.
#
# Each register appends: the audit rows and comparison rows are per job and the claims and the algebra-device
# bundle bind job records (docs/design/retention-bookkeeping-per-record.md), so no earlier evidence changes.
#
# Usage: sh scripts/retain_run.sh RUN ID FAMILY QUESTION   (from the repository root; GOROROBA_IBM_ACCOUNT selects
#        the account as for the run's --collect). Exit 0 retained, 1 a step failed, 2 usage.
set -eu

PYTHON=${PYTHON:-python3}
export PYTHON
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096

[ $# -eq 4 ] || {
	echo "usage: sh scripts/retain_run.sh RUN ID FAMILY QUESTION" >&2
	exit 2
}
run=${1%/}
id=$2
family=$3
question=$4
"$PYTHON" scripts/reconcile_qpu_inventory.py --retention-preflight "$run"
new=
cleanup() { if [ -n "$new" ]; then rm -f "$new"; fi; }
trap cleanup EXIT
trap 'exit 130' INT TERM HUP

"$PYTHON" ci/seed_provenance.py --add-runtime
observed=$("$PYTHON" scripts/observe_qpu_job_inventory.py --out results/live/qpu-job-inventory.json)
echo "$observed"
inventory=$(echo "$observed" | sed -n 's/.*; wrote //p')
[ -f "$inventory" ] || {
	echo "retain_run: the observation named no inventory file" >&2
	exit 1
}
audit=$(echo "$inventory" | sed 's/qpu-job-inventory/qpu-job-retention-audit/')
# reconcile_qpu_inventory.py creates its output exclusively, so the audit is written beside the old one and moved
# over it; git keeps the replaced bytes.
new="$audit.new"
"$PYTHON" scripts/reconcile_qpu_inventory.py --snapshot "$inventory" --out "$new"
mv "$new" "$audit"
new=
if [ "$audit" = results/live/qpu-job-retention-audit.json ]; then
	"$PYTHON" scripts/compare_submitted_circuits.py --append
	"$PYTHON" scripts/ghost_calibrations.py --add
fi
"$PYTHON" scripts/research_state.py --add-acquisition "$id" ibm "$run" "$family" "$question"
echo "retain_run: retained $run as $id; write the claim that cites it, then run scripts/research_state.py --write"
