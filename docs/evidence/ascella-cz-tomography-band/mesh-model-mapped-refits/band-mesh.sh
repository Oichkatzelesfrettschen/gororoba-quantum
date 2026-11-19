#!/bin/sh
# Run mesh_model.py serial (committed) and mapped (patched) and compare the two outputs.
set -u
cd ~/a5/gq-band
out=~/a5/band-mesh-out; mkdir -p "$out"; rm -f "$out/done"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
M=docs/evidence/ascella-cz-tomography-band/mesh_model.py
run() { t0=$(date +%s); ~/a5env/bin/python "$M" "$out/$1.json" > "$out/$1.log" 2>&1; echo "$1 rc=$? seconds=$(( $(date +%s) - t0 ))" >> "$out/summary.txt"; }
: > "$out/summary.txt"
run serial
cp SCRATCH/mesh_model.patched.py "$M"
run mapped
if cmp -s "$out/serial.json" "$out/mapped.json"; then echo "outputs identical" >> "$out/summary.txt"; else echo "outputs DIFFER" >> "$out/summary.txt"; fi
if cmp -s "$out/serial.json" docs/evidence/ascella-cz-tomography-band/mesh-model.json; then echo "serial equals retained" >> "$out/summary.txt"; else echo "serial differs from retained" >> "$out/summary.txt"; fi
touch "$out/done"
