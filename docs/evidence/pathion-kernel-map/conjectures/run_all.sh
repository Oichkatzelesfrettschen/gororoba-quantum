#!/bin/sh
# Regenerates every log and derived array of this directory in dependency order, from any working directory.
# Usage: PYTHON=/path/to/python sh run_all.sh [SCRIPT_STEM ...]   (no argument runs every step)
set -eu
PYTHON=${PYTHON:-python3}
export PYTHON
GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
export GLIBC_TUNABLES
here=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
cd "$here"
tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT

# step LOG SCRIPT [ARG]: run one script and keep its stdout as LOG only when it exits zero.
step() {
	log=$1
	shift
	if [ -n "${ONLY:-}" ] && ! printf '%s\n' "$ONLY" | grep -qx "$log"; then
		return 0
	fi
	"$PYTHON" "$@" >"$tmp"
	cp "$tmp" "$log.txt"
}

ONLY=$(printf '%s\n' "$@")
step mirror_test mirror_test.py
step mirror_test_sim mirror_test.py ../../../../results/quandela/runs/2026-11-07T002936Z-sim_ascella-ascella_pathion_coset_block_pairs-sim-00
step c1_mesh c1_mesh.py
step c1_observed c1_observed.py
step c1_predecessor c1_predecessor.py
step c1_phase c1_phase.py
step c1_phase_eq c1_phase_eq.py
step c1_anchor c1_anchor.py
step c1_controls c1_controls.py
step c1_static c1_static.py
step c1_heldout c1_heldout.py
step c1_static_null c1_static_null.py
step c2_scale c2_scale.py
step c2_algebra c2_algebra.py
step c2_mech c2_mech.py
step c2_resid_fez c2_resid.py fez
step c2_resid_marrakesh c2_resid.py marrakesh
step c2_resid_informative c2_resid_informative.py
step c2_stopped c2_stopped.py
step c2_tuna c2_tuna.py
step c3_readout c3_readout.py
step c3_walsh c3_walsh.py
step c3_corr c3_corr.py
step c3_zz c3_zz.py
step c3_mech2 c3_mech2.py
step c3_depol c3_depol.py
step c3_multi c3_multi.py
step c2_tuna_mech c2_tuna_mech.py
step c2_overrotation c2_overrotation.py
step d1_ibm_overrotation d1_ibm_overrotation.py
step d2_null_offset d2_null_offset.py
step d3_crosstalk d3_crosstalk.py
step d4_four_term d4_four_term.py
step c2_one_cz_mech c2_one_cz_mech.py
step c2_one_cz_twins c2_one_cz_twins.py
