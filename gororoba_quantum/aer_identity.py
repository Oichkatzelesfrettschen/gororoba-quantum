"""Portable identity of the imported native Aer extension and optional CUDA build.

Linux process mappings tie the imported extension to the on-disk device/inode.
Repeated observations additionally reject file, version, or manifest drift.
Other platforms retain the repeated-observation guard and report unavailable
mapping verification. The initial observation cannot reconstruct an in-place
rewrite that predates observation; package replacement on Linux changes the
mapped inode and is rejected even when Aer imports before the identity helper.
The helper constructs zero simulators, services, or primitives.
"""

from __future__ import annotations

import copy
import ctypes
import hashlib
import importlib.machinery
import importlib.metadata
import json
import math
import os
import re
import shlex
import sys
import sysconfig
import threading
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

SCHEMA = "native-aer-identity-v1"
BUILD_SCHEMA = "native-aer-cuda-build-v1"
MANIFEST_NAME = "native_cuda_build.json"
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")


@dataclass(frozen=True)
class _FileStamp:
    device: int
    inode: int
    size: int
    modified_ns: int
    changed_ns: int


@dataclass(frozen=True)
class _Observation:
    record: dict[str, Any]
    extension_path: Path
    extension_stamp: _FileStamp
    manifest_path: Path
    manifest_stamp: _FileStamp | None


