# mesh-model-mapped-refits

Class: result (an output of a recorded run that no ledger row cites yet).

Question: Does mapping the null refits of `../mesh_model.py` across workers change the component-model result, and how much faster is the mapped run? `serial.json` is the output of the serial `mesh_model.py` of the working tree, `mapped.json` the output of a variant of it that maps the null refits through `parallel.ordered_map`.

Generator and command: `band-mesh.sh` (included) runs `mesh_model.py` once per variant and compares the two outputs; the variant is a temporary file that the script copies over the module, and its bytes are not retained. Hypothesis: the variant is the module of commit 200736361 (`ascella band mesh model: map the null refits`, 2026-11-09 22:49 -0800), which follows the run (files written 22:42 to 22:47) and changes the null loop to `ordered_map`.

Measured (`summary.txt`, `compare.txt`): the serial run took 160 s and the mapped run 125 s, both with exit status 0 and empty log files (the two `.log` files are empty and not retained); `serial.json` and `mapped.json` are byte-identical; against the retained `../mesh-model.json`, 108 of the 117 numeric leaves are bit-identical and the other 9 (deviance of the in-sample ceiling, train deviance and shift correlations of four hold-outs) differ by at most 8.6e-16 relative, one to a few units in the last place, so the retained result reproduces and the `serial differs from retained` line of `summary.txt` records floating-point summation order and no change of any reported figure. `compare_outputs.py` produced `compare.txt` (`python3 compare_outputs.py mapped.json ../mesh-model.json`).

Host role: the compute workstation. Dates (file modification times): 2026-11-09. Home-directory paths read `~` and the temporary directory reads `SCRATCH`; the digest of each file before that rewrite is in [SOURCE-DIGESTS.tsv](SOURCE-DIGESTS.tsv); each file is listed with its sha256 in `SHA256SUMS` (`sha256sum -c SHA256SUMS` from this directory).
