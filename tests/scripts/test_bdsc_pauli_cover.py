import bdsc_pauli
import pytest


def _check(condition: object, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_bank_is_the_antisymmetric_set() -> None:
    bank = bdsc_pauli.antisymmetric_bank()
    _check(len(bank) == 28, f"{len(bank)} words")
    _check(sum("I" not in w for w in bank) == 13, "13 full-support words")
    _check(all(w[0] == "Y" and w[1:].count("Y") % 2 == 1 for w in bank), "Y on q3 and odd Y count in Q")


def test_least_cx_reads_a_product_set_locally() -> None:
    setting = bdsc_pauli.least_cx(("YIIY", "YIXY", "YXIY", "YXXY"))
    _check(setting["cx"] == 0, f"{setting['cx']} CX")
    bdsc_pauli.verify_setting(setting)


def test_least_cx_needs_two_for_the_ghz_class() -> None:
    setting = bdsc_pauli.least_cx(("YYYY", "YYZX", "YZYX", "YZZY"))
    _check(setting["cx"] == 2, f"{setting['cx']} CX")
    bdsc_pauli.verify_setting(setting)


def test_verify_setting_rejects_a_dropped_cx() -> None:
    setting = bdsc_pauli.least_cx(("YIYZ", "YIZY", "YXYZ", "YXZY"))
    _check(setting["cx"] == 1, f"{setting['cx']} CX")
    broken = {**setting, "cx_control_target": []}
    with pytest.raises(ValueError, match="off-diagonal"):
        bdsc_pauli.verify_setting(broken)


def test_commuting_cover_needs_seven_settings() -> None:
    cover = bdsc_pauli.commuting_cover(bdsc_pauli.antisymmetric_bank())
    _check(cover["largest_commuting_set"] == 4, "largest commuting set")
    _check(cover["minimum_settings"] == len(cover["chosen_cover"]) == 7, "seven settings")
    words = sorted(w for s in cover["chosen_cover"] for w in s["words"])
    _check(words == bdsc_pauli.antisymmetric_bank(), "the chosen cover reads every word once")
    total = sum(s["cx"] for s in cover["chosen_cover"])
    _check(total == cover["cover_total_cx_range"][0], f"chosen cover uses {total} CX")
