# Console logs of unretained dry runs

Each file is the console output of a submit-free `live_run.py` dry run whose
audit record (`record.json`, `isa.qpy`) no longer exists. The log is the only
surviving trace of the run: it names the record stamp on its last line, each
backend's status, pending count, calibration timestamp and median T1, T2,
readout and CZ error at the read, and every case's backend, seed, layout,
joint score, replica count, routed CZ per member and model summary. A dry run
submits nothing, so no job id, charge or raw result belongs to any of them.

| Log | Program | Source commit | Record |
|---|---|---|---|
| `2026-10-15T153810.457216Z-conditional-ramsey.log` | conditional Ramsey on ibm_kingston, layout `[105, 117]` | not recorded | lost |
| `2026-10-15T154004.769702Z-conditional-ramsey.log` | conditional Ramsey on ibm_kingston, layout `[149, 148]` | not recorded | lost |
| `2026-10-17T080522.648289Z-default-program.log` | the default seven-case program on fez, kingston and marrakesh | `8d5f038`, `sources_modified` false | lost |
| `2026-10-25T192234.800525Z-latency-recovery-w526.log` | latency-recovery exploration on ibm_kingston, W = 526 dt | `373e7dc`, `sources_modified` true | session scratch, not retained |
| `2026-10-25T192404.355979Z-latency-recovery-w2500.log` | latency-recovery exploration on ibm_kingston, W = 2500 dt | `373e7dc`, `sources_modified` true | session scratch, not retained |

The conditional Ramsey program (backlog #87) is retired with its retained
records kept; these two dry runs were never among them. The default-program
run confirmed the rebuilt python-qiskit-aer-cuda 0.17.2-2 module end to end
(`docs/notes/build_host/custatevec.md`); its Aer extension sha256
`a4e55f3de57edbe0cde3c926ef397c47358c2b84a51c1357629f35cd374c6c1a` matches the installed module and recurs in retained records
from `2026-10-17T101105.548987Z` on, so the install evidence survives in those.

A record lost this way cannot be regenerated: a dry run reads each backend's
live Target and properties at the moment it runs.

| sha256 | file |
|---|---|
| `8029aa5e87c3c8a0a09db293413fb7f856407cc92103bb59af5382c509fd0b57` | `2026-10-15T153810.457216Z-conditional-ramsey.log` |
| `8fe01125c7c3451d366f11fc4e7096fb07da0f2babbc9749ca1c06400f56d237` | `2026-10-15T154004.769702Z-conditional-ramsey.log` |
| `ed50d737fd4abd4cceab5be171c039bf3965b7be4b79f03e9b34167f1a004176` | `2026-10-17T080522.648289Z-default-program.log` |

The two latency-recovery explorations ran the family before its contracts were final, under one 60 s ceiling; their model summaries give the window costs 0.017 (W = 526 dt) and 0.081 (W = 2500 dt) that set the design's W ([heron-latency-logical-recovery.md](../../../docs/design/heron-latency-logical-recovery.md)).