_INITIAL: _Observation | None = None
_LOCK = threading.RLock()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _stamp(info: os.stat_result) -> _FileStamp:
    return _FileStamp(info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def _read_stable(path: Path, *, retain_bytes: bool = False) -> tuple[str, _FileStamp, bytes | None]:
    with path.open("rb") as handle:
        before = _stamp(os.fstat(handle.fileno()))
        if retain_bytes:
            _require(before.size <= 1024 * 1024, "native Aer build manifest exceeds one MiB")
            contents = handle.read()
            checksum = hashlib.sha256(contents).hexdigest()
        else:
            contents = None
            checksum = hashlib.file_digest(handle, "sha256").hexdigest()
        after = _stamp(os.fstat(handle.fileno()))
    _require(before == after == _stamp(path.stat()), "native Aer file changes during provenance capture")
    return checksum, before, contents


def _portable(value: Any) -> None:
    """Keep recorded compiler fields and nested manifest values path-free."""
    if value is None or type(value) in (bool, int):
        return
    if isinstance(value, float):
        _require(math.isfinite(value), "native Aer provenance contains a nonfinite number")
        return
    if isinstance(value, str):
        _require("\x00" not in value, "native Aer provenance contains a NUL")
        _require(not re.search(r"[A-Za-z]:[\\/]", value), "native Aer provenance contains an absolute path")
        try:
            tokens = shlex.split(value)
        except ValueError as error:
            raise ValueError("native Aer provenance contains an invalid quoted field") from error
        for token in tokens:
            for fragment in re.split(r"[=,;]", token):
                candidate = fragment.removeprefix("-I").removeprefix("-L").removeprefix("-isystem")
                _require(
                    not PurePosixPath(candidate).is_absolute() and not PureWindowsPath(candidate).is_absolute(),
                    "native Aer provenance contains an absolute path",
                )
        return
    if isinstance(value, list):
        for item in value:
            _portable(item)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            _require(isinstance(key, str), "native Aer provenance keys must be strings")
            _portable(key)
            _portable(item)
        return
    raise ValueError("native Aer provenance contains a non-JSON value")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        _require(key not in result, "native Aer build manifest contains a duplicate key")
        result[key] = value
    return result


def _validate_build(build: dict[str, Any], version: str, abi: str) -> None:
    _portable(build)
    _require(build.get("schema") == BUILD_SCHEMA, "native Aer build schema is unsupported")
    _require(build.get("distribution") == "qiskit-aer", "native Aer build distribution differs")
    _require(build.get("version") == version, "native Aer build version differs from the imported distribution")
    _require(build.get("python_soabi") == abi, "native Aer build ABI differs from the running interpreter")
    _require(build.get("build_mode") == "upstream-aer-thrust-cuda-with-cpu-support", "native Aer build mode differs")
    sources = build.get("source_sha256")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("native Aer build needs source checksums")
    for name, checksum in sources.items():
        _require(
            isinstance(name, str) and PurePosixPath(name).name == name and name not in ("", ".", ".."),
            "native Aer build source identity needs a basename",
        )
        _require(isinstance(checksum, str) and bool(_SHA256.fullmatch(checksum)), "invalid native Aer source checksum")


def validate_contract(record: dict[str, Any]) -> None:
    """Validate a portable saved identity without inspecting installed packages."""
    _portable(record)
    _require(record.get("schema") == SCHEMA, "native Aer identity schema is unsupported")
    _require(record.get("distribution") == "qiskit-aer", "native Aer identity distribution differs")
    version, abi = record.get("version"), record.get("python_soabi")
    if not isinstance(version, str) or not version:
        raise ValueError("native Aer distribution version is missing")
    if not isinstance(abi, str) or not abi:
        raise ValueError("native Aer Python ABI is missing")
    extension = record.get("extension")
    if not isinstance(extension, dict):
        raise ValueError("native Aer extension identity is missing")
    basename, checksum = extension.get("basename"), extension.get("sha256")
    _require(
        isinstance(basename, str)
        and PurePosixPath(basename).name == PureWindowsPath(basename).name == basename
        and basename.startswith("controller_wrappers.")
        and any(basename.endswith(suffix) for suffix in (".so", ".pyd", ".dll", ".dylib")),
        "native Aer extension identity needs its module basename",
    )
    _require(isinstance(checksum, str) and bool(_SHA256.fullmatch(checksum)), "invalid native Aer extension checksum")
    verified, scope = record.get("loaded_mapping_verified"), record.get("loaded_mapping_scope")
    _require(type(verified) is bool, "native Aer mapping verification flag must be Boolean")
    _require(
        scope == ("linux-process-map-device-inode" if verified else "platform-map-check-unavailable"),
        "native Aer mapping scope differs from its verification flag",
    )
    _require("native_cuda_build" in record, "native Aer build manifest presence must be explicit")
    manifest = record["native_cuda_build"]
    if manifest is not None:
        _require(
            isinstance(manifest, dict) and manifest.get("basename") == MANIFEST_NAME, "invalid build manifest name"
        )
        checksum = manifest.get("sha256")
        _require(isinstance(checksum, str) and bool(_SHA256.fullmatch(checksum)), "invalid build manifest checksum")
        build = manifest.get("contract")
        _require(isinstance(build, dict), "native Aer build contract is missing")
        _validate_build(build, version, abi)


def _process_maps() -> str | None:
    if not sys.platform.startswith("linux"):
        return None
    try:
        return Path("/proc/self/maps").read_text()
    except OSError as error:
        raise ValueError("Linux process mappings are unavailable for native Aer provenance") from error


def _verify_mapping(path: Path, stamp: _FileStamp, maps: str | None, label: str = "native Aer extension") -> bool:
    if maps is None:
        return False
    matches = []
    for line in maps.splitlines():
        fields = line.split(maxsplit=5)
        if len(fields) != 6:
            continue
        mapped_path = fields[5].removesuffix(" (deleted)")
        if mapped_path != str(path):
            continue
        _require(not fields[5].endswith(" (deleted)"), f"loaded {label} is deleted or replaced")
        major, minor = fields[3].split(":", 1)
        matches.append((int(major, 16), int(minor, 16), int(fields[4]), fields[1]))
    _require(bool(matches) and any("x" in row[3] for row in matches), f"loaded {label} mapping is absent")
    _require(
        all(
            (major, minor, inode) == (os.major(stamp.device), os.minor(stamp.device), stamp.inode)
            for major, minor, inode, _permissions in matches
        ),
        f"loaded {label} differs from the on-disk package; restart the process",
    )
    return True


def _optional_stamp(path: Path) -> _FileStamp | None:
    try:
        return _stamp(path.stat())
    except FileNotFoundError:
        return None


def _capture(
    extension: Path,
    manifest_path: Path,
    version: str,
    abi: str,
    maps: Callable[[], str | None],
) -> _Observation:
    checksum, extension_stamp, _contents = _read_stable(extension)
    verified = _verify_mapping(extension, extension_stamp, maps())
    manifest, manifest_stamp = None, None
    if manifest_path.exists():
        manifest_checksum, manifest_stamp, contents = _read_stable(manifest_path, retain_bytes=True)
        assert contents is not None
        try:
            build = json.loads(contents, object_pairs_hook=_unique_object)
        except (UnicodeError, json.JSONDecodeError) as error:
            raise ValueError("native Aer build manifest is invalid JSON") from error
        if not isinstance(build, dict):
            raise ValueError("native Aer build manifest must be a JSON object")
        manifest = {"basename": manifest_path.name, "sha256": manifest_checksum, "contract": build}
    _require(verified == _verify_mapping(extension, extension_stamp, maps()), "native Aer mapping verification changes")
    record = {
        "schema": SCHEMA,
        "distribution": "qiskit-aer",
        "version": version,
        "python_soabi": abi,
        "extension": {"basename": extension.name, "sha256": checksum},
        "native_cuda_build": manifest,
        "loaded_mapping_verified": verified,
        "loaded_mapping_scope": "linux-process-map-device-inode" if verified else "platform-map-check-unavailable",
    }
    validate_contract(record)
    _require(extension_stamp == _stamp(extension.stat()), "native Aer extension changes during manifest capture")
    _require(manifest_stamp == _optional_stamp(manifest_path), "native Aer build manifest changes during capture")
    return _Observation(record, extension, extension_stamp, manifest_path, manifest_stamp)


def _capture_current() -> _Observation:
    import qiskit_aer
    from qiskit_aer.backends import controller_wrappers

    module_path = Path(controller_wrappers.__file__).resolve(strict=True)
    package_root = Path(qiskit_aer.__file__).resolve(strict=True).parent
    _require(module_path.parent.parent == package_root, "native Aer module resolves outside its imported package")
    specification = controller_wrappers.__spec__
    _require(
        specification is not None
        and isinstance(specification.loader, importlib.machinery.ExtensionFileLoader)
        and specification.origin is not None
        and Path(specification.origin).resolve(strict=True) == module_path,
        "native Aer controller has an unexpected loader or module origin",
    )
    distribution = importlib.metadata.distribution("qiskit-aer")
    _require(
        Path(str(distribution.locate_file("qiskit_aer"))).resolve(strict=True) == package_root,
        "native Aer distribution metadata resolves outside the imported package",
    )
    _require(distribution.version == qiskit_aer.__version__, "native Aer loaded and installed versions differ")
    abi = sysconfig.get_config_var("SOABI")
    _require(isinstance(abi, str) and bool(abi), "native Aer Python ABI is unavailable")
    return _capture(module_path, package_root / MANIFEST_NAME, distribution.version, abi, _process_maps)


def _check_unchanged(before: _Observation, after: _Observation) -> None:
    _require(before == after, "native Aer provenance changes during the active process; start a fresh process")


def identity() -> dict[str, Any]:
    """Observe actual imported Aer and reject drift from the first observation."""
    global _INITIAL
    with _LOCK:
        # A full capture hashes the native extension and reads the process
        # map; once the first capture exists, unchanged stat stamps (device,
        # inode, size, mtime, ctime) on the extension and manifest establish
        # the same bytes, and any stamp change reruns the full capture.
        if _INITIAL is not None:
            try:
                unchanged = (
                    _stamp(_INITIAL.extension_path.stat()) == _INITIAL.extension_stamp
                    and _optional_stamp(_INITIAL.manifest_path) == _INITIAL.manifest_stamp
                )
            except OSError:
                unchanged = False
            if unchanged:
                return copy.deepcopy(_INITIAL.record)
        try:
            observation = _capture_current()
        except (OSError, ImportError, importlib.metadata.PackageNotFoundError) as error:
            raise ValueError("native Aer provenance inputs are unavailable") from error
        if _INITIAL is None:
            _INITIAL = observation
        else:
            _check_unchanged(_INITIAL, observation)
        return copy.deepcopy(observation.record)


def require_current(expected: dict[str, Any]) -> None:
    """Bind a valid saved identity to the imported extension in the active process."""
    validate_contract(expected)
    _require(expected == identity(), "native Aer identity differs from the saved execution contract")


class _DlInfo(ctypes.Structure):
    _fields_ = [
        ("filename", ctypes.c_char_p),
        ("base", ctypes.c_void_p),
        ("symbol_name", ctypes.c_char_p),
        ("symbol_address", ctypes.c_void_p),
    ]


class _CudaUuid(ctypes.Structure):
    _fields_ = [("bytes", ctypes.c_ubyte * 16)]


@dataclass(frozen=True)
class _GpuObservation:
    record: dict[str, Any]
    libraries: tuple[tuple[str, Path, _FileStamp], ...]


_GPU_INITIAL: _GpuObservation | None = None
_GPU_HANDLES: tuple[ctypes.CDLL, ctypes.CDLL] | None = None
_GPU_FILE_CACHE: dict[Path, tuple[_FileStamp, str]] = {}
GPU_SCHEMA = "native-aer-cuda-runtime-identity-v1"


def _loaded_symbol_path(function: Any) -> Path:
    """Resolve the library that supplies an already loaded native API symbol."""
    loader = ctypes.CDLL(None)
    loader.dladdr.argtypes = [ctypes.c_void_p, ctypes.POINTER(_DlInfo)]
    loader.dladdr.restype = ctypes.c_int
    info = _DlInfo()
    found = loader.dladdr(ctypes.cast(function, ctypes.c_void_p), ctypes.byref(info))
    _require(bool(found) and info.filename is not None, "CUDA symbol has no loaded library identity")
    assert info.filename is not None
    return Path(os.fsdecode(info.filename)).resolve(strict=True)


def _cuda_check(status: int, operation: str) -> None:
    _require(status == 0, f"native CUDA {operation} fails with status {status}")


def _gpu_device_identity(runtime: ctypes.CDLL, driver: ctypes.CDLL) -> dict[str, Any]:
    """Query native API versions and bind both APIs to logical CUDA device zero."""
    driver.cuInit.argtypes = [ctypes.c_uint]
    driver.cuInit.restype = ctypes.c_int
    _cuda_check(driver.cuInit(0), "cuInit")
    device_counts = []
    for library, operation in ((runtime, "cudaGetDeviceCount"), (driver, "cuDeviceGetCount")):
        function = getattr(library, operation)
        function.argtypes = [ctypes.POINTER(ctypes.c_int)]
        function.restype = ctypes.c_int
        count = ctypes.c_int()
        _cuda_check(function(ctypes.byref(count)), operation)
        _require(count.value > 0, "native CUDA reports zero available devices")
        device_counts.append(count.value)
    _require(device_counts[0] == device_counts[1], "CUDA runtime and driver device counts differ")
    driver.cuDeviceGet.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int]
    driver.cuDeviceGet.restype = ctypes.c_int
    device = ctypes.c_int()
    _cuda_check(driver.cuDeviceGet(ctypes.byref(device), 0), "cuDeviceGet(0)")
    uuid_api = "cuDeviceGetUuid_v2" if hasattr(driver, "cuDeviceGetUuid_v2") else "cuDeviceGetUuid"
    uuid_function = getattr(driver, uuid_api)
    uuid_function.argtypes = [ctypes.POINTER(_CudaUuid), ctypes.c_int]
    uuid_function.restype = ctypes.c_int
    uuid = _CudaUuid()
    _cuda_check(uuid_function(ctypes.byref(uuid), device), uuid_api)
    _require(any(uuid.bytes), "CUDA driver returns an empty device UUID")
    # Both documented PCI queries describe domain:bus:device.function. Comparing
    # them binds runtime ordinal zero to the driver ordinal whose UUID is hashed.
    buses = []
    for library, name, ordinal in (
        (runtime, "cudaDeviceGetPCIBusId", 0),
        (driver, "cuDeviceGetPCIBusId", device.value),
    ):
        function = getattr(library, name)
        function.argtypes = [ctypes.POINTER(ctypes.c_char), ctypes.c_int, ctypes.c_int]
        function.restype = ctypes.c_int
        buffer = ctypes.create_string_buffer(32)
        _cuda_check(function(buffer, len(buffer), ordinal), name)
        bus = buffer.value.decode("ascii").lower()
        _require(
            bool(re.fullmatch(r"[0-9a-f]{4,8}:[0-9a-f]{2}:[0-9a-f]{2}\.[0-7]", bus)), "CUDA PCI identity is invalid"
        )
        buses.append(tuple(int(field, 16) for field in re.split(r"[:.]", bus)))
    _require(buses[0] == buses[1], "CUDA runtime and driver device zero differ")
    record: dict[str, Any] = {
        "device_count": device_counts[0],
        "device_ordinal": 0,
        "device_uuid_sha256": hashlib.sha256(bytes(uuid.bytes)).hexdigest(),
        "device_uuid_api": uuid_api,
        "runtime_driver_device_match": "pci-domain-bus-device-function",
    }
    for library, operation, key in (
        (runtime, "cudaRuntimeGetVersion", "runtime_version"),
        (driver, "cuDriverGetVersion", "driver_version"),
    ):
        function = getattr(library, operation)
        function.argtypes = [ctypes.POINTER(ctypes.c_int)]
        function.restype = ctypes.c_int
        version = ctypes.c_int()
        _cuda_check(function(ctypes.byref(version)), operation)
        _require(version.value > 0, "CUDA version query returns an invalid version")
        record[key] = version.value
    return record


