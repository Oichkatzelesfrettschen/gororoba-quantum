> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/newlines.html](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/newlines.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 0de92a13eff50469c415e9a4c4307f97f0161691cf010b97033db836c31f3625;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# Newlines

cQASM is newline-sensitive, *i.e.* a newline terminates a statement.

A semicolon **`;`** may be used instead of a newline to separate statements, for instance when putting multiple statements on the same line. Semicolons can also be put at the end of the line for clarity without changing the semantics of the program.
