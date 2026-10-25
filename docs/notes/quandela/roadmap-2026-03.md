# Quandela roadmap 2026-2033 and the Quandela-Welinq interconnect announcement

[P] identifies a statement in a source. [I] identifies a repository
inference. Both sources are vendor documents: the roadmap states targets and
the announcement states intent. Neither is a measurement, and neither names an
interconnect that a cloud user of the Ascella or Belenos processors can
reach.

## Source 1: Quandela roadmap PDF

- Title page: "ROADMAP 2026-2033", Quandela. The note calls it the 2026
  roadmap; the file name ends in `190326`, and the PDF metadata gives a
  creation date of 19 March 2026 (PDT, Adobe InDesign 21.2) [I: the file
  name and metadata agree on 19 March 2026; the PDF prints no publication
  date].
- Direct URL: https://www.quandela.com/wp-content/uploads/2026/03/Quandela-Roadmap-190326-web.pdf
- Retrieved 25 October 2026 (09:04 UTC); 9 PDF pages (square pages of
  595.276 x 595.276 pt); 1,855,118 bytes.
- PDF SHA-256: `692bfcd42d3fa83e95d00cbee831040e5879eb45eb89210df3fdb0f2aadfb3d3`.
- Rights: a text search of the extracted PDF for "copyright", "licen" and
  the copyright sign finds no match, so the PDF prints no license and no
  copyright line in its text layer. The English terms
  of the site that serves it (section 7, Intellectual Property, captured in
  [legal/www_legal-terms.md](legal/www_legal-terms.md)) prohibit reproduction,
  extraction or reuse of the site's contents without prior written
  authorization from Quandela. Retain the source as external-only with its
  audited URL and hash; the inspected PDF remains in the ignored local cache.
  The registry record in [SOURCES.json](../../SOURCES.json) uses
  `NOASSERTION` for the license.
- Local reading transcription: `docs/local_source_cache/quandela-roadmap-2026-03.md`
  (ignored, never committed; restore the PDF with
  `scripts/fetch_source_cache.py`). It carries every page, the three timeline
  grids cell by cell with row and column labels, and the publication list.
- Reading scope: all 9 pages, read as page images and compared with the
  `pdftotext -layout` text. The three grids (pages 4, 5 and 6) were read cell
  by cell against the image to attribute each cell, band label and rule to
  its year column. Page 7 (publication list) and page 9 (back cover) carry no
  networking statement beyond the citations listed below. The closing
  statement quoted below sits on page 8 together with the contact blocks, whose
  names, e-mail addresses and telephone number are not recorded. The
  brochure's own figures were not measured; no value was read from a graphic
  that the text layer does not also state.

### Statements on networking, interconnects and modular systems

Every quotation below is verbatim. The year column of a table cell is the
column header above its text in the rendered page.

Page 2, "Introduction from Shane Mansfield, Chief Research Officer":

- "Our hardware engineering program leverages photonic integrated circuits
  fabricated with partner foundries, enabling the development of control-chip
  modules for “repeat-until-success” gates by 2027."
- "2028–2029 will see performance metrics pushed to within error-correction
  thresholds, in particular through improvements in optical transmission
  across all modules and scaling via modular, high-speed optical
  networking. This hardware trajectory is matched by the continued evolution
  of our middleware and software stack."
- "Our hybrid spin-photon quantum computing architecture offers a natural
  path toward scalable systems with high connectivity and modular design."
- "In parallel, we are assembling the first quantum computing system
  integrating our spin-photon sources with unprecedented entanglement
  generation capabilities, enhanced by a high-speed feedforward module,
  upgraded compilation software, and new encoding strategies that push
  computing power far beyond raw qubit number metrics."

Page 3, "Quandela's roadmap":

- "Featuring a modular, scalable, upgradeable, and energy efficient
  architecture, Quandela’s mission is to deliver the first useful quantum
  computer to drive quantum transformation to industry and society."
- "Quandela’s unique technology is modular, interconnected, and compatible
  with state-of-the-art error-correcting codes."
- "We leverage spin-mediated qubit devices, a unique innovation that enables
  us to generate deterministic entanglement links between qubits as they are
  created."

Page 4, history table (all columns are past years):

