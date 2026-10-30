"""Source association rejects substituted provider resources before scoring."""

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest


def test_slot_binding_refuses_the_other_arm_manifest() -> None:
    from qi_tuna_source_association import validate_slot_binding

    root = Path(__file__).resolve().parents[2] / "results/quantum_inspire/proposals/tuna-destination-slot-alternatives"
    catalogue = (root / "catalogue.json").read_bytes()
    manifest = (root / "slot-01/baseline/cases.json").read_bytes()
    source = (root / "slot-01/baseline/baseline-before.cq").read_bytes()
    with pytest.raises(ValueError):
        validate_slot_binding(catalogue, hashlib.sha256(catalogue).hexdigest(), 1, "rotated", manifest, source)


@pytest.mark.parametrize("arm,filename", [("baseline", "baseline-before.cq"), ("rotated", "rotated-destinations.cq")])
def test_slot_binding_accepts_catalogue_selected_source(arm: str, filename: str) -> None:
    from qi_tuna_source_association import validate_slot_binding

    root = Path(__file__).resolve().parents[2] / "results/quantum_inspire/proposals/tuna-destination-slot-alternatives"
    catalogue = (root / "catalogue.json").read_bytes()
    manifest = (root / f"slot-01/{arm}/cases.json").read_bytes()
    source = (root / f"slot-01/{arm}/{filename}").read_bytes()
    validate_slot_binding(catalogue, hashlib.sha256(catalogue).hexdigest(), 1, arm, manifest, source)


def test_slot_binding_accepts_all_retained_catalogue_alternatives() -> None:
    from qi_tuna_source_association import validate_slot_binding

    root = Path(__file__).resolve().parents[2] / "results/quantum_inspire/proposals/tuna-destination-slot-alternatives"
    catalogue = (root / "catalogue.json").read_bytes()
    digest = hashlib.sha256(catalogue).hexdigest()
    for slot in range(1, 25):
        for arm, filename in (("baseline", "baseline-before.cq"), ("rotated", "rotated-destinations.cq")):
            directory = root / f"slot-{slot:02d}" / arm
            validate_slot_binding(
                catalogue,
                digest,
                slot,
                arm,
                (directory / "cases.json").read_bytes(),
                (directory / filename).read_bytes(),
            )


def test_selected_slot_and_provider_readbacks_must_agree() -> None:
    from qi_tuna_source_association import validate_slot_association

    root = Path(__file__).resolve().parents[2] / "results/quantum_inspire/proposals/tuna-destination-slot-alternatives"
    catalogue = (root / "catalogue.json").read_bytes()
    manifest = (root / "slot-01/baseline/cases.json").read_bytes()
    source = (root / "slot-01/baseline/baseline-before.cq").read_bytes()
    checkpoint = {
        "job": 11,
        "file": 12,
        "commit": 13,
        "batch": 14,
        "backend_type": 7,
        "shots": 4096,
        "language_id": 8,
        "result": 21,
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "slot": 2,
        "arm": "baseline",
        "cases_sha256": hashlib.sha256(manifest).hexdigest(),
        "catalogue_sha256": hashlib.sha256(catalogue).hexdigest(),
    }
    job = {"id": 11, "file_id": 12, "batch_job_id": 14, "number_of_shots": 4096, "raw_data_enabled": True}
    batch = {"id": 14, "backend_type_id": 7, "job_ids": [11]}
    batch_page = {"items": [batch], "total": 1, "page": 1, "size": 100, "pages": 1}
    provider_file = {
        "id": 12,
        "commit_id": 13,
        "language_id": 8,
        "compile_stage": "none",
        "compile_properties": {},
        "content": source.decode("utf-8"),
    }
    page = {"items": [{"id": 21, "job_id": 11}], "total": 1, "page": 1, "size": 100, "pages": 1}
    with pytest.raises(ValueError):
        validate_slot_association(
            catalogue,
            hashlib.sha256(catalogue).hexdigest(),
            1,
            "baseline",
            manifest,
            source,
            checkpoint,
            job,
            batch_page,
            provider_file,
            page,
        )
    checkpoint["slot"] = 1
    validate_slot_association(
        catalogue,
        hashlib.sha256(catalogue).hexdigest(),
        1,
        "baseline",
        manifest,
        source,
        checkpoint,
        job,
        batch_page,
        provider_file,
        page,
    )
    for field in ("arm", "cases_sha256", "catalogue_sha256"):
        original = checkpoint[field]
        checkpoint[field] = "invalid"
        with pytest.raises(ValueError):
            validate_slot_association(
                catalogue,
                hashlib.sha256(catalogue).hexdigest(),
                1,
                "baseline",
                manifest,
                source,
                checkpoint,
                job,
                batch_page,
                provider_file,
                page,
            )
        checkpoint[field] = original
    with pytest.raises(ValueError):
        validate_slot_association(
            catalogue,
            hashlib.sha256(catalogue).hexdigest(),
            1,
            "rotated",
            manifest,
            source,
            checkpoint,
            job,
            batch_page,
            provider_file,
            page,
        )
    checkpoint["backend_type"] = 1
    batch["backend_type_id"] = 1
    with pytest.raises(ValueError):
        validate_slot_association(
            catalogue,
            hashlib.sha256(catalogue).hexdigest(),
            1,
            "baseline",
            manifest,
            source,
            checkpoint,
            job,
            batch_page,
            provider_file,
            page,
        )


