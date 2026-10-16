# Citing Quantum Inspire

Quantum Inspire asks for one reference, given verbatim on its reference page
and its quick guide ([site/reference.md](site/reference.md),
[live](https://www.quantum-inspire.com/reference/);
[site/kbase_quick-guide.md](site/kbase_quick-guide.md),
[live](https://www.quantum-inspire.com/kbase/quick-guide/); retrieved
2026-10-16 UTC):

> QuTech. (2025). Quantum Inspire Home. Retrieved from Quantum Inspire:
> https://www.quantum-inspire.com/

A paper that reports runs on a specific backend also cites that backend's
publication and the software that compiled and simulated the job. Every
BibTeX entry below was built from the DOI registration (doi.org BibTeX
content negotiation and the Crossref works API) or from the arXiv DataCite
DOI record, fetched 2026-10-16; a field those records lack is left out, and
each entry's comment names any field taken from another source. Non-ASCII
names use TeX escapes.

## Platform

The SPIE 2020 paper is the platform description QI lists first among its
background papers and the fact sheet's reference [1].

```bibtex
% QI's prescribed reference (site/reference.md); not a DOI-registered work.
@misc{QuTech2025QuantumInspire,
  author       = {{QuTech}},
  title        = {Quantum Inspire Home},
  year         = {2025},
  howpublished = {\url{https://www.quantum-inspire.com/}},
  note         = {Retrieved from Quantum Inspire}
}

% doi.org and Crossref. Volume 11324 comes from the SPIE URL QI links and the
% Spin-2+ fact sheet, which also gives article 113240J; Crossref's page field
% (17) is a page count and is omitted.
@inproceedings{Last2020QuantumInspire,
  author    = {Last, Thorsten and Samkharadze, Nodar and Eendebak, Pieter and Versluis, Richard and Xue, Xiao and Sammak, Amir and Brousse, Delphine and Loh, Kelvin and Polinder, Henk and Scappucci, Giordano and Veldhorst, Menno and Vandersypen, Lieven and Maturova, Klara and Veltin, Jeremy and Alberts, Garrelt},
  title     = {Quantum Inspire: QuTech's platform for co-development and collaboration in quantum computing},
  booktitle = {Novel Patterning Technologies for Semiconductors, MEMS/NEMS and MOEMS 2020},
  editor    = {Panning, Eric M. and Sanchez, Martha I.},
  series    = {Proc. SPIE},
  volume    = {11324},
  publisher = {SPIE},
  year      = {2020},
  month     = mar,
  doi       = {10.1117/12.2551853}
}
```

The fact sheet spells the thirteenth author "K. Maturov\'a"; the DOI record has
"Maturova". The fact sheet is identified by sha256
`aeaa1513ecebc7d8918066d11915fd74f13fd77362268b58c5c5e006f1811594` in
[site/MANIFEST.json](site/MANIFEST.json) (`hosted_documents`); live:
https://www.datocms-assets.com/119587/1738752183-4-technical-fact-sheet-quantum-inspire-spin-2-plus.pdf.

## Backends

### Tuna-5

The transmons page links the Tuna-5 publication as "Physical Review Letters
(in press)" with its arXiv preprint
([site/backends_transmons.md](site/backends_transmons.md),
[live](https://www.quantum-inspire.com/backends/transmons/)). It appeared as
Phys. Rev. Lett. 136, 200801 on 18 May 2026, so "in press" is stale. The
journal author order swaps Stavenga and Brulleman relative to the arXiv
DataCite record; the entry follows the journal.

```bibtex
% doi.org; article number 200801 from Crossref (article-number).
@article{VallesSanclemente2026TunableCouplers,
  author  = {Vall{\'e}s-Sanclemente, S. and Vroomans, T. H. F. and van Abswoude, T. R. and Stavenga, T. and Brulleman, F. and van der Meer, S. L. M. and Xin, Y. and Lawrence, A. and Singh, V. and Rol, M. A. and DiCarlo, L.},
  title   = {Optimizing the Frequency Positioning of Tunable Couplers in a Circuit {QED} Processor to Mitigate Spectator Effects on Quantum Operations},
  journal = {Physical Review Letters},
  volume  = {136},
  number  = {20},
  pages   = {200801},
  year    = {2026},
  month   = may,
  doi     = {10.1103/wdfj-4nbt},
  eprint  = {2503.13225},
  archivePrefix = {arXiv}
}
```

The page says "The very Tuna-5 QPU available here was previously used in the
experiment below", so the paper characterizes the device itself.

### Starmon-5 and Starmon-7

Both discontinued backends link arXiv:2602.18388. It studies qubit error
bursts in QI's superconducting processors, not the device design, so it
supports claims about Starmon error statistics.

```bibtex
% DataCite record for arXiv:2602.18388 (no journal version found).
@misc{DiCarlo2026ErrorBursts,
  author        = {Di Carlo, G. R. and Samiotis, M. and Kamlapure, A. and Finkel, M. and Muthusubramanian, N. and Beekman, M. W. and Haider, N. and Moreira, M. S. and Marques, J. F. and Segers, B. and Vall{\'e}s-Sanclemente, S. and DiCarlo, L.},
  title         = {Qubit error bursts in superconducting quantum processors of Quantum Inspire: quasiparticle pumping and anomalous time dependence},
  year          = {2026},
  eprint        = {2602.18388},
  archivePrefix = {arXiv},
  doi           = {10.48550/arXiv.2602.18388}
}
```

### Tuna-9 and Tuna-17

No page links a publication for these devices (retrieved 2026-10-16).

### Spin-2 and Spin-2+

The Spin-2+ landing page links no paper; its fact sheet (identified above)
cites the device and control lineage. The verified entries:

```bibtex
% doi.org. Fact sheet reference [4]: the six-qubit device Spin-2+ uses three dots of.
@article{Philips2022SixQubit,
  author  = {Philips, Stephan G. J. and M{\k{a}}dzik, Mateusz T. and Amitonov, Sergey V. and de Snoo, Sander L. and Russ, Maximilian and Kalhor, Nima and Volk, Christian and Lawrie, William I. L. and Brousse, Delphine and Tryputen, Larysa and Wuetz, Brian Paquelet and Sammak, Amir and Veldhorst, Menno and Scappucci, Giordano and Vandersypen, Lieven M. K.},
  title   = {Universal control of a six-qubit quantum processor in silicon},
  journal = {Nature},
  volume  = {609},
  number  = {7929},
  pages   = {919--924},
  year    = {2022},
  month   = sep,
  doi     = {10.1038/s41586-022-05117-x}
}

% DataCite record for arXiv:2406.07267. Fact sheet reference [5].
@misc{DeSmet2024Shuttling,
  author        = {De Smet, Maxim and Matsumoto, Yuta and Zwerver, Anne-Marije J. and Tryputen, Larysa and de Snoo, Sander L. and Amitonov, Sergey V. and Katiraee-Far, S. R. and Sammak, Amir and Samkharadze, Nodar and G{\"u}l, {\"O}nder and Wasserman, Rick N. M. and Greplov{\'a}, E. and Rimbach-Russ, Maximilian and Scappucci, Giordano and Vandersypen, Lieven M. K.},
  title         = {High-fidelity single-spin shuttling in silicon},
  year          = {2024},
  eprint        = {2406.07267},
  archivePrefix = {arXiv},
  doi           = {10.48550/arXiv.2406.07267}
}

% doi.org. Fact sheet reference [3] and a QI background paper.
@article{Watson2018TwoQubitSilicon,
  author  = {Watson, T. F. and Philips, S. G. J. and Kawakami, E. and Ward, D. R. and Scarlino, P. and Veldhorst, M. and Savage, D. E. and Lagally, M. G. and Friesen, Mark and Coppersmith, S. N. and Eriksson, M. A. and Vandersypen, L. M. K.},
  title   = {A programmable two-qubit quantum processor in silicon},
  journal = {Nature},
  volume  = {555},
  number  = {7698},
  pages   = {633--637},
  year    = {2018},
  month   = feb,
  doi     = {10.1038/nature25766}
}

% doi.org; article number 34 from Crossref. Fact sheet reference [2] and a QI background paper.
@article{Vandersypen2017Interfacing,
  author  = {Vandersypen, L. M. K. and Bluhm, H. and Clarke, J. S. and Dzurak, A. S. and Ishihara, R. and Morello, A. and Reilly, D. J. and Schreiber, L. R. and Veldhorst, M.},
  title   = {Interfacing spin qubits in quantum dots and donors--hot, dense, and coherent},
  journal = {npj Quantum Information},
  volume  = {3},
  number  = {1},
  pages   = {34},
  year    = {2017},
  month   = sep,
  doi     = {10.1038/s41534-017-0038-y}
}
```

Fact sheet references [6] and [7] (Esposti et al., Appl. Phys. Lett. 120,
184003 (2022) and npj Quantum Inf. 10, 32 (2024)) and the software reference
[8] were not checked against a registration record and carry no entry here.

Two 2026 QuTech-affiliated spin-qubit papers are retained with notes on the
platform documentation branch, `docs/notes/s41586-026-10423-9.md` and
`docs/notes/s41567-026-03466-2.md` (they join this tree when that branch
merges). No Quantum Inspire page cites them and neither describes a QI
backend; the checkable relation is authorship: Matsumoto and De Smet, the
first two authors of the Nature paper, are the first two authors of
fact-sheet reference [5] in reverse order.

```bibtex
% doi.org: Nature 653(8114), 391-397; published online 6 May 2026, issue 14 May 2026.
@article{Matsumoto2026MobileSpin,
  author  = {Matsumoto, Y. and De Smet, M. and Tryputen, L. and de Snoo, S. L. and Amitonov, S. V. and Sammak, A. and Rimbach-Russ, M. and Scappucci, G. and Vandersypen, L. M. K.},
  title   = {Two-qubit logic and teleportation with mobile spin qubits in silicon},
  journal = {Nature},
  volume  = {653},
  number  = {8114},
  pages   = {391--397},
  year    = {2026},
  month   = may,
  doi     = {10.1038/s41586-026-10423-9}
}

% doi.org and Crossref: published online 15 October 2026; volume and pages unassigned.
@article{Wu2026SimultaneousGates,
  author  = {Wu, Yi-Hsien and Camenzind, Leon C. and B{\"u}tler, Patrick and Jin, Ik Kyeong and Noiri, Akito and Takeda, Kenta and Nakajima, Takashi and Kobayashi, Takashi and Scappucci, Giordano and Goan, Hsi-Sheng and Tarucha, Seigo},
  title   = {Simultaneous high-fidelity single-qubit gates in a spin qubit array},
  journal = {Nature Physics},
  year    = {2026},
  month   = oct,
  doi     = {10.1038/s41567-026-03466-2}
}
```

The quantum-classification page and the reference page also cite Spin-2
results through N. M. P. Neumann, "Classification using a two-qubit quantum
chip", arXiv:2004.10426 (2020).

## Language, compiler and simulator

```bibtex
% DataCite record for arXiv:1805.09607. cQASM v1.0, the language QI 1.0 ran.
@misc{Khammassi2018cQASM,
  author        = {Khammassi, N. and Guerreschi, G. G. and Ashraf, I. and Hogaboam, J. W. and Almudever, C. G. and Bertels, K.},
  title         = {{cQASM} v1.0: Towards a Common Quantum Assembly Language},
  year          = {2018},
  eprint        = {1805.09607},
  archivePrefix = {arXiv},
  doi           = {10.48550/arXiv.1805.09607}
}

% doi.org. The QX simulator paper.
@inproceedings{Khammassi2017QX,
  author    = {Khammassi, N. and Ashraf, I. and Fu, X. and Almudever, C. G. and Bertels, K.},
  title     = {{QX}: A high-performance quantum computer simulation platform},
  booktitle = {Design, Automation \& Test in Europe Conference \& Exhibition (DATE), 2017},
  publisher = {IEEE},
  pages     = {464--469},
  year      = {2017},
  month     = mar,
  doi       = {10.23919/DATE.2017.7927034}
}

% doi.org; Crossref lists online 20 Dec 2021, print 31 Jan 2022. Starmon-7 compiler.
@article{Khammassi2021OpenQL,
  author  = {Khammassi, N. and Ashraf, I. and Someren, J. V. and Nane, R. and Krol, A. M. and Rol, M. A. and Lao, L. and Bertels, K. and Almudever, C. G.},
  title   = {{OpenQL}: A Portable Quantum Programming Framework for Quantum Accelerators},
  journal = {ACM Journal on Emerging Technologies in Computing Systems},
  volume  = {18},
  number  = {1},
  pages   = {1--24},
  year    = {2021},
  month   = dec,
  doi     = {10.1145/3474222}
}
```

cQASM 3.0, libqasm, OpenSquirrel, the SDK and the two plugins have no paper
and no `CITATION.cff` in their repositories (GitHub contents API,
2026-10-16). Cite them as software at the release used; the version and date
come from the retained release histories ([releases/](releases/MANIFEST.json))
and the license from the GitHub repository metadata. `@software` is a
biblatex entry type; classic BibTeX styles treat it as unknown.

```bibtex
@software{cQASMspec3beta2,
  author  = {{QuTech-Delft}},
  title   = {{cQASM} language specification},
  version = {3.0-beta2},
  date    = {2025-02-18},
  url     = {https://github.com/QuTech-Delft/cQASM-spec},
  license = {Apache-2.0}
}

@software{libqasm160,
  author  = {{QuTech-Delft}},
  title   = {{libQASM}: Library to parse {cQASM} files},
  version = {1.6.0},
  date    = {2026-10-14},
  url     = {https://github.com/QuTech-Delft/libqasm}
}

@software{OpenSquirrel091,
  author  = {{QuTech-Delft}},
  title   = {{OpenSquirrel}: A flexible (Python-based) quantum program compiler},
  version = {0.9.1},
  date    = {2026-07-30},
  url     = {https://github.com/QuTech-Delft/OpenSquirrel},
  license = {Apache-2.0}
}

@software{QXsimulator0100,
  author  = {{QuTech-Delft}},
  title   = {{QX} Simulator},
  version = {0.10.0},
  date    = {2025-08-28},
  url     = {https://github.com/QuTech-Delft/qx-simulator}
}

@software{QuantumInspireSDK410,
  author  = {{QuTech-Delft}},
  title   = {Quantum Inspire {SDK}},
  version = {4.1.0},
  date    = {2026-09-25},
  url     = {https://github.com/QuTech-Delft/quantuminspire},
  license = {Apache-2.0}
}

@software{QiskitQuantumInspire0185,
  author  = {{QuTech-Delft}},
  title   = {Qiskit provider for Quantum Inspire backends},
  version = {0.18.5},
  date    = {2026-10-05},
  url     = {https://github.com/QuTech-Delft/qiskit-quantuminspire},
  license = {Apache-2.0}
}

@software{PennyLaneQuantumInspire0155,
  author  = {{QuTech-Delft}},
  title   = {{PennyLane-QuantumInspire} plugin},
  version = {0.15.5},
  date    = {2026-10-05},
  url     = {https://github.com/QuTech-Delft/pennylane-quantuminspire},
  license = {Apache-2.0}
}
```

`author` names the GitHub organization that publishes each repository; the
repositories name no individual authors. GitHub reports no SPDX license
for libqasm and qx-simulator (`NOASSERTION`), so those entries carry none.

## References the knowledge base cites

| Page | Reference | Verified record |
|---|---|---|
| spin-2-plus-operational-specifics, opensquirrel | D. C. McKay et al., "Efficient Z-Gates for Quantum Computing", arXiv:1612.00858 | DataCite doi:10.48550/arXiv.1612.00858 |
| neutral-atom example | M. Saffman, J. Phys. B 49, 202001 (2016) | doi:10.1088/0953-4075/49/20/202001 |
| grover-algorithm | L. K. Grover, Phys. Rev. Lett. 79, 325-328 (1997) | doi:10.1103/PhysRevLett.79.325 |
| quantum-classification, reference | N. M. P. Neumann, arXiv:2004.10426 | DataCite doi:10.48550/arXiv.2004.10426 |
| reference | T. F. Watson et al., Nature 555, 633-637 (2018); L. M. K. Vandersypen et al., npj Quantum Inf. 3, 34 (2017) | entries above |