- Column 2020 "Modular integration – building blocks for scalable quantum
  systems"; the delivered items are DMX-6 (an active demultiplexer for single
  photons) and a pigtailed single-photon source device.
- Column 2023 lists "Ascella QPU 6 qubits >140 QOPS".

Page 5, "Scaling to High-Value, Error-Corrected, Networked Quantum
Computing", columns 2024-25 (checked), 2026, 2027, 2028-29, 2030-31, 2032-33:

- Quantum systems, 2024-25: "Altaïr — QOPS >400, 10 physical qubits" and
  "Belenos — QOPS >550 (CNOT), 12 physical qubits"; 2026: "Canopus – QOPS
  >2000, 24 physical qubits".
- Column header 2027: "Quantum Computing Scaling via Modularity". Quantum
  systems 2027: "Deneb QOPS >5000 48 physical qubits Modular, energy-efficient
  photonic architecture".
- Column header 2028-29: "Crossing Fault-Tolerance Thresholds". Quantum
  systems 2028-29: "Diadem QOPS >9500 ~100 physical qubits Modular,
  networked photonic system".
- Error correction row 2028-29: "Andromeda prototype QOPS >10⁶ Logical
  qubits: ~50 Operation below error-correction thresholds Distributed quantum
  error correction". The band label "DISTRIBUTED ERROR CORRECTIONS" starts in
  the 2028-29 column and runs to the right edge; the label "NETWORKING"
  sits under the 2027 column as a band between the stage bands "LOGICAL
  QUBITS / CLUSTER PHOTONS" and "DISTRIBUTED ERROR CORRECTIONS".
- Software and algorithms 2028-29: "Distributed compilation and scheduling"
  and "Error- and energy-aware resource estimation"; 2030-31: "Secure
  delegated quantum computing" and "Distributed resource management".
- Applications 2032-33: "Cross-domain quantum utility Secure delegated quantum
  computing".
- Manufacturing 2028-29: "Increased integration through heterogeneous
  chips"; the band label "MULTI-SITE, LARGE-SCALE PRODUCTION" spans 2027, and
  "QUANTUM-CENTRIC DATA CENTER" starts in the 2028-29 column.

Page 6, "Scaling to High-Value, Error-Corrected, Networked Quantum
Computing", columns 2024, 2025, 2026, 2027, 2028-29, 2030-31, 2032-33:

- Column headers: 2027 "QC scaling via modularity"; 2028–29 "QC scaling via
  quantum networking"; 2030–31 "QC in the FT regime"; 2032–33 "Large Scale QC
  Advantage".
- Quantum processors: 2025 "Belenos: 12 phys. qubits. QOPS=576"; 2026
  "Canopus: 24 phys. qubits. QOPS=2328"; 2027 "Deneb: 48 phys. qubits.
  QOPS=5160 10 Logical qubits demonstrator"; 2028–29 "Diadem: 100 phys.
  qubits. QOPS=9768" and "Andromeda: 50 Logical qubits. QOPS= 10⁶".
- Hardware development: 2027 "Spin-spin entang. mediated by photons",
  "feedforward on PICs", "cryogenic packaging". 2028-29 "High fidelity
  cluster qubits fusion operations" and "Photon loss beyond threshold"; this
  cell's rule runs across the 2028-29 column and into the first part of the
  2030-31 column. A second cell, "Modular scaling via interconnected
  cabinets", begins inside the 2030-31 column and runs to the end of the
  2032-33 column, so its first text is not in the 2028-29 column.

Page 8, closing page:

- "Our modular and interconnected approach enables a reliable, scalable
  platform for quantum computing systems with real-world impact."
- "Quandela’s technical roadmap focuses on delivering useful near-term
  products while laying the foundations for large-scale, fault-tolerant
  quantum computing through a patented modular architecture and
  industrial-scale manufacturing processes."

Page 7 (relevant scientific publications) cites, among others, reference 13,
de Gliniasty et al., "A spin-optical quantum computing architecture,"
Quantum 8, 1423 (2024), and reference 12, Pont et al., "Indistinguishability
of remote quantum dot-cavity single-photon sources" (arXiv:2412.15762). The
roadmap prints these as a list and carries no statement about their results.

