> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/assembly_declaration.html](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/assembly_declaration.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 3cd386af7ea28399ab88926bd209cd3ecad994a0985b5763275aa77eaa9fe687;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# Assembly declaration

Assembly declarations can be used to add backend-specific (assembly) code to a cQASM circuit. They are realized through an **`asm`** *declaration* statement. An **`asm`** declaration statement consists of the keyword **`asm`** with the [identifier](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/identifiers.html) of the backend in parentheses, followed by the backend code. The latter is to be provided as a [*raw text string*](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/raw_text_string.html), which consists of a *raw text* delimited by opening and closing triple quotes (**`'''`**):

  **`asm(`***backend-identifier***`)`** *backend-code*

Grammar for assembly declaration

*assembly-declaration*:\
  **`asm(`***backend-identifier***`)`** *backend-code*

*backend-identifier*:\
  *identifier*

*backend-code*:\
  *raw-text-string*

As part of a cQASM circuit, the contents of the raw text string will be passed verbatim to the backend and ignored by all other consumers of the circuit.

The location of the **`asm`** declaration in the cQASM circuit is preserved, *i.e.*, no cQASM statements can be moved across it by any subsequent processing of the cQASM circuit. This allows for the ability to embed backend code into cQASM with the guarantee that the relative order between cQASM and backend code remains the same.

The following example shows how sections of code, specific to the example `Backend`, can be interlaced with cQASM statements:

```
version 3.0

qubit[4] q
bit[2]

asm(Backend) '''
    POS(0, 0) q[0]
    POS(1, 0) q[1]
    POS(0, 1) q[2]
    POS(1, 1) q[3]
'''

init q

X q[0]

asm(Backend) '''
    PULSE(0.000467, -0.971166, 0.157596)
    PULSE(0.001868, -0.942333, 0.157596)
    PULSE(0.004196, -0.913500, 0.157596)
    PULSE(0.007442, -0.884666, 0.157596)
'''

H q
CNOT q[0], q[1]

b = measure q[0, 1]
```
