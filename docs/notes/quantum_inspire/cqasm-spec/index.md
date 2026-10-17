> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/index.html](https://qutech-delft.github.io/cQASM-spec/latest/index.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 40eac59fd190c1b2d381ec64476548a8e172cedc21056859ee4633767c77bfde;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# Home

This documentation describes the language specification of the cQASM quantum programming language, version 3.0. cQASM stands for common Quantum ASseMbly language, and is pronounced *c-kazem*.

cQASM 3.0 supersedes the [cQASM 1.\[012\] languages](https://libqasm.readthedocs.io/en/latest/) and [cQASM 2.0 language specification](https://github.com/QuTech-Delft/cQASM-spec/tree/2.0-draft-2), the latter of which remains incomplete.

Note

Even though cQASM 3.0 is conceptually similar to previous language specifications, it is not a straightforward extension thereof; the syntax and grammar of cQASM 3.0 differ fundamentally from its predecessors. These changes break backwards compatibility.

In the rest of the documentation we will drop the version label of language and simply refer to it as the cQASM language.

Warning

The cQASM language is currently under active development. cQASM 3.0 serves as a minimum viable product; to be used as a baseline version for the further development of, *e.g.*, the [libQASM](https://github.com/QuTech-Delft/libqasm) language parser library, [OpenSquirrel](https://github.com/QuTech-Delft/OpenSquirrel) quantum algorithm compiler, and [QX simulator](https://github.com/QuTech-Delft/qx-simulator). The cQASM specification will be updated as new features are introduced to the language. Where applicable, these features are then also implemented in the aformentioned software components, in an iterative fashion.
