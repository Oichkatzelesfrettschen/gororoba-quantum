"""Project one PUB's aligned register shots onto declared error observables.

The caller must authenticate the raw bytes, manifest and provider identities.
The projection pairs register list positions within the supplied PUB record;
equal lengths alone cannot authenticate that the provider aligned those lists.
The projection makes no claim about physical predecessor order or statistical
independence and does not emit an acquisition or confidence decision.
The aggregate-work ceiling counts shots times the sum of input register widths
and declared projection widths. It is an interface limit, not a universal
runtime or memory guarantee.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

import numpy as np

BATCH_SHOTS = 2048
MAX_SHOTS = 1_000_000
MAX_REGISTER_BITS = 4096
MAX_PROJECTIONS = 10_000
MAX_WORK_UNITS = 250_000_000


def _integer(value: Any, lower: int, upper: int, field: str) -> int:
    if type(value) is not int or not lower <= value <= upper:
        raise ValueError(f"{field} must be a bounded integer")
    return value


def _name(value: Any, field: str) -> str:
    if type(value) is not str or not value or len(value) > 256:
        raise ValueError(f"{field} must be a nonempty bounded string")
    return value


def project_pub(raw_pub: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    """Return declared paired error tables and error parity counts for one PUB."""
    required = {"schema", "condition", "pub_name", "pub_index", "registers", "bits", "pairs", "groups"}
    if type(manifest) is not dict or set(manifest) != required or manifest["schema"] != "readout-sparse-projection-v1":
        raise ValueError("a complete supported projection manifest is required")
    condition = _name(manifest["condition"], "condition")
    pub_name = _name(manifest["pub_name"], "PUB name")
    pub_index = _integer(manifest["pub_index"], 0, 1_000_000, "PUB index")
    if (
        type(raw_pub) is not dict
        or raw_pub.get("pub_name") != pub_name
        or type(raw_pub.get("pub_index")) is not int
        or raw_pub["pub_index"] != pub_index
    ):
        raise ValueError("raw PUB identity differs from the manifest")
    widths = manifest["registers"]
    registers = raw_pub.get("registers")
    if type(widths) is not dict or not widths or type(registers) is not dict or set(registers) != set(widths):
        raise ValueError("raw and declared register names must match exactly")
    for name, width in widths.items():
        _name(name, "register name")
        _integer(width, 1, MAX_REGISTER_BITS, "register width")
    if sum(widths.values()) > MAX_REGISTER_BITS:
        raise ValueError("the total register width exceeds the projection limit")
    declared_bits = manifest["bits"]
    if type(declared_bits) is not list or len(declared_bits) != sum(widths.values()):
        raise ValueError("the manifest must map every declared classical bit")
    by_logical: dict[int, dict[str, Any]] = {}
    destinations: set[tuple[str, int]] = set()
    physical_bits: set[int] = set()
    for bit in declared_bits:
        if type(bit) is not dict or set(bit) != {"register", "index", "logical", "physical", "prepared"}:
            raise ValueError("each bit requires register, index, logical, physical and prepared fields")
        name = _name(bit["register"], "register name")
        if name not in widths:
            raise ValueError("mapped register is absent")
        index = _integer(bit["index"], 0, widths[name] - 1, "classical index")
        logical = _integer(bit["logical"], 0, MAX_REGISTER_BITS - 1, "logical index")
        physical = _integer(bit["physical"], 0, MAX_REGISTER_BITS - 1, "physical index")
        _integer(bit["prepared"], 0, 1, "prepared bit")
        if (name, index) in destinations or logical in by_logical or physical in physical_bits:
            raise ValueError("classical, logical and physical mappings must be injective")
        destinations.add((name, index))
        physical_bits.add(physical)
        by_logical[logical] = bit
    for name, width in widths.items():
        if any((name, index) not in destinations for index in range(width)):
            raise ValueError("the manifest omits a declared classical bit")

    def projections(value: Any, minimum: int, maximum: int, label: str) -> list[list[int]]:
        if type(value) is not list or len(value) > MAX_PROJECTIONS:
            raise ValueError(f"{label} must be a bounded list")
        result: list[list[int]] = []
        seen: set[tuple[int, ...]] = set()
        for row in value:
            if type(row) is not list or not minimum <= len(row) <= maximum:
                raise ValueError(f"{label} has an invalid projection width")
            if any(type(bit) is not int or bit not in by_logical for bit in row):
                raise ValueError(f"{label} names an unknown logical bit")
            key = tuple(row)
            if len(set(row)) != len(row) or key in seen:
                raise ValueError(f"{label} contains repeated bits or projections")
            seen.add(key)
            result.append(row)
        return result

    pairs = projections(manifest["pairs"], 2, 2, "pairs")
    groups = projections(manifest["groups"], 1, MAX_REGISTER_BITS, "groups")
    if not pairs and not groups:
        raise ValueError("at least one declared projection is required")
    selected = sorted({bit for row in pairs + groups for bit in row})
    selected_columns = {logical: index for index, logical in enumerate(selected)}
    selected_by_register: dict[str, list[tuple[int, int, int]]] = {name: [] for name in widths}
    for logical in selected:
        bit = by_logical[logical]
        selected_by_register[bit["register"]].append((selected_columns[logical], bit["index"], bit["prepared"]))
    shot_count: int | None = None
    for name, width in widths.items():
        register = registers[name]
        if type(register) is not dict or type(register.get("bitstrings")) is not list:
            raise ValueError("each raw register must contain ordered bitstrings")
        if _integer(register.get("num_bits"), 1, MAX_REGISTER_BITS, "raw register width") != width:
            raise ValueError("raw register width differs from the manifest")
        count = _integer(register.get("num_shots"), 1, MAX_SHOTS, "raw shot count")
        if len(register["bitstrings"]) != count or (shot_count is not None and count != shot_count):
            raise ValueError("all registers must contain the same declared shot count")
        shot_count = count
    if shot_count is None:
        raise ValueError("at least one register is required")
    work_units = shot_count * (sum(widths.values()) + 2 * len(pairs) + sum(len(group) for group in groups))
    if work_units > MAX_WORK_UNITS:
        raise ValueError("declared aggregate projection work exceeds the interface limit")
    pair_counts = np.zeros((len(pairs), 4), dtype=np.int64)
    group_counts = np.zeros((len(groups), 2), dtype=np.int64)
    register_hashes = {name: hashlib.sha256() for name in widths}
    for start in range(0, shot_count, BATCH_SHOTS):
        stop = min(start + BATCH_SHOTS, shot_count)
        selected_errors = np.zeros((stop - start, len(selected)), dtype=np.uint8)
        for name, width in widths.items():
            batch = registers[name]["bitstrings"][start:stop]
            if any(type(shot) is not str or len(shot) != width for shot in batch):
                raise ValueError("raw bitstrings must match the declared width")
            try:
                encoded = "".join(batch).encode("ascii")
            except UnicodeEncodeError as error:
                raise ValueError("raw bitstrings must contain binary characters") from error
            raw_bits = np.frombuffer(encoded, dtype=np.uint8).reshape(stop - start, width)
            if not np.all((raw_bits == ord("0")) | (raw_bits == ord("1"))):
                raise ValueError("raw bitstrings must contain binary characters")
            register_hashes[name].update(encoded)
            for column, classical_index, prepared in selected_by_register[name]:
                selected_errors[:, column] = (raw_bits[:, width - 1 - classical_index] - ord("0")) ^ prepared
        for index, pair in enumerate(pairs):
            cells = 2 * selected_errors[:, selected_columns[pair[0]]] + selected_errors[:, selected_columns[pair[1]]]
            pair_counts[index] += np.bincount(cells, minlength=4)
        for index, group in enumerate(groups):
            parity = np.bitwise_xor.reduce(selected_errors[:, [selected_columns[bit] for bit in group]], axis=1)
            group_counts[index] += np.bincount(parity, minlength=2)
    manifest_bytes = json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    return {
        "schema": "readout-sparse-projection-result-v1",
        "manifest_canonical_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "condition": condition,
        "pub_name": pub_name,
        "pub_index": pub_index,
        "num_shots": shot_count,
        "work_units": work_units,
        "shot_index": {"first": 0, "stop_exclusive": shot_count, "meaning": "within-PUB list position"},
        "register_bitstrings_sha256": {name: digest.hexdigest() for name, digest in register_hashes.items()},
        "alignment": "Equal list positions are paired; physical same-shot alignment remains unauthenticated.",
        "pair_counts": [
            {"logical_bits": list(pair), "error_cells_00_01_10_11": pair_counts[index].tolist()}
            for index, pair in enumerate(pairs)
        ],
        "group_counts": [
            {"logical_bits": list(group), "error_parity_even_odd": group_counts[index].tolist()}
            for index, group in enumerate(groups)
        ],
        "boundary": (
            "Descriptive projection only; raw identity, physical mapping, "
            "predecessor order and inference are unauthenticated."
        ),
    }
