> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/keywords.html](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/keywords.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 ad9f969ff62f4ec4de33cd0431cfde0d22baef035943023c3bf1d0e576e0e692;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# Keywords

Keywords constitute identifiers reserved by the language parser. As such, they have a specific predefined meaning and cannot be overwritten or used as a general identifier, *e.g.*, as the name of the (qu)bit register.

The table below lists the reserved keywords in cQASM:

| Keyword       | Use                         |
|:--------------|:----------------------------|
| **`asm`**     | Assembly declaration        |
| **`barrier`** | Barrier control instruction |
| **`bit`**     | Bit type                    |
| **`ctrl`**    | Control gate modifier       |
| **`init`**    | Init instruction            |
| **`inv`**     | Inverse gate modifier       |
| **`measure`** | Measure instruction         |
| **`pow`**     | Power gate modifier         |
| **`qubit`**   | Qubit type                  |
| **`reset`**   | Reset instruction           |
| **`version`** | Version statement           |
| **`wait`**    | Wait control instruction    |