def test_slot_binding_rejects_changed_bytes_and_invalid_release() -> None:
    from qi_tuna_source_association import validate_slot_binding

    root = Path(__file__).resolve().parents[2] / "results/quantum_inspire/proposals/tuna-destination-slot-alternatives"
    catalogue = (root / "catalogue.json").read_bytes()
    manifest = (root / "slot-01/baseline/cases.json").read_bytes()
    source = (root / "slot-01/baseline/baseline-before.cq").read_bytes()
    digest = hashlib.sha256(catalogue).hexdigest()
    for supplied_catalogue, supplied_digest, slot, arm, supplied_manifest, supplied_source in (
        (catalogue + b" ", digest, 1, "baseline", manifest, source),
        (catalogue, digest, True, "baseline", manifest, source),
        (catalogue, digest, 25, "baseline", manifest, source),
        (catalogue, digest, 1, "other", manifest, source),
        (catalogue, digest, 1, "baseline", manifest + b" ", source),
        (catalogue, digest, 1, "baseline", manifest, source + b" "),
    ):
        with pytest.raises(ValueError):
            validate_slot_binding(supplied_catalogue, supplied_digest, slot, arm, supplied_manifest, supplied_source)


def test_complete_slot_counts_require_matching_source_result_and_histogram(monkeypatch: pytest.MonkeyPatch) -> None:
    import qi_tuna_source_association
    from qi_tuna_readback_transport import read_qi_json
    from qi_tuna_sequential_score import score_sequence
    from qi_tuna_source_association import decode_associated_complete, decode_associated_complete_bytes

    root = Path(__file__).resolve().parents[2] / "results/quantum_inspire/proposals/tuna-destination-slot-alternatives"
    catalogue = (root / "catalogue.json").read_bytes()
    manifest = (root / "slot-01/baseline/cases.json").read_bytes()
    source = (root / "slot-01/baseline/baseline-before.cq").read_bytes()
    checkpoint = {
        "job": 11,
        "file": 12,
        "commit": 13,
        "batch": 14,
        "backend_type": 7,
        "shots": 4096,
        "language_id": 8,
        "result": 21,
        "slot": 1,
        "arm": "baseline",
        "cases_sha256": hashlib.sha256(manifest).hexdigest(),
        "catalogue_sha256": hashlib.sha256(catalogue).hexdigest(),
        "source_sha256": hashlib.sha256(source).hexdigest(),
    }
    job = {
        "id": 11,
        "file_id": 12,
        "batch_job_id": 14,
        "number_of_shots": 4096,
        "raw_data_enabled": True,
        "status": "completed",
    }
    batch = {"id": 14, "backend_type_id": 7, "job_ids": [11]}
    batch_page = {"items": [batch], "total": 1, "page": 1, "size": 100, "pages": 1}
    provider_file = {
        "id": 12,
        "commit_id": 13,
        "language_id": 8,
        "compile_stage": "none",
        "compile_properties": {},
        "content": source.decode("utf-8"),
    }
    shot = "0" * 20
    result = {
        "id": 21,
        "job_id": 11,
        "shots_requested": 4096,
        "shots_done": 4096,
        "raw_data": [shot] * 4096,
        "results": {shot: 4096},
    }
    page = {"items": [result], "total": 1, "page": 1, "size": 100, "pages": 1}
    decoded = decode_associated_complete(
        catalogue,
        hashlib.sha256(catalogue).hexdigest(),
        1,
        "baseline",
        manifest,
        source,
        checkpoint,
        job,
        batch_page,
        provider_file,
        page,
    )
    if decoded != {"slot": 1, "arm": "baseline", "kind": "complete", "early_ones": 0, "terminal_ones": 0}:
        raise AssertionError("decoded counts differ from the all-zero raw record")
    encoded = [json.dumps(record).encode("utf-8") for record in (checkpoint, job, batch_page, provider_file, page)]
    byte_decoded = decode_associated_complete_bytes(
        catalogue, hashlib.sha256(catalogue).hexdigest(), 1, "baseline", manifest, source, *encoded
    )
    if byte_decoded != decoded:
        raise AssertionError("byte snapshot did not reproduce the associated row")

    class FakeResponse:
        status_code = 200
        headers = {"Content-Type": "application/json"}
        closed = False

        def iter_content(self, chunk_size: int) -> list[bytes]:
            return [encoded[4]]

        def close(self) -> None:
            self.closed = True

    class FakeSession:
        def __init__(self) -> None:
            self.response = FakeResponse()

        def request(self, method: str, url: str, **options: object) -> FakeResponse:
            return self.response

    session = FakeSession()
    receipt = read_qi_json(
        session,
        "/results/job/11",
        {"page": 1, "size": 100},
        lambda _force: None,
        lambda: None,
        timeout_seconds=1.0,
    )
    readback_row = decode_associated_complete_bytes(
        catalogue,
        hashlib.sha256(catalogue).hexdigest(),
        1,
        "baseline",
        manifest,
        source,
        encoded[0],
        encoded[1],
        encoded[2],
        encoded[3],
        receipt.body,
    )
    if readback_row != decoded or not session.response.closed:
        raise AssertionError("byte-preserving readback changed the associated row")
    duplicate_job = encoded[1].replace(b'"id": 11', b'"id": 99, "id": 11', 1)
    with pytest.raises(ValueError):
        decode_associated_complete_bytes(
            catalogue,
            hashlib.sha256(catalogue).hexdigest(),
            1,
            "baseline",
            manifest,
            source,
            encoded[0],
            duplicate_job,
            *encoded[2:],
        )
    for index, original_bytes, duplicate in (
        (0, b'"slot": 1', b'"slot": 2, "slot": 1'),
        (2, b'"total": 1', b'"total": 2, "total": 1'),
        (3, b'"language_id": 8', b'"language_id": 9, "language_id": 8'),
        (3, b'"compile_stage": "none"', b'"compile_stage": "bad", "compile_stage": "none"'),
        (3, b'"compile_properties": {}', b'"compile_properties": {"bad": true}, "compile_properties": {}'),
        (3, b'"content":', b'"content": "bad", "content":'),
        (4, b'"job_id": 11', b'"job_id": 99, "job_id": 11'),
    ):
        altered = encoded.copy()
        altered[index] = altered[index].replace(original_bytes, duplicate, 1)
        if altered[index] == encoded[index]:
            raise AssertionError("duplicate-key mutation did not apply")
        with pytest.raises(ValueError):
            decode_associated_complete_bytes(
                catalogue, hashlib.sha256(catalogue).hexdigest(), 1, "baseline", manifest, source, *altered
            )
    for nonfinite in (b"NaN", b"Infinity", b"-Infinity", b"1e400", b"-1e400"):
        altered = encoded.copy()
        altered[1] = altered[1][:-1] + b', "extra": ' + nonfinite + b"}"
        with pytest.raises(ValueError):
            decode_associated_complete_bytes(
                catalogue, hashlib.sha256(catalogue).hexdigest(), 1, "baseline", manifest, source, *altered
            )
    for field, invalid_metadata in (
        ("bit_order", "classical bit zero is the leftmost character"),
        ("index_convention", "different indexing"),
        ("canonical_early_string_offsets", [0, 1, 2]),
        ("decoder_rule", "different decoding"),
        ("measurement_to_bit_map", "missing"),
        ("measurement_to_bit_map", "duplicate"),
        ("measurement_to_bit_map", "reordered"),
        ("measurement_to_bit_map", "boolean"),
        ("measurement_to_bit_map", "conflicting"),
    ):
        changed_manifest = json.loads(manifest)
        if field == "measurement_to_bit_map":
            mapping = changed_manifest["circuits"][0][field]
            if invalid_metadata == "missing":
                mapping.pop()
            elif invalid_metadata == "duplicate":
                mapping.append(dict(mapping[0]))
            elif invalid_metadata == "reordered":
                mapping[0], mapping[1] = mapping[1], mapping[0]
            elif invalid_metadata == "boolean":
                mapping[0]["qubit"] = True
            else:
                mapping[0]["classical_bit"] = 0
        else:
            changed_manifest["circuits"][0]["analysis_metadata"][field] = invalid_metadata
        changed_manifest_bytes = json.dumps(changed_manifest).encode()
        changed_catalogue = json.loads(catalogue)
        row = next(
            item for item in changed_catalogue["alternatives"] if item["slot"] == 1 and item["arm"] == "baseline"
        )
        row["cases_sha256"] = hashlib.sha256(changed_manifest_bytes).hexdigest()
        changed_catalogue_bytes = json.dumps(changed_catalogue).encode()
        changed_checkpoint = dict(checkpoint)
        changed_checkpoint["cases_sha256"] = hashlib.sha256(changed_manifest_bytes).hexdigest()
        changed_checkpoint["catalogue_sha256"] = hashlib.sha256(changed_catalogue_bytes).hexdigest()
        with pytest.raises(ValueError):
            decode_associated_complete(
                changed_catalogue_bytes,
                hashlib.sha256(changed_catalogue_bytes).hexdigest(),
                1,
                "baseline",
                changed_manifest_bytes,
                source,
                changed_checkpoint,
                job,
                batch_page,
                provider_file,
                page,
            )
    if score_sequence([decoded])["processes"]["early_positive"]["value"] != Fraction(39, 20):
        raise AssertionError("the associated response did not reach the expected exact score")
    early_only = "1" + "0" * 19
    result["raw_data"] = [early_only] * 4096
    result["results"] = {early_only: 4096}
    asymmetric = decode_associated_complete(
        catalogue,
        hashlib.sha256(catalogue).hexdigest(),
        1,
        "baseline",
        manifest,
        source,
        checkpoint,
        job,
        batch_page,
        provider_file,
        page,
    )
    if asymmetric["early_ones"] != 4096 or asymmetric["terminal_ones"] != 0:
        raise AssertionError("associated baseline record did not preserve distinct response destinations")
    decoder = qi_tuna_source_association.decode_counts
    monkeypatch.setattr(
        qi_tuna_source_association, "decode_counts", lambda _arm, _raw: {"early_ones": 0, "terminal_ones": 0}
    )
    with pytest.raises(ValueError):
        decode_associated_complete(
            catalogue,
            hashlib.sha256(catalogue).hexdigest(),
            1,
            "baseline",
            manifest,
            source,
            checkpoint,
            job,
            batch_page,
            provider_file,
            page,
        )
    monkeypatch.setattr(qi_tuna_source_association, "decode_counts", decoder)
    result["raw_data"] = [shot] * 4096
    result["results"] = {shot: 4095}
    with pytest.raises(ValueError):
        decode_associated_complete(
            catalogue,
            hashlib.sha256(catalogue).hexdigest(),
            1,
            "baseline",
            manifest,
            source,
            checkpoint,
            job,
            batch_page,
            provider_file,
            page,
        )
    result["results"] = {shot: 4096}
    for record, key, invalid in (
        (job, "status", "running"),
        (result, "shots_requested", True),
        (result, "shots_done", 4095),
        (result, "raw_data", [shot] * 4095),
        (result, "raw_data", ["x" * 20] * 4096),
        (result, "results", {shot: True}),
        (result, "results", {shot: 4096, "not-a-width-20-shot": 0}),
    ):
        original = record[key]
        record[key] = invalid
        with pytest.raises(ValueError):
            decode_associated_complete(
                catalogue,
                hashlib.sha256(catalogue).hexdigest(),
                1,
                "baseline",
                manifest,
                source,
                checkpoint,
                job,
                batch_page,
                provider_file,
                page,
            )
        record[key] = original


