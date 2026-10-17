> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/literals.html](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/literals.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 fd2943173ba3d5561fbbfdc64a21944ed3acde2c93a8da4127d4c7fb94c7cfe0;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# Literals

The only literals accepted as tokens are integer and float numbers.

| Literal | Size / precision          |
|:--------|:--------------------------|
| Integer | 64-bit signed             |
| Float   | IEEE 754 double precision |

Grammar of number literals

*integer-literal*:\
  *digit-sequence*

*floating-literal*:\
  *digit-sequence* **`.`** *digit-sequence exponent*_(opt)\
  *digit-sequence* **`.`** *exponent*_(opt)\
  **`.`** *digit-sequence* *exponent*_(opt)

*exponent*:\
  **`e`** *sign*_(opt) *digit-sequence*\
  **`E`** *sign*_(opt) *digit-sequence*

*sign*: one of\
  **`+`** **`-`**

*digit-sequence*:\
  *digit*\
  *digit-sequence* *digit*

*digit*: one of\
  **`0`** through **`9`**
