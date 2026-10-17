> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/language_specification/expressions/builtin_functions.html](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/expressions/builtin_functions.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 ff31e3b1307a18bbad42875d4cd0ff923ab96f8194c9537ec3e0f4e929639069;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# Built-in functions

The following built-in functions can either be used individually or in more complex expressions using [arithmetic operators](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/operators_and_punctuators.html).

The value of *x*

The value *x* is either a (composite) expression, a [predefined constant](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/expressions/predefined_constants.html), or a *integer-* or *float-literal*. Note that *x* is real-valued, it cannot be a complex number.

| Function name            | Operation | Grammar                  |
|--------------------------|-----------|--------------------------|
| Square root              | $`\sqrt{x}`$  | **`sqrt(`** *x* **`)`**  |
| Natural exponential      | $`\text{e}^x`$  | **`exp(`** *x* **`)`**   |
| Natural logarithm        | $`\log(x)`$  | **`log(`** *x* **`)`**   |
| Absolute value           | $`\|x\|`$  | **`abs(`** *x* **`)`**   |
| Sine                     | $`\sin(x)`$  | **`sin(`** *x* **`)`**   |
| Cosine                   | $`\cos(x)`$  | **`cos(`** *x* **`)`**   |
| Tangent                  | $`\tan(x)`$  | **`tan(`** *x* **`)`**   |
| Arcsine                  | $`\sin^{-1}(x)`$  | **`asin(`** *x* **`)`**  |
| Arccosine                | $`\cos^{-1}(x)`$  | **`acos(`** *x* **`)`**  |
| Arctangent               | $`\tan^{-1}(x)`$  | **`atan(`** *x* **`)`**  |
| Hyperbolic of sine       | $`\sinh(x)`$ | **`sinh(`** *x* **`)`**  |
| Hyperbolic of cosine     | $`\cosh(x)`$ | **`cosh(`** *x* **`)`**  |
| Hyperbolic of tangent    | $`\tanh(x)`$ | **`tanh(`** *x* **`)`**  |
| Hyperbolic of arcsine    | $`\sinh^{-1}(x)`$ | **`asinh(`** *x* **`)`** |
| Hyperbolic of arccosine  | $`\cosh^{-1}(x)`$ | **`acosh(`** *x* **`)`** |
| Hyperbolic of arctangent | $`\tanh^{-1}(x)`$ | **`atanh(`** *x* **`)`** |