def test_slot_binding_rejects_duplicate_catalogue_keys_even_with_matching_digest() -> None:
    from qi_tuna_source_association import validate_slot_binding

    root = Path(__file__).resolve().parents[2] / "results/quantum_inspire/proposals/tuna-destination-slot-alternatives"
    catalogue = (root / "catalogue.json").read_bytes().replace(b'"schema":', b'"schema":"bad","schema":', 1)
    manifest = (root / "slot-01/baseline/cases.json").read_bytes()
    source = (root / "slot-01/baseline/baseline-before.cq").read_bytes()
    with pytest.raises(ValueError):
        validate_slot_binding(catalogue, hashlib.sha256(catalogue).hexdigest(), 1, "baseline", manifest, source)


def test_rotated_associated_record_uses_rotated_early_destination() -> None:
    from qi_tuna_source_association import decode_associated_complete

    root = Path(__file__).resolve().parents[2] / "results/quantum_inspire/proposals/tuna-destination-slot-alternatives"
    catalogue = (root / "catalogue.json").read_bytes()
    manifest = (root / "slot-01/rotated/cases.json").read_bytes()
    source = (root / "slot-01/rotated/rotated-destinations.cq").read_bytes()
    catalogue_digest = hashlib.sha256(catalogue).hexdigest()
    checkpoint = {
        "job": 11,
        "file": 12,
        "commit": 13,
        "batch": 14,
        "backend_type": 7,
        "shots": 4096,
        "language_id": 8,
        "result": 21,
        "slot": 1,
        "arm": "rotated",
        "cases_sha256": hashlib.sha256(manifest).hexdigest(),
        "catalogue_sha256": catalogue_digest,
        "source_sha256": hashlib.sha256(source).hexdigest(),
    }
    job = {
        "id": 11,
        "file_id": 12,
        "batch_job_id": 14,
        "number_of_shots": 4096,
        "raw_data_enabled": True,
        "status": "completed",
    }
    batch_page = {
        "items": [{"id": 14, "backend_type_id": 7, "job_ids": [11]}],
        "total": 1,
        "page": 1,
        "size": 100,
        "pages": 1,
    }
    provider_file = {
        "id": 12,
        "commit_id": 13,
        "language_id": 8,
        "compile_stage": "none",
        "compile_properties": {},
        "content": source.decode("utf-8"),
    }
    shot = "01" + "0" * 18
    result = {
        "id": 21,
        "job_id": 11,
        "shots_requested": 4096,
        "shots_done": 4096,
        "raw_data": [shot] * 4096,
        "results": {shot: 4096},
    }
    page = {"items": [result], "total": 1, "page": 1, "size": 100, "pages": 1}
    row = decode_associated_complete(
        catalogue, catalogue_digest, 1, "rotated", manifest, source, checkpoint, job, batch_page, provider_file, page
    )
    if row["early_ones"] != 4096 or row["terminal_ones"] != 0:
        raise AssertionError("rotated source did not decode its designated early bit")


