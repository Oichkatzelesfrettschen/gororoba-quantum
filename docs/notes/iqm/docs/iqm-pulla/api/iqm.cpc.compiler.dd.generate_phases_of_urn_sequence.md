> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.dd.generate_phases_of_urn_sequence.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.dd.generate_phases_of_urn_sequence.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ef4b28f8de2dd8405c4ee8543734d3d82180af14da1c7de8d12440b763189ed2.

# iqm.cpc.compiler.dd.generate_phases_of_urn_sequence

iqm.cpc.compiler.dd.generate_phases_of_urn_sequence(*n*)  
Generate PRX gate phases for the URn sequence.

More information on the URn sequence is available in \[[1](https://docs.iqm.tech/4.7/iqm-pulla/references.html#id2 "Nic Ezzell, Bibek Pokharel, Lina Tewala, Gregory Quiroz, and Daniel A. Lidar. Dynamical decoupling for superconducting qubits: a performance survey. Phys. Rev. Appl., 20:064027, Dec 2023. arXiv:2207.03670, doi:10.1103/PhysRevApplied.20.064027.")\], at the end in Appendix A.1.

Parameters:  
**n** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of single qubit PRX pulses with different phases to apply, must be a positive even number.

Returns:  
Phases to be used by the URn sequence.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]
