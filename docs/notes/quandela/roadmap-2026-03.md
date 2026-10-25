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
- Reading scope: all 9 pages, read as extracted text (`pdftotext -layout`),
  with pages 5 and 6 (the two timeline tables) also rendered to images to
  attribute each cell to its year column. Page 7 (publication list) and page
  9 (closing slogan) carry no networking statement beyond the citations
  listed below. Page 8 contact names, e-mail addresses and a telephone number
  are not recorded.

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

### Does the PDF support "modular optical networking development in 2028-2029"?

[I] Verdict: partly. The PDF supports a 2028-2029 target for scaling through
"modular, high-speed optical networking" and for a "Modular, networked
photonic system" product (Diadem). It does not describe networking
development in that period, and it names no networking hardware step in the
2028-29 hardware-development cell.

- Supported (page 2): "2028–2029 will see ... scaling via modular,
  high-speed optical networking."
- Supported (page 6): the 2028–29 column header reads "QC scaling via quantum
  networking", and the 2027 header reads "QC scaling via modularity".
- Supported (page 5): the 2028-29 quantum system, Diadem, is "Modular,
  networked photonic system" with "~100 physical qubits".
- Not supported as "development": the 2028-29 hardware-development cell
  (page 6) lists "High fidelity cluster qubits fusion operations" and "Photon
  loss beyond threshold", and the hardware row's only interconnection item,
  "Modular scaling via interconnected cabinets", starts in the 2030-31
  column. The 2027 column lists "Spin-spin entang. mediated by photons" as
  the hardware step that precedes networking.
- Stage of work: the roadmap states a target year for a capability. It does
  not say whether 2028-29 means laboratory demonstration, first system
  delivery, or availability to cloud users.
- Wording to use in the design: "the March 2026 Quandela roadmap targets
  scaling through modular, high-speed optical networking in 2028-2029,
  with the Diadem system (about 100 physical qubits) as the networked
  product"; avoid "development", and avoid a delivery date for cloud users.

[I] The roadmap places Ascella (2023) and Belenos (2025) in the single-photon
phase. Page 5 labels their column band "SINGLE PHOTONS" for 2024-25; neither
processor appears in any networking or modular statement above. The roadmap
names no mechanism that would link a cloud-accessible Ascella or Belenos to
another processor.

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