def _kernel_identity(contents: bytes) -> dict[str, str]:
    text = contents.decode("utf-8")
    match = re.search(r"^NVRM version:.*?\s([0-9]+(?:\.[0-9]+){1,3})\s", text, flags=re.MULTILINE)
    _require(match is not None, "loaded NVIDIA kernel version is unavailable")
    assert match is not None
    return {"version": match.group(1), "version_text_sha256": hashlib.sha256(contents).hexdigest()}


def validate_gpu_contract(record: dict[str, Any]) -> None:
    """Validate the enumerated CUDA identity without loading CUDA or a simulator."""
    _portable(record)
    _require(record.get("schema") == GPU_SCHEMA, "native CUDA identity schema is unsupported")
    _require(
        type(record.get("device_ordinal")) is int and record["device_ordinal"] == 0,
        "CUDA identity requires device zero",
    )
    _require(record.get("device_uuid_api") in ("cuDeviceGetUuid", "cuDeviceGetUuid_v2"), "CUDA UUID API is unsupported")
    _require(
        record.get("runtime_driver_device_match") == "pci-domain-bus-device-function",
        "CUDA device agreement is missing",
    )
    checksum = record.get("device_uuid_sha256")
    _require(isinstance(checksum, str) and bool(_SHA256.fullmatch(checksum)), "CUDA device UUID digest is invalid")
    for key in ("runtime_version", "driver_version", "device_count"):
        _require(type(record.get(key)) is int and record[key] > 0, f"CUDA {key} is invalid")
    libraries = record.get("libraries")
    if not isinstance(libraries, dict) or set(libraries) != {"cuda_runtime", "cuda_driver"}:
        raise ValueError("CUDA identity requires the runtime and driver libraries")
    for key, prefix in (("cuda_runtime", "libcudart.so"), ("cuda_driver", "libcuda.so")):
        library = libraries[key]
        if not isinstance(library, dict):
            raise ValueError("CUDA library identity is invalid")
        basename = library.get("basename")
        _require(
            isinstance(basename, str)
            and basename.startswith(prefix)
            and PurePosixPath(basename).name == PureWindowsPath(basename).name == basename,
            "CUDA library identity needs its native basename",
        )
        checksum = library.get("sha256")
        _require(isinstance(checksum, str) and bool(_SHA256.fullmatch(checksum)), "CUDA library checksum is invalid")
        _require(library.get("loaded_mapping_verified") is True, "CUDA library mapping requires Linux verification")
    kernel = record.get("nvidia_kernel")
    if not isinstance(kernel, dict):
        raise ValueError("NVIDIA kernel identity is missing")
    version, checksum = kernel.get("version"), kernel.get("version_text_sha256")
    _require(
        isinstance(version, str) and bool(re.fullmatch(r"[0-9]+(?:\.[0-9]+){1,3}", version)),
        "NVIDIA kernel version is invalid",
    )
    _require(isinstance(checksum, str) and bool(_SHA256.fullmatch(checksum)), "NVIDIA kernel version digest is invalid")
    _require(
        record.get("scope") == "logical-device-zero-libcudart-libcuda-loaded-nvidia-kernel",
        "CUDA identity scope differs",
    )