### Page-by-page reading of the roadmap PDF

| Page | Content | Repository relevance |
| --- | --- | --- |
| 1 | Cover, "ROADMAP 2026-2033". | None. |
| 2 | Introduction by the Chief Research Officer: three phases (Utility, Quantum Advantage, Large-Scale Fault-Tolerant Architecture), the 2027 and 2028-2029 statements quoted above, an energy-use estimate. | [I] The only prose that dates networking (2028-2029). |
| 3 | "Leading the way towards the fault tolerant era": a 2016 / 2023 / 2030 arrow and three themes of the strategy, with "modular, interconnected" and "deterministic entanglement links between qubits as they are created" as statements about spin-mediated devices. | [I] Describes the product architecture; no cloud interconnect. |
| 4 | History grid, columns 2017-2018 to 2023, six rows (quantum systems, applications and use cases, error correction and logical qubits, developer platform, software and algorithms, manufacturing and industrialization). Ascella appears in the 2023 quantum-systems cell. | [I] Dates Ascella. |
| 5 | Forward grid, columns 2024-25 to 2032-33, with stage bands. | [I] Dates Belenos, Diadem and the NETWORKING band. |
| 6 | Second forward grid with columns 2024, 2025, 2026, 2027, 2028-29, 2030-31 and 2032-33, a hardware-development row and a performance-threshold arrow (photon loss, distinguishability, spin coherence). | [I] Carries the "quantum networking" column header and the cabinet-interconnect cell. |
| 7 | Twenty-six references, including remote-source indistinguishability (reference 12) and the spin-optical architecture (reference 13). | [I] Citations only. |
| 8 | Contact blocks (not recorded) and the closing statement quoted above. | [I] Marketing statement. |
| 9 | Back cover. | None. |

### Does the PDF support "modular optical networking development in 2028-2029"?

[I] Verdict: partly, with a year conflict inside the PDF. Pages 2 and 6 target
2028-2029 for networking; page 5 opens a NETWORKING band in the 2027 column.
The PDF supports a 2028-2029 target for scaling through "modular,
high-speed optical networking" and for a "Modular, networked photonic
system" product (Diadem). It does not describe networking development in that
period, and it names no networking hardware step in the 2028-29
hardware-development cell.

