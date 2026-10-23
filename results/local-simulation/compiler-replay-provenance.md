# Compiler replay provenance

Three follow-on JSON records retain their discovered bytes. Execution
authorship, launch commands, launch time and the asserted authorization
remain unverified; filesystem timestamps and matching producer digests do
not establish those facts. The records' `authorization` strings are retained
claims, rather than a new approval receipt or authority to launch a job.

- `photonic-compiler-crosscheck-perceval-1-3-1/photonic.json` contains 128
  passing optical settings. Its probabilities, operators' maximum residuals,
  frozen source identities and seeded synthetic counts exactly reproduce
  `physical-photonic-compiler-crosscheck/photonic.json` after excluding
  reported timing and producer/interpreter metadata.
- `photonic-compiler-crosscheck-perceval-1-3-1/qi.json` reproduces all 24
  source/default-writer cases in
  `validated-terminal-unitary-compiler-crosscheck/qi.json`. Twenty meet the
  numerical criterion; the same four default-writer residuals remain.
- `cqasm-fullprecision-compiler-crosscheck/qi.json` reproduces all 24 passing
  cases in `fullprecision-compiler-crosscheck/qi.json`, including compiled
  programs, terminal probes, amplitudes and shot histograms.

Each follow-on directory contains a `producer.py` snapshot whose SHA-256 is
`9448f2a10fcc59c860ea81ce2008926efe9a2a7a84ee9f772b451918fc25faa5`, matching
the recorded producer and the committed cross-check script. The full-precision
directory also retains the recorded `exporter.py` bytes. Matching source
identities bind the records' declared implementation; they leave execution
authorship unverified.

The offline replay admits these three records explicitly. It verifies their
producer/exporter bindings and compares every scientific field with the
corresponding admitted record using canonical JSON with scalar types preserved.
Boolean or floating replacements for integer counts fail the comparison.
The comparison excludes only top-level `python`,
`runner_sha256` and `elapsed_seconds`, and each optical row's `seconds`.
Timing and interpreter values remain reported metadata. The existing QI
denominator, frozen-source and numerical checks also cover both follow-on
QI records. The original records and producer snapshots retain their bytes.

The shell wrapper retains its original contents with owner execution enabled.
Its regression test checks that permission independently of the simulation
records.
