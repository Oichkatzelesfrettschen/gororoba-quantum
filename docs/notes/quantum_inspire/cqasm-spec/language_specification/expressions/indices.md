> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/language_specification/expressions/indices.html](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/expressions/indices.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 59b9a7eb8c2c0392b9275117fdd24990f8201b8dd4f47dc61ffed23be0d765f1;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# Indices

An index is a reference to one or more positions within a register. The first position of a register is 0. Positions are expressed as a list of comma-separated entries. Each entry can be a single integer or a range. A range is written as two integers separated by a colon, pointing to a first and to a last element within a register. The last position is also part of the range, *i.e.*, it does not point to the first element out of the range.

Grammar for indices

*index*:\
  *identifier* **`[`** *index-list* **`]`**

*index-list*:\
  *index-entry*\
  *index-list* **`,`** *index-entry*

*index-entry*:\
  *integer-literal*\
  *index-range*

*index-range*:\
  *index-entry* **`:`** *index-entry*

Indices, index entries, and index ranges

```
// Qubit register containing 7 qubits, numbered from 0 to 6
qubit[7] q 

// q[1, 3:5] is a qubit index with two entries: 
// the first entry points to qubit 1 in q, and the second to qubits 3, 4, and 5
H q[1, 3:5]
```