def _capture_gpu(
    paths: dict[str, Path],
    device: Callable[[], dict[str, Any]],
    kernel: Callable[[], bytes],
    maps: Callable[[], str | None],
    cache: dict[Path, tuple[_FileStamp, str]],
) -> _GpuObservation:
    device_record = device()
    kernel_bytes = kernel()
    libraries = {}
    observations = []
    for name, path in sorted(paths.items()):
        stamp = _stamp(path.stat())
        _require(_verify_mapping(path, stamp, maps(), name), "CUDA identity requires Linux process mappings")
        if path in cache:
            prior_stamp, checksum = cache[path]
            _require(prior_stamp == stamp, "loaded CUDA library changes during the active process; restart")
        else:
            checksum, hashed_stamp, _contents = _read_stable(path)
            _require(hashed_stamp == stamp, "CUDA library changes during its first identity capture")
            cache[path] = (stamp, checksum)
        libraries[name] = {"basename": path.name, "sha256": checksum, "loaded_mapping_verified": True}
        observations.append((name, path, stamp))
    record = {
        "schema": GPU_SCHEMA,
        **device_record,
        "libraries": libraries,
        "nvidia_kernel": _kernel_identity(kernel_bytes),
        "scope": "logical-device-zero-libcudart-libcuda-loaded-nvidia-kernel",
    }
    validate_gpu_contract(record)
    _require(device_record == device(), "CUDA device identity changes during capture")
    _require(kernel_bytes == kernel(), "loaded NVIDIA kernel identity changes during capture")
    for name, path, stamp in observations:
        _require(_verify_mapping(path, stamp, maps(), name), "CUDA library mapping disappears during capture")
        _require(stamp == _stamp(path.stat()), "CUDA library changes during capture")
    return _GpuObservation(record, tuple(observations))


