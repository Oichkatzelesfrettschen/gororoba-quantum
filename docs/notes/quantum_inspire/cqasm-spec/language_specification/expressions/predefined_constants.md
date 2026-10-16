> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/language_specification/expressions/predefined_constants.html](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/expressions/predefined_constants.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 177250417af7f78e42bd80196d4de7a7187d8006eb3af24b7f10fa7082039c55;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# Predefined constants

The following mathematical constants are recognized: **`pi`**, **`tau`**, and **`eu`**, where **`tau`** is $`2\pi`$ and **`eu`** represents Euler's constant $`e`$. They are stored as floating-point [number literals](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/literals.html) and can be used in arithmetic expressions with [operators](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/operators_and_punctuators.html), *e.g.*, **`pi/2`** equals $`\tfrac{\pi}{2}`$.

The latter can be used, for example, as an argument for a [parameterized named gate](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/unitary_instructions.html#named-gates), *i.e.*,  **`Rx(pi/2) q[0]`**.