def test_slot_binding_rejects_noninteger_catalogue_slot_count() -> None:
    from qi_tuna_source_association import validate_slot_binding

    root = Path(__file__).resolve().parents[2] / "results/quantum_inspire/proposals/tuna-destination-slot-alternatives"
    value = json.loads((root / "catalogue.json").read_bytes())
    value["slots"] = 24.0
    catalogue = json.dumps(value).encode()
    manifest = (root / "slot-01/baseline/cases.json").read_bytes()
    source = (root / "slot-01/baseline/baseline-before.cq").read_bytes()
    with pytest.raises(ValueError):
        validate_slot_binding(catalogue, hashlib.sha256(catalogue).hexdigest(), 1, "baseline", manifest, source)


def test_job_must_reference_the_checkpointed_file() -> None:
    from qi_tuna_source_association import validate_association

    source = b"version 3.0\n"
    checkpoint = {
        "job": 11,
        "file": 12,
        "commit": 13,
        "batch": 14,
        "backend_type": 7,
        "shots": 4096,
        "language_id": 8,
        "result": 21,
        "source_sha256": hashlib.sha256(source).hexdigest(),
    }
    job = {"id": 11, "file_id": 99, "batch_job_id": 14, "number_of_shots": 4096, "raw_data_enabled": True}
    batch = {"id": 14, "backend_type_id": 7, "job_ids": [11]}
    provider_file = {
        "id": 12,
        "commit_id": 13,
        "language_id": 8,
        "compile_stage": "none",
        "compile_properties": {},
        "content": source.decode("utf-8"),
    }
    result = {"items": [{"id": 21, "job_id": 11}], "total": 1, "page": 1, "size": 100, "pages": 1}
    with pytest.raises(ValueError):
        validate_association(checkpoint, source, job, batch, provider_file, result)


