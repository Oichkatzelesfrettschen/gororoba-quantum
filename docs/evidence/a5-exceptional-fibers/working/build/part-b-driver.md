# Part B: the degree-by-degree driver and the certificate layer

Goal: `fiber_cone_driver.py` (method A by degree with receipts) and `fiber_certificates.py` (completion statuses).
Inputs are Singular header files (ring in t over F_p, `number I`, `ideal J`, `ideal G`), as in
docs/local/a5-failed-runs/runs/e8vb_a2/input.sing lines 1-4; Part A builds the emitter in parallel, so take a header
path as the CLI input.
Driver:
- `--header FILE --degree d --previous-relations FILE --out DIR --prime p`. Degree 1 and 2 use all products; d >= 3
  uses kbase(std(K_{<d}), d) normal monomials and builds products reducing mod J after each factor (runs/s1/input.sing).
- Normal forms of P_d modulo std(J + m P_d) in dp; exact F_p rank and left kernel with python-flint (merge the two
  parsers of probes/rank_nf.py and relations_nf.py into one; parse Singular's printed polynomials exactly).
- Verify each extracted relation by exact membership: sum c_b P_b reduces to 0 modulo std(J + m P_d) (one Singular
  call), and fail otherwise.
- Receipt JSON per degree: input sha256, prime and root, generator count and order hash, ordered target monomials,
  normal-form file sha256, matrix rows/cols/nonzeros, rank h_d, relation count and file sha256, membership check
  result, per-stage wall seconds (not cumulative), memory peak (run Singular via `systemd-run --user --wait
  --pipe -p MemoryMax=...`, which reports the peak, or read the scope's memory.peak), tool versions. Repo-relative
  paths only. Status field: "degree-certified".
- Pool independent (pair, degree-1/2) items through parallel.py only with an explicit memory-admission bound, and
  record why the pool is bounded.
Certificates (`fiber_certificates.py`), each a separate status, never merged:
- "candidate-ideal": given relations K, build Rees lifts (cofactors over t via Singular `lift` or division) to get L
  in k[t,y]; check H in L, L in ker(y_j -> a G_j) by substitution, and L : g = L; if all hold, L = H : g^inf and the
  special fiber is (L + (t)) restricted to y: status "scheme-equal". Measure cost on E8-bar->VB before claiming it is
  cheaper than saturation.
- "dense-family": sample genuine limits of the kernel map along arcs into the boundary point and test containment in
  each prime of V(K); with a certified-dimension argument that is "support-equal"; without it, report "support
  lower bound". Every random draw takes its seed via qrng_seeds (qrng:<draw>#<index>); add the ledger rows the seed
  rule requires, or leave the random route unimplemented and say so if no draw is available.
- "bounded Hilbert function": there is no proven relation-type bound in the tree. Do not ship a stub; record it as a
  scope cut in the report.
Validation (3G, 15 min, one job at a time): E8-bar->VB degrees 1-3 must reproduce h = 10, 34, 80 and the relation
ideal of runs/e8vb_a2/k2.rel; X- degree 2 must reproduce h2 = 51 and the 69-relation ideal of
kaggle-pack-a/xm_nm/xm_nm_fiber.rel. Run the candidate-ideal certificate on E8-bar->VB and report time, memory and
outcome. Propose (do not edit) ci/gates.json entries: VB degree 2 as a fast gate (<= 15 s), X degree 2 as full tier.
