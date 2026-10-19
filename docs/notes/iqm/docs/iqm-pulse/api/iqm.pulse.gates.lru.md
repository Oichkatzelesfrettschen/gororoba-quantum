> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.lru.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.lru.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f1d2c7788e8d07b8c0567803c924395154f43d20b2cafc6efa22fa5834bb37b7.

# lru

Full path: iqm.pulse.gates.lru

Qubit leakage reduction unit.

The leakage reduction unit (LRU) is a non-unitary quantum channel that removes population from the \\\|2\rangle\\ state of a qubit. If there is no population in the \\\|2\rangle\\ state, the computational subspace is left unchanged (LRU will act as identity on \\\mathrm{Span} \\ \\\|0\rangle, \|1\rangle\\\\). However, any leaked population is moved to one of the computational states, thus changing the computational subspace.

Different LRU implementations may move the population to different states within the computational subspace.

Classes

|  |  |
|----|----|
| [`LRU_F0G1`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.lru.LRU_F0G1.html#iqm.pulse.gates.lru.LRU_F0G1 "iqm.pulse.gates.lru.LRU_F0G1") | Leakage reduction unit implementation driving the \\\|f0\rangle \leftrightarrow \|g1\rangle\\ transition. |

Inheritance

![Inheritance diagram of iqm.pulse.gates.lru](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-d0d1c1111315682a7543fa60a2a770aacf9b4c2d.png)
