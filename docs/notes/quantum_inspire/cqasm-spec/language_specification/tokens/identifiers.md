> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/identifiers.html](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/identifiers.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 b6180b7e3221040c6e8e616c790bdd907b29f9c384b2e30939c66f08e1a21cf3;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# Identifiers

An identifier is a single character or a sequence of characters of the following form: upper or lowercase letters from the ISO basic Latin alphabet, underscore, and digits, with the constraint that the first (or singular) character cannot be a digit.

For now, they are used to name qubits and bits (registers) by the user, and predefine the names of useful [mathematical constants](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/expressions/predefined_constants.html), [built-in functions](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/expressions/builtin_functions.html), and [named gates](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/unitary_instructions.html#named-gates). Note that identifiers are not protected, *i.e.* they can be reused. For example, it is permissible, however discouraged, to name a (qu)bit (register) **`pi`**, **`cos`**, or **`Rx`**.

Reserved [keywords](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/keywords.html) cannot be used as an identifier.

Grammar for identifiers

*identifier*:\
  *letter*\
  *identifier* *letter*\
  *identifier* *digit*

*letter*: one of\
  **`a`** through **`z`** or **`A`** through **`Z`** or **`_`**

Examples

Valid identifiersInvalid identifiers

```
q
_i
ID
b01
```

```
1q     // first character cannot be a digit
+q     // the underscore '_' is the only permissible special character 
qubit  // 'qubit' is a reserved keyword
```