def gpu_runtime_identity() -> dict[str, Any]:
    """Bind GPU telemetry libraries and device zero without simulating a circuit.

    The optional entrypoint requires Linux CUDA and never substitutes a CPU
    result. The identity covers libcudart, libcuda and the loaded NVIDIA kernel
    version, not the complete linked-library closure. Aer extension identity
    separately covers any runtime statically linked into the extension.
    """
    global _GPU_INITIAL, _GPU_HANDLES
    with _LOCK:
        _require(sys.platform.startswith("linux"), "native CUDA identity requires Linux mappings and kernel metadata")
        try:
            if _GPU_HANDLES is None:
                _GPU_HANDLES = (ctypes.CDLL("libcudart.so"), ctypes.CDLL("libcuda.so.1"))
            runtime, driver = _GPU_HANDLES
            paths = {
                "cuda_runtime": _loaded_symbol_path(runtime.cudaRuntimeGetVersion),
                "cuda_driver": _loaded_symbol_path(driver.cuInit),
            }
            cache = dict(_GPU_FILE_CACHE)
            observation = _capture_gpu(
                paths,
                partial(_gpu_device_identity, runtime, driver),
                Path("/proc/driver/nvidia/version").read_bytes,
                _process_maps,
                cache,
            )
        except (OSError, AttributeError, UnicodeError) as error:
            raise ValueError("native CUDA provenance inputs or APIs are unavailable") from error
        if _GPU_INITIAL is not None:
            _require(_GPU_INITIAL == observation, "native CUDA identity changes during the active process; restart")
        else:
            _GPU_INITIAL = observation
        _GPU_FILE_CACHE.update(cache)
        return copy.deepcopy(observation.record)