Each timeline claim, with its page, row label, column header and cell text
(the grids' own words):

| Claim | Page | Row label | Column header | Cell text |
| --- | --- | --- | --- | --- |
| Scaling via modular, high-speed optical networking in 2028-2029 | 2 | introduction prose, paragraph "2028-2029 will see performance metrics..." | not a grid | "scaling via modular, high-speed optical networking" |
| Networking is the 2028-29 theme | 6 | column headers | "2028-29" | "QC scaling via quantum networking" |
| Modularity is the 2027 theme | 6 | column headers | "2027" | "QC scaling via modularity" |
| Modularity is the 2027 theme | 5 | column headers | "2027" | "Quantum Computing Scaling via Modularity" |
| The 2028-29 column theme on page 5 is fault tolerance, not networking | 5 | column headers | "2028-29" | "Crossing Fault-Tolerance Thresholds" |
| NETWORKING stage band starts in 2027 (conflicts with pages 2 and 6) | 5 | band beneath ERROR CORRECTION & LOGICAL QUBITS | text starts in the "2027" column | "NETWORKING" |
| Networked product | 5 | QUANTUM SYSTEMS | "2028-29" | "Diadem QOPS >9500 ~100 physical qubits Modular, networked photonic system" |
| Same system, page 6 | 6 | QUANTUM PROCESSORS | "2028-29" | "Diadem: 100 phys. qubits. QOPS=9768" and "Andromeda: 50 Logical qubits. QOPS= 10^6" |
| Modular architecture at 2027 | 5 | QUANTUM SYSTEMS | "2027" | "Deneb QOPS >5000 48 physical qubits Modular, energy-efficient photonic architecture" |
| Distributed error correction | 5 | ERROR CORRECTION & LOGICAL QUBITS | "2028-29" | "Andromeda prototype QOPS >10^6 Logical qubits: ~50 Operation below error-correction thresholds Distributed quantum error correction" |
| Distributed error correction band | 5 and 6 | band beneath ERROR CORRECTION (page 5) and beneath QUANTUM PROCESSORS (page 6) | text starts in "2028-29" | "DISTRIBUTED ERROR CORRECTIONS" |
| Distributed software | 5 | SOFTWARE & ALGORITHMS | "2028-29"; "2030-31" | "Distributed compilation and scheduling"; "Distributed resource management" |
| Quantum-centric data center | 5 | band beneath MANUFACTURING & INDUSTRIALIZATION | text starts in "2028-29" | "QUANTUM-CENTRIC DATA CENTER" |
| Hardware step before networking | 6 | HARDWARE DEVELOPMENT | "2027" | "Spin-spin entang. mediated by photons"; "feedforward on PICs"; "cryogenic packaging" |
| No networking hardware item in 2028-29 | 6 | HARDWARE DEVELOPMENT | "2028-29" | "High fidelity cluster qubits fusion operations"; "Photon loss beyond threshold" |
| Only interconnect hardware item | 6 | HARDWARE DEVELOPMENT | text starts in "2030-31", rule runs to the end of "2032-33" | "Modular scaling via interconnected cabinets" |

- The design's wording "targets scaling through modular, high-speed optical
  networking in 2028-2029" is supported by page 2 and by the page-6 column
  header; the page-5 NETWORKING band starts one column earlier, in 2027, and
  the page-5 header of 2028-29 names fault tolerance. State the 2028-2029
  target with its two supporting pages and keep the page-5 band as a
  year conflict.
- Not supported as "development": the hardware row names no networking step
  in 2028-29, and its only interconnection item starts in the 2030-31
  column.
- Stage of work: the roadmap states a target year for a capability. It does
  not say whether 2028-29 means laboratory demonstration, first system
  delivery, or availability to cloud users.
- Wording to use in the design: "the March 2026 Quandela roadmap targets
  scaling through modular, high-speed optical networking in 2028-2029
  (pages 2 and 6), with the Diadem system (about 100 physical qubits) as the
  networked product and a NETWORKING stage band that begins in the 2027
  column (page 5)"; avoid "development", and avoid a delivery date for cloud
  users.

[I] Ascella and Belenos in the grids. Ascella appears once, on page 4, in the
2023 quantum-systems cell ("Ascella QPU 6 qubits >140 QOPS"), under the
"SINGLE PHOTONS" band that starts in the 2023 column. Belenos appears on page
5 in the 2024-25 quantum-systems cell ("Belenos -- QOPS >550 (CNOT), 12
physical qubits", with "Fidelity gains via error mitigation") under the
"SINGLE PHOTONS" band, and on page 6 in the 2025 quantum-processors cell
("Belenos: 12 phys. qubits. QOPS=576", "Logical qubits at fidelity threshold")
under the "CLUSTER PHOTONS" band that starts in the 2025 column. The two pages
therefore place Belenos in different photon phases; the earlier statement that
the roadmap places Belenos in the single-photon phase held for page 5 only.
Neither processor appears in any cell, header, band or prose passage that
contains "networking", "modular", "interconnected" or "distributed": those
words occur on pages 2 to 6 and 8 in the cells (page 4 only as the 2020 "Modular integration" column and its "MODULE INTEGRATION" band) and passages listed above,
none of which names Ascella or Belenos. The roadmap names no mechanism that
would link a cloud-accessible Ascella or Belenos to another processor.

### Corrections to the earlier reading

Two statements changed. The earlier text placed Belenos in the single-photon
phase on the strength of page 5; page 6 puts the 2025 Belenos cell under
"CLUSTER PHOTONS". The earlier reading scope called page 9 "the closing
slogan"; the slogan "Our modular and interconnected approach ..." is on page
8, and page 9 is a back cover. No quoted statement of the earlier note differs
from the PDF.

### Repository use

The repository uses this source in
[the Ascella-Belenos design](../../design/ascella-belenos-entanglement-teleportation.md)
(sections "The partition constraint", "Gates" row G2 and "Provider request"),
which reads the roadmap as development context.

[I] The roadmap supplies no access route, port map or interconnect for the
installations behind `qpu:ascella` and `qpu:belenos`, so it does not
satisfy gate G2 (physical access) and supports none of the claim levels C2 to
C6, which each need a shared entangled resource across the Ascella|Belenos
cut. It states targets, not measurements; the Hoeffding radius, the separable
witness bound and the `2/3` benchmark of the design's decision statistics have
no content on these pages. A provider answer that names an accessible
apparatus, route and data contract would enter G2; a roadmap row does not.

## Source 2: Quandela and Welinq announcement

- Title: "Quandela and Welinq Join Forces to Create Custom Quantum
  Interconnects for Photonic Quantum Computing" (Quandela newsroom, press
  release).
- URL read: https://www.quandela.com/about-us/newsroom/quandela-and-welinq-join-forces-to-create-custom-quantum-interconnects-for-photonic-quantum-computing/
  The `/fr/` form of the address, https://www.quandela.com/fr/about-us/newsroom/quandela-and-welinq-join-forces-to-create-custom-quantum-interconnects-for-photonic-quantum-computing/,
  serves a French-language shell (`lang="fr-FR"`, 193,133 bytes, SHA-256
  `1f5a4511b9e711236fff736e5170dc4f8d9b6789b7dce5886f26071b841fdedb`) with
  the same English article text and the same canonical link; the registry
  records the English address.
- Date: the visible text carries no date. The page's structured data gives
  `datePublished` 2024-07-18T09:57:24+00:00 and `dateModified`
  2024-10-16T16:38:51+00:00. The announcement therefore dates from July 2024
  [I: the structured-data date is page metadata, not text of the release].
  The release states that the AQADOC project was announced "a few weeks ago".
- Retrieved 25 October 2026 (09:04 UTC); 194,407 bytes; SHA-256
  `ef20c92a9645fcf02b1d3a4b4b0e31ef4ed51c41e7118551f7432e124fe1c378`. The
  served page also embeds unrelated newsroom items dated October 2026, so
  the response hash identifies the inspected bytes and changes whenever the
  site updates.
- Reading scope: the full article body (headline, introduction, "Advancing
  QPU scaling", "Importance of Photonic QPUs and Quantum Interconnects",
  "Implementing a multi-pronged approach", and the two company boilerplates).
  The page's site navigation, which lists the products Ascella, Belenos,
  Canopus and Mosaiq, is not part of the article; media-contact details are
  not recorded.

Decisive statements, verbatim:

- "This collaboration combines Quandela’s expertise in photonic quantum
  computing with Welinq’s pioneering full-stack quantum interconnects
  technology, to provide custom quantum links for photonic quantum computers,
  setting new industry standards and paving the way for clusters of
  interconnected and error-corrected photonic quantum computers."
- "In joining forces, Welinq’s state-of-the-art quantum interconnects combined
  with Quandela’s quantum processors, will support fault-tolerant computing
  and the expansion of comprehensive quantum networks, beyond the
  capabilities of a single chip."
- "Scaling to a large number of qubits will involve the interconnection of
  multiple independent photonic QPUs, a process that demands additional
  technological advancements and represents a huge technological challenge in
  itself."
- "Full-stack quantum interconnects based on efficient quantum memories are
  crucial for linking multiple QPUs regardless of the qubit modality."
- "This partnership is in line with Quandela and Welinq’s desire to work
  together to develop fully-fledged clusters of photonic quantum computers,
  which would have both hardware and algorithmic advantages over alternative
  approaches."
- "The aim of this project [AQADOC, led by Welinq, with Quandela as a key
  member] is to explore energy-related use-cases and to develop the next
  generation of distributed software capabilities, capable of running on
  several QPUs interconnected by the hardware work to be carried out as part
  of this strategic partnership."
- Welinq's boilerplate describes quantum links "based on laser-cooled neutral
  atom quantum memories" that interconnect quantum computers.

[I] The release is a statement of intent in the future and conditional tense
("will support", "would have", "work to be carried out"). It names no
delivery date, no interface specification, no performance figure and no
processor. Neither "Ascella" nor "Belenos" appears in the article body, and
the article offers no access route for cloud users to any interconnected
system. The expected finding holds: the announcement names no accessible
Ascella or Belenos link.
