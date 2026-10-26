# Pais "Superforce" papers and the sources they lean on -- bibliographic record

This note lists the sources of the Planck-force ("Superforce", `c^4/G`) argument of Pais and the references the
repository needs to check it. It records identities, licenses and retention; the mathematical decomposition lives
in [pais-claims-falsification.md](../topics/pais-claims-falsification.md) and the patents in
[pais-patent-web-sources.md](pais-patent-web-sources.md). Tag convention: [P] marks a statement of the source's own
record; [I] marks repository interpretation.

## Retained PDFs (docs/pdf)

| Source | Retained file | SHA-256 | Pages | Bytes | License evidence |
|---|---|---|---|---|---|
| Pais, "SUPERFORCE -- the Fundamental Force of Unification", OSF preprint 9kebt_v1, published 2023-07-24, DOI 10.31219/osf.io/9kebt | `docs/pdf/pais-2023-superforce.pdf` | `8ea4fecbd504b2dfa73941f856befe5bee23b1ebffa8a6a8bbd19e185a675176` | 3 | 238900 | `https://api.osf.io/v2/preprints/9kebt_v1/` (capture `docs/evidence/source_rights/osf-9kebt_v1.json`): license id `563c1cf88c5e4a3877f9e96c`, which `https://api.osf.io/v2/licenses/563c1cf88c5e4a3877f9e96c/` names "CC0 1.0 Universal" |
| Particle Data Group, Review of Particle Physics 2024, Phys. Rev. D 110, 030001, chapter 9 "Quantum Chromodynamics" (Huston, Rabbertz, Zanderighi) | `docs/pdf/rpp2024-rev-qcd.pdf` | `d06948c331663c2341c3f922e48cd29b4aac83f3bbff71fe3ac8d70cb4f40c51` | 64 | 1569596 | INSPIRE-HEP record 2817040, `https://inspirehep.net/api/literature?q=recid%3A2817040&fields=control_number,dois,titles,license` (capture `docs/evidence/source_rights/inspire-2817040.json`): the review's publication license entry reads "CC BY 4.0"; Crossref lists CC BY 4.0 (`vor`) for the DOI |
| Fragkos and Pikovski, "Probing classical and quantum violations of the equivalence of active and passive gravitational mass", arXiv:2503.16198v1 | `docs/pdf/2503.16198v1.pdf` | `8b265152ee659c36933ed39d265784e2cc2ab12131732b654508f38d57539193` | 13 | 3350972 | exact-version arXiv abstract page `https://arxiv.org/abs/2503.16198v1` (capture `docs/evidence/source_rights/arxiv-2503.16198v1.html`): license link `http://creativecommons.org/licenses/by/4.0/` |

Source URLs: the OSF file `https://osf.io/download/64be6e13903ac107b0dcc5e3/` (retrieved 2026-10-26T01:56:49Z; the PDF
text states no license, so the OSF record carries the grant), `https://pdg.lbl.gov/2024/reviews/rpp2024-rev-qcd.pdf`
(2026-10-26T01:56:58Z) and `https://arxiv.org/pdf/2503.16198v1` (2026-10-26T01:56:59Z). The PDG file is one chapter of
the licensed review; the record binds the license by the review's DOI `10.1103/PhysRevD.110.030001` and the chapter
route, and the 64-page file prints no license of its own. The CC BY 4.0 and CC0 terms are at
`https://creativecommons.org/licenses/by/4.0/` and `https://creativecommons.org/publicdomain/zero/1.0/`; retain
attribution, notices and links, and mark changes. [SOURCES.json](../../SOURCES.json) binds each hash and capture.

[P] The Superforce paper's abstract states that "it is the Planck Force (c4/G) that is the ruling force of
unification, named the Superforce", that the same factor appears as the inverse of the coupling of the stress-energy
tensor in Einstein's field equations, and that the Superforce "accounts for a feasible theory of Quantum Gravity".

## External-only reading copies (docs/local_source_cache)