def test_matching_provider_readback_accepts_the_source_association() -> None:
    from qi_tuna_source_association import validate_association

    source = b"version 3.0\n"
    checkpoint = {
        "job": 11,
        "file": 12,
        "commit": 13,
        "batch": 14,
        "backend_type": 7,
        "shots": 4096,
        "language_id": 8,
        "result": 21,
        "source_sha256": hashlib.sha256(source).hexdigest(),
    }
    job = {"id": 11, "file_id": 12, "batch_job_id": 14, "number_of_shots": 4096, "raw_data_enabled": True}
    batch = {"id": 14, "backend_type_id": 7, "job_ids": [11]}
    provider_file = {
        "id": 12,
        "commit_id": 13,
        "language_id": 8,
        "compile_stage": "none",
        "compile_properties": {},
        "content": source.decode("utf-8"),
    }
    page = {"items": [{"id": 21, "job_id": 11}], "total": 1, "page": 1, "size": 100, "pages": 1}
    validate_association(checkpoint, source, job, batch, provider_file, page)
    page["pages"] = 2
    with pytest.raises(ValueError):
        validate_association(checkpoint, source, job, batch, provider_file, page)


@pytest.mark.parametrize(
    ("record_name", "field", "replacement"),
    [
        ("job", "id", 20),
        ("job", "file_id", True),
        ("job", "batch_job_id", 20),
        ("job", "number_of_shots", 1),
        ("job", "raw_data_enabled", 1),
        ("batch", "id", 20),
        ("batch", "backend_type_id", 1),
        ("batch", "job_ids", [11, 11]),
        ("batch", "job_ids", [True]),
        ("file", "id", 20),
        ("file", "commit_id", 20),
        ("file", "language_id", 9),
        ("file", "compile_properties", {"option": True}),
        ("file", "compile_stage", "compiled"),
        ("file", "content", "version 3.0\r\n"),
        ("result", "job_id", 20),
        ("checkpoint", "source_sha256", "0" * 64),
        ("checkpoint", "job", True),
    ],
)
def test_each_association_edge_refuses_conflict(record_name: str, field: str, replacement: Any) -> None:
    from qi_tuna_source_association import validate_association

    source = b"version 3.0\n"
    records: dict[str, dict[str, Any]] = {
        "checkpoint": {
            "job": 11,
            "file": 12,
            "commit": 13,
            "batch": 14,
            "backend_type": 7,
            "shots": 4096,
            "language_id": 8,
            "result": 21,
            "source_sha256": hashlib.sha256(source).hexdigest(),
        },
        "job": {"id": 11, "file_id": 12, "batch_job_id": 14, "number_of_shots": 4096, "raw_data_enabled": True},
        "batch": {"id": 14, "backend_type_id": 7, "job_ids": [11]},
        "file": {
            "id": 12,
            "commit_id": 13,
            "language_id": 8,
            "compile_stage": "none",
            "compile_properties": {},
            "content": source.decode("utf-8"),
        },
        "result": {"job_id": 11},
    }
    records[record_name][field] = replacement
    result_page = {"items": [records["result"] | {"id": 21}], "total": 1, "page": 1, "size": 100, "pages": 1}
    with pytest.raises(ValueError):
        validate_association(
            records["checkpoint"], source, records["job"], records["batch"], records["file"], result_page
        )


