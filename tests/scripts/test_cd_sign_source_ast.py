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


def test_digest_covers_the_helper_closure_and_nothing_else() -> None:
    source = source_ast.SOURCE.read_text(encoding="utf-8")
    term = source_ast.generated(source)
    if source_ast.generated(source + "\n\ndef unrelated() -> int:\n    return 1\n") != term:
        raise AssertionError("a definition cd_sign never reaches changed the certificate block")
    helper = source.replace(
        "def _index(dim: int, index: int) -> int:\n", "def _index(dim: int, index: int) -> int:\n    pass\n", 1
    )
    if helper == source or source_ast.generated(helper) == term:
        raise AssertionError("an edit to a helper cd_sign calls left the source digest unchanged")
    rebindings = {
        "a later helper rebinding": "\n\n_dimension = None\n",
        "a rebinding of cd_sign itself": "\n\ncd_sign = lambda *args: 0\n",
        "a helper rebound inside a module-level conditional": "\n\nif True:\n    _index = lambda dim, index: 0\n",
        "a helper rebound through a global declaration": (
            "\n\ndef patch():\n    global _dimension\n    _dimension = None\n"
        ),
    }
    for label, suffix in rebindings.items():
        if source_ast.generated(source + suffix) == term:
            raise AssertionError(f"{label} left the source digest unchanged")
    if source_ast.generated(source + "\n\nsign = 123\nhalf = 4\n") != term:
        raise AssertionError("a module-level name shadowed by a cd_sign local changed the certificate block")
    local = (
        "\n\ndef unrelated() -> int:\n    from operator import index as integer_index\n"
        "    _index = 1\n    return _index\n"
    )
    if source_ast.generated(source + local) != term:
        raise AssertionError("names local to an unrelated function changed the certificate block")
    if source_ast.generated(source + "\n\nerror = 123\n") != term:
        raise AssertionError("a module-level name that a helper's except target shadows changed the certificate block")
    default = "\n\ndef unrelated(value=(_index := lambda dim, index: 0)):\n    return value\n"
    if source_ast.generated(source + default) == term:
        raise AssertionError("a helper rebound by a default expression left the source digest unchanged")
    nested = "\n\nif True:\n    def unrelated(value=(_index := lambda dim, index: 0)):\n        pass\n"
    if source_ast.generated(source + nested) == term:
        raise AssertionError("a default expression under a module-level conditional left the source digest unchanged")
    rest = "\n\nmatch {}:\n    case {**_index}:\n        pass\n"
    if source_ast.generated(source + rest) == term:
        raise AssertionError("a mapping-rest capture rebinding a helper left the source digest unchanged")
    if source_ast.generated(source + "\n\nindices = [_index for _index in range(3)]\n") != term:
        raise AssertionError("a comprehension target named after a helper changed the certificate block")
    if source_ast.generated(source + "\n\nvalues = [(_index := 0) for item in range(3)]\n") == term:
        raise AssertionError("an assignment expression rebinding a helper left the source digest unchanged")
    with pytest.raises(source_ast.UnsupportedValue):
        source_ast.closure_source(source + "\n\nfrom math import *\n")
    closure = source_ast.closure_source(source)
    for name in ["def cd_sign(", "def _dimension(", "def _index(", "import index as integer_index"]:
        if name not in closure:
            raise AssertionError(f"the helper closure omits {name}")


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
