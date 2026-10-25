"""Source identity and lossless serialization contracts for the Rocq translation validator."""

from __future__ import annotations

import ast
import hashlib

import cd_sign_source_ast as source_ast
import pytest


def test_complete_source_export_and_digest_match_the_certificate() -> None:
    source = source_ast.SOURCE.read_bytes()
    proof = source_ast.PROOF.read_text(encoding="utf-8")
    start, stop = source_ast.span(proof)
    term = source_ast.generated(source.decode("utf-8"))
    closure = source_ast.closure_source(source.decode("utf-8")).encode("utf-8")
    if proof[start:stop] != term or hashlib.sha256(closure).hexdigest() not in term:
        raise AssertionError("the complete raw source AST or its exact source-byte digest differs")


# A small module shaped like cd_core's cd_sign and its helpers, so the closure contract does not depend on the
# spelling of the retained source, which other changes legitimately edit.
FIXTURE = """from operator import index as integer_index


def _dimension(dim: int) -> None:
    if dim < 1:
        raise ValueError(dim)


def _index(dim: int, index: int) -> int:
    try:
        value = integer_index(index)
    except TypeError as error:
        raise ValueError(index) from error
    return value


def cd_sign(dim: int, p: int, q: int) -> int:
    _dimension(dim)
    sign = 1
    half = dim >> 1
    p = _index(dim, p)
    return sign * half * p
"""


def closure(text: str) -> str:
    return source_ast.closure_source(text)


def test_closure_holds_cd_sign_and_its_helpers_only() -> None:
    selected = closure(FIXTURE)
    for name in ["def cd_sign(", "def _dimension(", "def _index(", "import index as integer_index"]:
        if name not in selected:
            raise AssertionError(f"the helper closure omits {name}")
    unchanged = {
        "an unreached definition": "\n\ndef unrelated() -> int:\n    return 1\n",
        "module names shadowed by cd_sign locals": "\n\nsign = 123\nhalf = 4\n",
        "names local to an unrelated function": (
            "\n\ndef unrelated() -> int:\n    from operator import index as integer_index\n"
            "    _index = 1\n    return _index\n"
        ),
        "a module name shadowed by a helper's except target": "\n\nerror = 123\n",
        "a comprehension target named after a helper": "\n\nindices = [_index for _index in range(3)]\n",
    }
    for label, suffix in unchanged.items():
        if closure(FIXTURE + suffix) != selected:
            raise AssertionError(f"{label} changed the helper closure")


def test_every_module_scope_rebinding_enters_the_closure() -> None:
    selected = closure(FIXTURE)
    rebindings = {
        "a helper edit": FIXTURE.replace("    return value\n", "    return value + 0\n", 1),
        "a later helper rebinding": FIXTURE + "\n\n_dimension = None\n",
        "a rebinding of cd_sign itself": FIXTURE + "\n\ncd_sign = lambda *args: 0\n",
        "a helper rebound in a module-level conditional": FIXTURE + "\n\nif True:\n    _index = lambda d, i: 0\n",
        "a helper rebound through a global declaration": (
            FIXTURE + "\n\ndef patch():\n    global _dimension\n    _dimension = None\n"
        ),
        "a helper rebound by a default expression": (
            FIXTURE + "\n\ndef unrelated(value=(_index := lambda d, i: 0)):\n    return value\n"
        ),
        "a default expression under a module-level conditional": (
            FIXTURE + "\n\nif True:\n    def unrelated(value=(_index := lambda d, i: 0)):\n        pass\n"
        ),
        "a mapping-rest capture": FIXTURE + "\n\nmatch {}:\n    case {**_index}:\n        pass\n",
        "an assignment expression in a comprehension": FIXTURE + "\n\nvalues = [(_index := 0) for item in range(3)]\n",
    }
    for label, text in rebindings.items():
        if text == FIXTURE or closure(text) == selected:
            raise AssertionError(f"{label} left the helper closure unchanged")
    with pytest.raises(source_ast.UnsupportedValue):
        closure(FIXTURE + "\n\nfrom math import *\n")


def test_a_nested_global_declaration_reaches_module_scope() -> None:
    nested = FIXTURE.replace(
        "    try:\n        value = integer_index(index)\n",
        "    integer_index = None\n\n    def convert(item: int) -> int:\n        global integer_index\n"
        "        return integer_index(item)\n\n    try:\n        value = convert(index)\n",
        1,
    )
    if nested == FIXTURE or "import index as integer_index" not in closure(nested):
        raise AssertionError("a nested global declaration hid the module-level integer_index from the closure")
    replaced = nested.replace("from operator import index as integer_index", "integer_index = lambda value: 0", 1)
    if closure(replaced) == closure(nested):
        raise AssertionError("replacing the module-level integer_index left the closure unchanged")


def test_semantic_mutations_change_raw_tree_without_target_translation() -> None:
    source = source_ast.SOURCE.read_text(encoding="utf-8")
    original = source_ast.raw_term(source_ast.function_node(source))
    guard = source_ast.raw_term(source_ast.function_node(source.replace(source_ast.MUTANT_OLD, source_ast.MUTANT_NEW)))
    shift = source_ast.raw_term(source_ast.function_node(source.replace("half >>= 1", "half >>= 2")))
    if original == guard or original == shift or '"NotEq"' not in original or '"NotEq"' in guard:
        raise AssertionError("a semantic mutation was lost by the raw serializer")


def test_unknown_constructs_and_contexts_remain_data() -> None:
    term = source_ast.raw_term(ast.parse("x = [item * 2 for item in values]").body[0])
    for tag in ["ListComp", "comprehension", "Mult", "Load", "Store"]:
        if f'"{tag}"' not in term:
            raise AssertionError(f"the raw serializer dropped {tag}")


def test_annotations_and_docstring_are_serialized() -> None:
    term = source_ast.raw_term(source_ast.function_node('def cd_sign(x: int) -> int:\n    "doc"\n    return x\n'))
    for item in ['"annotation"', '"returns"', '(PStr "doc")', '"type_comment"', '"type_params"']:
        if item not in term:
            raise AssertionError(f"the raw serializer dropped function metadata {item}")


def test_boolean_integer_and_string_atoms_are_distinct() -> None:
    if source_ast.raw_term(True) != "(PBool true)" or source_ast.raw_term(1) != "(PInt (1)%Z)":
        raise AssertionError("boolean and integer leaves were conflated")
    if source_ast.raw_term("1") != '(PStr "1")' or source_ast.raw_term(None) != "PNone":
        raise AssertionError("string or None leaves changed their representation")


def test_string_data_cannot_escape_a_rocq_literal() -> None:
    if source_ast.string_term('a"b') != '"a""b"':
        raise AssertionError("Rocq quotes were not doubled")
    for value in ["line\nbreak", "λ", "\x00"]:
        expected = "(utf8 (" + " :: ".join(f"{byte}%nat" for byte in value.encode("utf-8")) + " :: nil))"
        if source_ast.string_term(value) != expected:
            raise AssertionError("nonprintable or non-ASCII string data escaped its UTF-8 byte term")


def test_selection_refuses_missing_or_duplicate_function() -> None:
    for source in ["def other():\n    pass\n", "def cd_sign():\n    pass\ndef cd_sign():\n    pass\n"]:
        with pytest.raises(source_ast.UnsupportedValue):
            source_ast.function_node(source)


def test_unrepresented_leaf_is_refused() -> None:
    for value in [1.5, b"bytes", complex(1, 2), {"key": "value"}]:
        with pytest.raises(source_ast.UnsupportedValue):
            source_ast.raw_term(value)