def test_digest_subclass_cannot_accept_a_different_source() -> None:
    from qi_tuna_source_association import validate_association

    class ForgedDigest(str):
        def __ne__(self, other: object) -> bool:
            return False

    source = b"version 3.0\n"
    checkpoint = {
        "job": 11,
        "file": 12,
        "commit": 13,
        "batch": 14,
        "backend_type": 7,
        "shots": 4096,
        "language_id": 8,
        "result": 21,
        "source_sha256": ForgedDigest("wrong"),
    }
    job = {"id": 11, "file_id": 12, "batch_job_id": 14, "number_of_shots": 4096, "raw_data_enabled": True}
    batch = {"id": 14, "backend_type_id": 7, "job_ids": [11]}
    provider_file = {
        "id": 12,
        "commit_id": 13,
        "language_id": 8,
        "compile_stage": "none",
        "compile_properties": {},
        "content": source.decode("utf-8"),
    }
    with pytest.raises(ValueError):
        page = {"items": [{"id": 21, "job_id": 11}], "total": 1, "page": 1, "size": 100, "pages": 1}
        validate_association(checkpoint, source, job, batch, provider_file, page)


@pytest.mark.parametrize(
    "page",
    [
        {"items": [{"id": 21, "job_id": 11}, {"id": 22, "job_id": 11}], "total": 2, "page": 1, "size": 100, "pages": 1},
        {"items": [{"id": 21, "job_id": 11}], "total": 2, "page": 1, "size": 1, "pages": 2},
        {"items": [{"job_id": 11}], "total": 1, "page": 1, "size": 100, "pages": 1},
        {"items": [{"id": True, "job_id": 11}], "total": 1, "page": 1, "size": 100, "pages": 1},
        {"items": [{"id": 22, "job_id": 11}], "total": 1, "page": 1, "size": 100, "pages": 1},
    ],
)
def test_result_page_rejects_duplicate_incomplete_or_misbound_identity(page: dict[str, Any]) -> None:
    from qi_tuna_source_association import validate_result_page

    with pytest.raises(ValueError):
        validate_result_page(page, expected_job_id=11, expected_result_id=21)