def _verify_gpu_fixtures() -> None:
    import tempfile
    from unittest.mock import patch

    def rejects(action: Callable[[], Any], label: str) -> None:
        try:
            action()
        except ValueError:
            return
        raise AssertionError(f"native CUDA identity accepts {label}")

    with tempfile.TemporaryDirectory(prefix="cuda-identity-check-") as temporary:
        directory = Path(temporary)
        paths = {"cuda_runtime": directory / "libcudart.so.13", "cuda_driver": directory / "libcuda.so.1"}
        for name, path in paths.items():
            path.write_bytes(name.encode())
        device_record = {
            "device_count": 1,
            "device_ordinal": 0,
            "device_uuid_sha256": hashlib.sha256(b"fixture-device-uuid").hexdigest(),
            "device_uuid_api": "cuDeviceGetUuid_v2",
            "runtime_driver_device_match": "pci-domain-bus-device-function",
            "runtime_version": 13040,
            "driver_version": 13040,
        }
        kernel_bytes = b"NVRM version: NVIDIA UNIX Open Kernel Module for x86_64 615.71.09 Release Build\n"

        def device() -> dict[str, Any]:
            return dict(device_record)

        def kernel() -> bytes:
            return kernel_bytes

        def mappings() -> str:
            return "\n".join(
                f"1000-2000 r-xp 0 {os.major(info.st_dev):x}:{os.minor(info.st_dev):x} {info.st_ino} {path}"
                for path in paths.values()
                for info in [path.stat()]
            )

        cache: dict[Path, tuple[_FileStamp, str]] = {}
        with patch.object(sys.modules[__name__], "_read_stable", wraps=_read_stable) as reader:
            baseline = _capture_gpu(paths, device, kernel, mappings, cache)
            assert reader.call_count == 2
            assert baseline == _capture_gpu(paths, device, kernel, mappings, cache)
            assert reader.call_count == 2
        assert str(directory) not in json.dumps(baseline.record)
        assert baseline.record["nvidia_kernel"]["version"] == "615.71.09"
        assert baseline.record["libraries"]["cuda_driver"]["sha256"] == hashlib.sha256(b"cuda_driver").hexdigest()
        for field, invalid in (
            ("schema", "unknown"),
            ("device_count", 0),
            ("device_count", True),
            ("device_ordinal", True),
            ("device_ordinal", 1),
            ("device_uuid_sha256", "broken"),
            ("runtime_version", 0),
            ("device_uuid_api", "invented"),
            ("libraries", {}),
            ("nvidia_kernel", None),
            ("scope", "all-linked-libraries"),
            ("private_path", "/private/cuda/library.so"),
        ):
            rejects(partial(validate_gpu_contract, baseline.record | {field: invalid}), field)
        broken_library = copy.deepcopy(baseline.record)
        broken_library["libraries"]["cuda_driver"]["loaded_mapping_verified"] = False
        rejects(partial(validate_gpu_contract, broken_library), "an unverified loaded CUDA library")
        for contents in (b"", b"NVRM version: missing version\n"):
            rejects(partial(_kernel_identity, contents), "an unavailable loaded NVIDIA kernel version")
        changed_devices = iter((device(), device_record | {"device_uuid_sha256": "0" * 64}))
        rejects(
            partial(_capture_gpu, paths, partial(next, changed_devices), kernel, mappings, cache), "a changing device"
        )
        changed_kernels = iter((kernel_bytes, kernel_bytes.replace(b"615.71.09", b"616.00.00")))
        rejects(
            partial(_capture_gpu, paths, device, partial(next, changed_kernels), mappings, cache), "a changing kernel"
        )
        for maps in (lambda: None, lambda: ""):
            rejects(partial(_capture_gpu, paths, device, kernel, maps, cache), "missing process mappings")
        old_mappings = mappings()
        driver_path = paths["cuda_driver"]
        replacement = directory / "replacement.so"
        replacement.write_bytes(driver_path.read_bytes())
        replacement.replace(driver_path)
        rejects(
            partial(_capture_gpu, paths, device, kernel, partial(str, old_mappings), cache), "a replaced mapped driver"
        )
        rejects(partial(_capture_gpu, paths, device, kernel, mappings, cache), "replacement by identical driver bytes")
        fresh_cache: dict[Path, tuple[_FileStamp, str]] = {}
        _capture_gpu(paths, device, kernel, mappings, fresh_cache)
        driver_path.write_bytes(b"changed-cuda-driver")
        rejects(partial(_capture_gpu, paths, device, kernel, mappings, fresh_cache), "in-place driver mutation")
        module = sys.modules[__name__]
        with (
            patch.object(sys, "platform", "linux"),
            patch.object(module, "_GPU_INITIAL", None),
            patch.object(module, "_GPU_HANDLES", None),
            patch.object(module, "_GPU_FILE_CACHE", {}),
            patch.object(ctypes, "CDLL", side_effect=OSError("unavailable")),
            patch.object(module, "identity", side_effect=AssertionError("GPU failure retries CPU")),
        ):
            rejects(gpu_runtime_identity, "an unavailable CUDA library")
        changed_observation = _GpuObservation(baseline.record | {"device_uuid_sha256": "0" * 64}, baseline.libraries)
        with (
            patch.object(sys, "platform", "linux"),
            patch.object(module, "_GPU_INITIAL", None),
            patch.object(module, "_GPU_HANDLES", None),
            patch.object(module, "_GPU_FILE_CACHE", {}),
            patch.object(ctypes, "CDLL"),
            patch.object(module, "_loaded_symbol_path", return_value=driver_path),
            patch.object(module, "_capture_gpu", side_effect=(baseline, baseline, baseline, changed_observation)),
        ):
            first = gpu_runtime_identity()
            first["libraries"]["cuda_driver"]["sha256"] = "0" * 64
            assert first != gpu_runtime_identity()
            assert gpu_runtime_identity() == baseline.record
            rejects(gpu_runtime_identity, "a changed active GPU identity")
    print("native CUDA identity: cached library hashes, device/kernel drift, unavailable APIs, and privacy checks pass")


