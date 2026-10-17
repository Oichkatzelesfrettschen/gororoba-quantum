> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/language_specification/types.html](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/types.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 c93b014fb1d0709f4783b620b30f8422ac497da0fcd53a096e97fac5755d5823;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# Types

The table below lists the available types in a cQASM program.

| Type       | Keyword     | Form                                  |
|:-----------|:------------|:--------------------------------------|
| Qubit      | **`qubit`** | **`qubit`** *identifier*              |
| QubitArray | **`qubit`** | **`qubit[`***size***`]`***identifier* |
| Bit        | **`bit`**   | **`bit`** *identifier*                |
| BitArray   | **`bit`**   | **`bit[`***size***`]`***identifier*   |

Note

Type keywords are [reserved](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/keywords.html) and, therefore, cannot be used as [identifiers](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/identifiers.html).
