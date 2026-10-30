# Consultation brief: four failed A_5 fiber-cone / Rees computations

Act as an independent computer-algebra consultant. Read only; write nothing except your final answer.
A Claude analysis agent is writing `first-principles-plan.md` in this directory in parallel; give an
independent view, and where that file already exists, critique it.

## Read first
- `docs/local/a5-failed-runs/purpose.md` FIRST: what the runs measure and why. Judge every option by whether it delivers that object (the exceptional-fiber limit set roadmap item 6 needs), not only by whether it finishes.
- `docs/local/a5-failed-runs/` : `inputs/` (the Singular/msolve inputs), `kaggle-pack-a/`, `azure-vm2/` (logs, memory traces), `probes/`.
- `docs/local/a5-iso-np-h3-analysis/algebra-options.md` and `execution-options.md` (a worked analysis of the sister Iso->N+ degree-3 run, including the Nakayama quadric reduction 969 -> 265 cubic generators).
- `AGENTS.md` section "Computer algebra"; `docs/runbooks/compute-flags.md` (measured flag rows, msolve rows 164-168); `docs/evidence/a5-strata-regularity/README.md`.

## The failures
1. Kaggle pack A, X+ -> N+ fiber: out of memory after the degree-2 count h2 = 51.
2. Kaggle pack A, X- -> N- fiber: hit the time limit.
3. Kaggle pack A, Iso K2: hit the time limit (partial: 69 relations, K2 degree 23).
4. Azure VM2: E8-bar -> N+ msolve variants crash growing hash tables (~2^28 entries); W8 N- fiber Singular "no more memory" near 80 GiB.

## Resources
- Host: 16 GiB-cgroup-capped Singular runs are routine; RTX 4070 Ti (12 GiB); multi-core CPU; ~64+ GiB RAM shared.
- Kaggle: 4-vCPU CPU (~30 GiB), T4 x2, TPU v5e kernels, 12 h sessions.
- Azure: FX4mds_v2 (4 vCPU, 84 GiB), cap 4 vCPU per region (eastus, westus2); a new VM needs an approved case.
- GitHub Actions runners (4 vCPU, 16 GiB, 6 h).
- Installed: Singular 4.4.1, Macaulay2, msolve 0.11.0, FLINT 3.6 (+ python-flint), Sage 10.10, giac, LinBox, fflas-ffpack, gfan, CuPy, nvmath, magma-cuda, cuQuantum 26.09.
- Buildable via `~/Github/PKGBUILDs` (Arch makepkg tree; each dir is one package; see its README.md) or AUR/paru: Normaliz, 4ti2, CoCoA-5, msolve master, OSCAR.jl, Macaulay2 packages (FastMinors, ReesAlgebra, MultigradedImplicitization), Gfan, M4RI/M4RIE, any GitHub project we can package.

## Answer, per failure
1. What invariant the run computes, and where the cost blows up (Groebner degree, module rank, hash size, coefficient growth).
2. At least two equivalent reformulations that keep the invariant (degree truncation, special-fiber-only linear algebra over F_p, symmetry reduction by the A_5 / Weyl action, multigrading, multi-modular + CRT, sparse Macaulay-matrix rank with block Wiedemann on GPU, primary decomposition first, Hilbert series via Normaliz/toric degeneration, implicitization by interpolation).
3. Exact commands/scripts and resource limits, and a falsifier against the partial outputs above.
4. Any change to the mathematical formulation itself that makes the run feasible, saying explicitly whether it preserves the invariant or changes the question.
5. Packages or GitHub projects worth building, with why.
Rank the options by expected chance of success per compute-hour. Be concrete and cite file:line for every claim read from a file.