def _verify() -> None:
    import tempfile

    actual = identity()
    require_current(actual)
    actual["extension"]["sha256"] = "0" * 64
    _require(actual != identity(), "returned native Aer identity aliases the process observation")
    try:
        require_current(actual)
    except ValueError:
        pass
    else:
        raise AssertionError("native Aer accepts a mismatched saved binary digest")
    with tempfile.TemporaryDirectory(prefix="aer-identity-check-") as temporary:
        directory = Path(temporary)
        extension = directory / "controller_wrappers.fixture.so"
        extension.write_bytes(b"native-extension-fixture")
        manifest_path = directory / MANIFEST_NAME
        abi, version = "cpython-314-fixture", "0.17.2"

        def mappings() -> str:
            stat = extension.stat()
            return f"1000-2000 r-xp 0 {os.major(stat.st_dev):x}:{os.minor(stat.st_dev):x} {stat.st_ino} {extension}"

        baseline = _capture(extension, manifest_path, version, abi, mappings)
        _require(baseline.record["native_cuda_build"] is None, "CPU identity requires an absent manifest")
        _require(baseline.record["loaded_mapping_verified"], "mapped fixture lacks verification")
        unmapped = _capture(extension, manifest_path, version, abi, lambda: None)
        _require(not unmapped.record["loaded_mapping_verified"], "unavailable mapping fabricates verification")
        old_mapping = mappings()
        replacement = directory / "replacement.so"
        replacement.write_bytes(extension.read_bytes())
        replacement.replace(extension)
        for invalid_maps in (old_mapping, old_mapping + " (deleted)", ""):
            try:
                _capture(extension, manifest_path, version, abi, partial(str, invalid_maps))
            except ValueError:
                pass
            else:
                raise AssertionError("native Aer accepts a replaced, deleted, or absent mapped extension")
        identical_replacement = _capture(extension, manifest_path, version, abi, mappings)
        try:
            _check_unchanged(baseline, identical_replacement)
        except ValueError:
            pass
        else:
            raise AssertionError("native Aer accepts replacement by identical bytes during an active process")
        extension.write_bytes(b"changed-native-extension")
        modified = _capture(extension, manifest_path, version, abi, mappings)
        try:
            _check_unchanged(identical_replacement, modified)
        except ValueError:
            pass
        else:
            raise AssertionError("native Aer accepts an in-place extension rewrite")
        build = {
            "schema": BUILD_SCHEMA,
            "distribution": "qiskit-aer",
            "version": version,
            "python_soabi": abi,
            "build_mode": "upstream-aer-thrust-cuda-with-cpu-support",
            "source_sha256": {"upstream.tar.gz": "1" * 64},
        }
        manifest_path.write_text(json.dumps(build))
        native = _capture(extension, manifest_path, version, abi, mappings)
        _require(native.record["native_cuda_build"]["contract"] == build, "build contract parsing loses fields")
        _require(
            native.record["native_cuda_build"]["sha256"] == hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
            "build manifest checksum differs from retained bytes",
        )
        for key, bad in (
            ("version", "0.0.0"),
            ("python_soabi", "wrong-abi"),
            ("schema", "unknown"),
            ("compiler_flags", "-I/private/build/include"),
            ("compiler_flags", "-ffile-prefix-map=/private/build=relative"),
            ("compiler_flags", "C:\\private\\build"),
        ):
            manifest_path.write_text(json.dumps(build | {key: bad}))
            try:
                _capture(extension, manifest_path, version, abi, mappings)
            except ValueError:
                pass
            else:
                raise AssertionError(f"native Aer accepts invalid build field {key}")
        manifest_path.write_text('{"schema":"first","schema":"second"}')
        try:
            _capture(extension, manifest_path, version, abi, mappings)
        except ValueError:
            pass
        else:
            raise AssertionError("native Aer accepts duplicate manifest keys")
        manifest_path.write_text(json.dumps(build | {"compile_jobs": 2}))
        changed_manifest = _capture(extension, manifest_path, version, abi, mappings)
        try:
            _check_unchanged(native, changed_manifest)
        except ValueError:
            pass
        else:
            raise AssertionError("native Aer accepts a changed build manifest")
        manifest_path.unlink()
        removed_manifest = _capture(extension, manifest_path, version, abi, mappings)
        try:
            _check_unchanged(native, removed_manifest)
        except ValueError:
            pass
        else:
            raise AssertionError("native Aer accepts a removed build manifest")
        for transition in ("appears", "changes", "disappears"):
            if transition == "appears":
                manifest_path.unlink(missing_ok=True)
            else:
                manifest_path.write_text(json.dumps(build))
            mapping_reads = 0

            def changing_mappings(change: str = transition) -> str:
                nonlocal mapping_reads
                mapping_reads += 1
                if mapping_reads == 2:
                    if change == "disappears":
                        manifest_path.unlink()
                    else:
                        manifest_path.write_text(json.dumps(build | {"compile_jobs": 3}))
                return mappings()

            try:
                _capture(extension, manifest_path, version, abi, changing_mappings)
            except ValueError:
                pass
            else:
                raise AssertionError(f"native Aer accepts a build manifest that {transition} during capture")
        _require(str(directory) not in json.dumps(native.record), "native Aer identity exposes a local path")
    _verify_gpu_fixtures()
    print("native Aer identity: imported binary, optional build contract, mapping drift, and mutation checks pass")


if __name__ == "__main__":
    _verify()