| Source | Reading copy | SHA-256 | Pages | Bytes | Rights decision |
|---|---|---|---|---|---|
| Pais, "On the Existence of the Superforce -- the possible fundamental Force of Unification", OSF preprint yh84c_v1, 2023-04-11, DOI 10.31219/osf.io/yh84c; `https://osf.io/download/64355871d62be735870005c6/` | `docs/local_source_cache/pais-2023-existence-of-the-superforce.pdf` | `920d2625e0c940b47c9701dfd020efdeaabfb649e0d2cfdf9922f5d738efa3eb` | 4 | 323390 | The OSF record carries license id `563c1cf88c5e4a3877f9e965` ("No license") and copyright holder Salvatore Cezar Pais (2023): all rights reserved, so the PDF stays out of the published library |
| Will, "The Confrontation between General Relativity and Experiment", Living Rev. Relativity 17, 4 (2014), DOI 10.12942/lrr-2014-4; publisher full text served by INSPIRE-HEP at `https://inspirehep.net/files/5b30018625fd0245ba3ae64f462b86f8` | `docs/local_source_cache/will-2014-confrontation-gr-experiment.pdf` | `9b59dbea38f7f8d5cb1846b1ca7a8484a9de4c35d0bbc1a39022eaf21dc45456` | 117 | 1907210 | The file states "licensed under a Creative Commons Attribution-Non-Commercial 3.0 Germany License" (PDF pp. 1-2) while Crossref lists CC BY 4.0 (`vor`); the Springer route answers automated requests with a client challenge, so the conflict stays open and the non-commercial statement in the retained bytes governs |
| Buttazzo, Degrassi, Giardino, Giudice, Sala, Salvio and Strumia, "Investigating the near-criticality of the Higgs boson", JHEP 12 (2013) 089, DOI 10.1007/JHEP12(2013)089; arXiv:1307.3536v4, `https://arxiv.org/pdf/1307.3536v4` | `docs/local_source_cache/1307.3536v4.pdf` | `d201cda6299774ed8704be2b7b9d272f0bd1bd984afcbff1ff7daaefff10aeb8` | 43 | 1756331 | exact-version arXiv page grants arXiv distribution only (`nonexclusive-distrib 1.0`); the Springer version of record (Crossref lists CC BY 2.0, outside the registry's CC BY 4.0 and CC0 allowlist) was unreachable, so the arXiv preprint serves as the reading copy |

## Metadata-only references (Crossref receipts in SOURCES.json)

- Kreuzer, "Experimental Measurement of the Equivalence of Active and Passive Gravitational Mass", Phys. Rev. 169,
  1007 (1968), DOI 10.1103/PhysRev.169.1007.
- Bartlett and Van Buren, "Equivalence of active and passive gravitational mass using the moon", Phys. Rev. Lett. 57,
  21 (1986), DOI 10.1103/PhysRevLett.57.21.
- Touboul et al. (MICROSCOPE), final results of the test of the equivalence principle, Phys. Rev. Lett. 129, 121102
  (2022), DOI 10.1103/PhysRevLett.129.121102.
- Burkert, Elouadrhiri and Girod, "The pressure distribution inside the proton", Nature 557, 396 (2018), DOI
  10.1038/s41586-018-0060-z.
- Shanahan and Detmold, "Pressure Distribution and Shear Forces inside the Proton", Phys. Rev. Lett. 122, 072003
  (2019), DOI 10.1103/PhysRevLett.122.072003.
- Gibbons, "The Maximum Tension Principle in General Relativity", Found. Phys. 32, 1891 (2002), DOI
  10.1023/A:1022370717626.
- Planck Collaboration, "Planck 2018 results. VI. Cosmological parameters", Astron. Astrophys. 641, A6 (2020), DOI
  10.1051/0004-6361/201833910. The publisher license is EDP copyright
  (`https://www.edpsciences.org/en/authors/copyright-and-licensing`), so no PDF is retained.
- Will 2014, Buttazzo et al. 2013 and the Review of Particle Physics also carry Crossref receipts for their
  bibliographic identity.

Each Crossref response is a mutable record; the registry's hash identifies the inspected bytes. No paywalled PDF
was downloaded.

## Open items

- [I] The Springer versions of record of Will 2014 and Buttazzo et al. 2013 need a browser session or an
  institutional route; a version of record under a CC BY 4.0 grant would replace the reading copies above and
  publish under `docs/pdf/` through the Springer or SCOAP3 route.
- [I] `docs/local_source_cache/pais-2023-existence-of-the-superforce.pdf`, the Will reading copy and the Buttazzo
  preprint are candidates for the private documents repository under its rule that a file belongs there only when
  its rights record excludes redistribution.
