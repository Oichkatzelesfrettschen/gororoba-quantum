# Current observable reconciliation

The current external theorem contracts extend open_gororoba base
`4706d40eafa524957a9b20384a6a7346fe8536a1` and bind retained inputs from
quantum commit `a3d95ab60b25c4a6f18e5ff7c0435b4947abceb8`.
The [retained delta](observable-contracts-delta.txt) records the current proof
scope and replay entry point. The [source snapshot](observable-contracts.tar.gz)
retains 235 files: the complete 29-source receipt closure, 21 source-bound
witnesses and receipt specifications, 25 binding assets, the 160-declaration
manifest, validator sources and raw compile/kernel/assumption logs.
[Retrieval identity](observable-contracts-source.json) pins the external commit
and archive digest; [member hashes](observable-contracts.files.sha256) bind
every extracted file. The archive preserves the external repository paths. The historical certificate
bundle retains its fixed-count application and Rocq 9.2 / OCaml 5.5.0 receipts.
The external build uses Rocq 9.3.0, OCaml 5.5.1 and Stdlib 9.2.0.

The external manifest binds 160 declarations across 11 scoped sources to basis,
normalization, original-byte circuit archive digests, little-endian register
maps and observables. Mathematical-only results mark physical fields
inapplicable. QPY byte identity proves archive provenance; circuit semantic
correspondence remains an explicit obligation.

The terminal certificate proves a finite Bernoulli degree-ten concentration
bound and a union bound for all 32 means with 8192 samples each. The outward
radius is exactly 0.021, compared with the historical floating analysis radius
0.02089696308600546. Under the common terminal-channel null and declared
within-mean IID Bernoulli marginal laws, the pre-data false-rejection probability
is at most 0.05. Dependence across means is unrestricted. The selected hardware
s1/s3 counts 2964/8192 and 4911/8192, and replay s1/s3 counts 4067/8192 and
4057/8192, give exact margin 156109/1024000 after subtracting four radii.
The certificate establishes a conditional sampling statement, rather than a
posterior null probability for fixed observations.

The signed-coherence proof uses c0=branch, c1=work_a, c2=work_b and c3=spectator.
With standard Pauli Y and trace(rho O), the odd matrix element is
`rho[01,10]=(XX+YY+i*(XY-YX))/4`. Subnormalized branches retain their weights;
spectator correlations remain allowed. The proof includes ordered Z rotation,
symmetric independent assignment attenuation, nuisance bounds and additive-drift
nonidentifiability. Physical Born interpretation requires positive branch blocks
with combined trace one. Physical assignment mixing requires an error probability
in [0,1] and the independent-error mixture model; the separate factorization
predicate is not proved to induce that matrix mixture.

The reconstructed coefficients remain immediate
`(0.413330078125,-0.006103515625)`, matched_idle
`(0.15478515625,-0.34130859375)` and measure_reset
`(0.17724609375,-0.341064453125)`. The registered measure/reset quadrature
comparison remains unresolved. Device drift, setting bias, leakage, crosstalk and
gate error remain nuisance mechanisms. Work-qubit coherence within recorded
classical branches differs from coherence between branches.

The change reads retained files and runs local proof and document checks. Quantum
acquisition, simulator execution and provider service calls remain outside scope.

To inspect and verify the retained snapshot without retrieving upstream bytes:

```sh
snapshot_dir="$(mktemp -d)"
tar -xzf docs/evidence/formal_certificates/observable-contracts.tar.gz -C "$snapshot_dir"
(cd "$snapshot_dir" && sha256sum -c "$OLDPWD/docs/evidence/formal_certificates/observable-contracts.files.sha256")
```

The per-target receipts retain exact compile and checker arguments, source
closures, source/object digests and declaration assumptions. A fresh kernel replay
requires the recorded Rocq 9.3.0 / OCaml 5.5.1 / Stdlib 9.2.0 toolchain. Running
the Rust validator uses the pinned external workspace, because the archive retains
the validator and its inputs rather than every unrelated Rust dependency crate.
The snapshot verifies retained evidence; acquisition and physical model validation
remain separate obligations.