def test_result_page_accepts_one_checkpointed_result() -> None:
    from qi_tuna_source_association import validate_result_page

    page = {"items": [{"id": 21, "job_id": 11}], "total": 1, "page": 1, "size": 100, "pages": 1}
    validate_result_page(page, expected_job_id=11, expected_result_id=21)


def test_batch_page_requires_one_matching_complete_page() -> None:
    from qi_tuna_source_association import validate_batch_page

    batch = {"id": 14, "backend_type_id": 7, "job_ids": [11]}
    page = {"items": [batch], "total": 1, "page": 1, "size": 100, "pages": 1}
    validate_batch_page(page, expected_batch_id=14)
    for field, invalid in (("pages", 2), ("total", True), ("items", [batch, batch]), ("size", 101)):
        original = page[field]
        page[field] = invalid
        with pytest.raises(ValueError):
            validate_batch_page(page, expected_batch_id=14)
        page[field] = original
    with pytest.raises(ValueError):
        validate_batch_page(page, expected_batch_id=15)


def test_result_page_rejects_stateful_mapping_subclass() -> None:
    from qi_tuna_source_association import validate_result_page

    class StatefulPage(dict[str, Any]):
        pass

    page = StatefulPage({"items": [{"id": 21, "job_id": 11}], "total": 1, "page": 1, "size": 100, "pages": 1})
    with pytest.raises(ValueError):
        validate_result_page(page, expected_job_id=11, expected_result_id=21)


def test_association_requires_the_complete_result_page() -> None:
    from qi_tuna_source_association import validate_association

    source = b"version 3.0\n"
    checkpoint = {
        "job": 11,
        "file": 12,
        "commit": 13,
        "batch": 14,
        "backend_type": 7,
        "shots": 4096,
        "language_id": 8,
        "result": 21,
        "source_sha256": hashlib.sha256(source).hexdigest(),
    }
    job = {"id": 11, "file_id": 12, "batch_job_id": 14, "number_of_shots": 4096, "raw_data_enabled": True}
    batch = {"id": 14, "backend_type_id": 7, "job_ids": [11]}
    provider_file = {
        "id": 12,
        "commit_id": 13,
        "language_id": 8,
        "compile_stage": "none",
        "compile_properties": {},
        "content": source.decode("utf-8"),
    }
    page = {"items": [{"id": 21, "job_id": 11}], "total": 1, "page": 1, "size": 100, "pages": 1}
    validate_association(checkpoint, source, job, batch, provider_file, page)
