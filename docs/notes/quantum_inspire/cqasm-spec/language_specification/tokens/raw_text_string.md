> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/raw_text_string.html](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/raw_text_string.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 623c71598437b84a1361e33659e02c05aa3d4549da253b21f4d80d5f847dac98;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# Raw text string

A raw text string is a sequence of zero or more characters delimited by triple quotes. Any character, including whitespaces, comments, and newlines, can be part of a raw text string.

Grammar for raw text string

*raw-text-string*:\
  **`'''`** raw-text_(opt) **`'''`**

*raw-text*:\
  raw-char\
  raw-text raw-char

*raw-char*:\
  any character

Warning

Even though any sequence of characters could be raw text, one should avoid using triple qoutes (**`'''`**) as they will be interpreted as the delimiters of the raw text string.
