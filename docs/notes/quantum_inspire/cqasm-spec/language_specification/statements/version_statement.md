> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/version_statement.html](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/version_statement.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 86207bf7deb1365a603e4b3744aad1476d8359480b7052c1b115e7b9c4c9e066;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# Version statement

The version statement is mandatory and indicates which version of the cQASM language the program is written in. Apart from comments, it must be the first statement of the program and occur only once. It has the following general form:

 **`version`** *major-version***`.`***minor-version*

Grammar for version statement

*version*:\
 **`version`** *major-version* *minor-version-suffix*_(opt)

*major-version*:\
  *digit-sequence*

*minor-version-suffix*:\
  **`.`** *minor-version*

*minor-version*:\
  *digit-sequence*

where the version number is to be given as two period separated integers, respectively indicating the major and minor version of the cQASM language. It is permitted to only specify the major version number, *i.e.*, the specification of the minor version number is optional. In that case, the *minor-version* will be interpreted as **`0`**.

Example

```
// Only comments may appear before the version statement.
version 3.0
```
