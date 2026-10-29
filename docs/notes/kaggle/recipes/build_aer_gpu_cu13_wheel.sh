#!/bin/sh
# Builds qiskit-aer 0.18.2 as a cp313 CUDA 13 wheel (qiskit-aer-gpu-cu13)
# for the Kaggle T4 image and checks it in a CUDA-free Ubuntu 24.04 container.
#
# The module carries SASS for sm_75 (Tesla T4) and sm_89 (Ada), links
# cuStateVec and cuTensorNet, and resolves every CUDA library through DT_RPATH
# entries relative to site-packages, where the pinned CUDA 13 pip wheels of
# aer-gpu-cu13-runtime-pins.txt install them.
#
# Usage: build_aer_gpu_cu13_wheel.sh [STEP...]
#   fetch       download and verify the source archives
#   images      build the build and test images from aer-gpu-cu13.Containerfile
#   build       compile, auditwheel-repair, and write dist/ and logs/
#   check       acceptance checks on the repaired wheel (no GPU needed)
#   gpu-check   seeded Bell runs on the host GPU through CDI (nvidia.com/gpu=all)
#   clean       remove the two built images and the pulled base images
# With no STEP it runs fetch images build check.
#
# Environment: AER_CU13_WORK (default
# ${XDG_CACHE_HOME:-$HOME/.cache}/gororoba-quantum/aer-gpu-cu13),
# AER_BUILD_JOBS (default 6), PODMAN (default podman). The work tree holds
# the sources, venvs, uv cache and wheel, several GB of Python packages, and
# lives outside every checkout so the checkout's tree walks never read it.
# Every checkout shares it, so one host run at a time holds WORK/.lock (a
# second run exits 75). images labels both images with the digest of the
# recipe inputs, build and check refuse an image whose label differs, and
# build records the digest and the image ids in WORK/producer.txt; check and
# gpu-check refuse a wheel whose digest differs from the running recipe's.
set -eu

RECIPE_DIR=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH='' cd -- "$RECIPE_DIR/../../../.." && pwd)
WORK=${AER_CU13_WORK:-${XDG_CACHE_HOME:-$HOME/.cache}/gororoba-quantum/aer-gpu-cu13}
JOBS=${AER_BUILD_JOBS:-6}
PODMAN=${PODMAN:-podman}

BUILD_BASE=docker.io/nvidia/cuda:13.0.3-devel-ubuntu24.04@sha256:7d56ebe2b7cd864a60dca3c8b2d0a39f8fc110417e8253e32505c3387f59119c
TEST_BASE=docker.io/library/ubuntu:noble-20260917@sha256:f610ab94648195aa356059f5b41d6085c9d4d903c072430cdd1af7bdb646106b
BUILD_TAG=localhost/aer-gpu-cu13-build:0.18.2
TEST_TAG=localhost/aer-gpu-cu13-test:0.18.2

AER_VERSION=0.18.2
AER_URL=https://github.com/Qiskit/qiskit-aer/archive/$AER_VERSION.tar.gz
AER_SHA256=ab4fa46a70836bff24e95078b10dc316e2c36d85a029de2f5817de41ed746810
JSON_VERSION=3.10.2
JSON_URL=https://github.com/nlohmann/json/archive/refs/tags/v$JSON_VERSION.tar.gz
JSON_SHA256=081ed0f9f89805c2d96335c3acfa993b39a0a5b4b4cef7edb68dd2210a13458c

# CUDA libraries the module excludes from auditwheel grafting; the pip wheels
# of aer-gpu-cu13-runtime-pins.txt supply them at run time.
CUDA_EXCLUDES="libcudart.so.13 libcublas.so.13 libcublasLt.so.13 libcusolver.so.12
libcusolverMg.so.12 libcusparse.so.12 libnvJitLink.so.13 libcustatevec.so.1
libcutensornet.so.2 libcutensor.so.2 libcutensorMg.so.2 libcuda.so.1"

log() { printf '%s\n' "$*" >&2; }

# recipe_digest: one sha256 over every input a build reads from the checkout.
recipe_digest() {
	{
		(cd "$RECIPE_DIR" && sha256sum build_aer_gpu_cu13_wheel.sh aer-gpu-cu13.Containerfile \
			aer-cu13-pip-layout.patch aer-gpu-cu13-build-pins.txt aer-gpu-cu13-runtime-pins.txt)
		(cd "$REPO_ROOT" && sha256sum requirements.txt docs/notes/build_host/recipes/aer-cccl3-unary-function.patch)
	} | sha256sum | cut -d' ' -f1
}

# require_images: both tagged images carry the running recipe's digest, so
# a step never runs an image a changed Containerfile or base no longer makes.
require_images() {
	want=$(recipe_digest)
	for tag in "$BUILD_TAG" "$TEST_TAG"; do
		label=$("$PODMAN" image inspect --format '{{index .Labels "gororoba.recipe"}}' "$tag" 2>/dev/null || true)
		if [ "$label" != "$want" ]; then
			log "$tag was built by recipe ${label:-unknown}, not $want; run images first"
			exit 1
		fi
	done
}

require_producer() {
	require_images
	want=$(recipe_digest)
	have=$(sed -n 's/^recipe //p' "$WORK/producer.txt" 2>/dev/null || true)
	if [ "$have" != "$want" ]; then
		log "$WORK holds a wheel built by recipe ${have:-unknown}, not $want; run build first"
		exit 1
	fi
}

# container_run IMAGE DEVICE STEP: run this script's STEP inside IMAGE; DEVICE
# is a CDI device name or empty. One bind mount holds the uv cache and both
# venvs, so uv hardlinks the multi-hundred-megabyte CUDA wheels instead of
# copying them.
container_run() {
	image=$1
	device=$2
	inner=$3
	set -- --rm \
		-v "$WORK:/work" \
		-v "$RECIPE_DIR:/recipe:ro" \
		-v "$REPO_ROOT/docs/notes/build_host/recipes:/host-recipe:ro" \
		-v "$REPO_ROOT/requirements.txt:/recipe-requirements.txt:ro" \
		-e UV_CACHE_DIR=/work/uv-cache -e UV_LINK_MODE=hardlink \
		-e AER_BUILD_JOBS="$JOBS"
	if [ -n "$device" ]; then
		set -- "$@" --device "$device"
	fi
	nice -n 19 "$PODMAN" run "$@" "$image" sh /recipe/build_aer_gpu_cu13_wheel.sh "$inner"
}

step_fetch() {
	mkdir -p "$WORK/sources"
	for spec in "qiskit-aer-$AER_VERSION.tar.gz $AER_URL $AER_SHA256" \
		"nlohmann-json-$JSON_VERSION.tar.gz $JSON_URL $JSON_SHA256"; do
		# shellcheck disable=SC2086
		set -- $spec
		if [ ! -f "$WORK/sources/$1" ]; then
			log "fetch $2"
			curl -fsSL -o "$WORK/sources/$1.part" "$2"
			mv "$WORK/sources/$1.part" "$WORK/sources/$1"
		fi
		printf '%s  %s\n' "$3" "$WORK/sources/$1" | sha256sum -c --quiet -
	done
}

step_images() {
	mkdir -p "$WORK/logs"
	digest=$(recipe_digest)
	nice -n 19 "$PODMAN" build --target build -t "$BUILD_TAG" --label "gororoba.recipe=$digest" \
		--build-arg BUILD_BASE="$BUILD_BASE" --build-arg TEST_BASE="$TEST_BASE" \
		-f "$RECIPE_DIR/aer-gpu-cu13.Containerfile" "$RECIPE_DIR" >"$WORK/logs/image-build.log" 2>&1
	nice -n 19 "$PODMAN" build --target test -t "$TEST_TAG" --label "gororoba.recipe=$digest" \
		--build-arg BUILD_BASE="$BUILD_BASE" --build-arg TEST_BASE="$TEST_BASE" \
		-f "$RECIPE_DIR/aer-gpu-cu13.Containerfile" "$RECIPE_DIR" >"$WORK/logs/image-test.log" 2>&1
	"$PODMAN" image inspect --format '{{.Id}} {{.RepoTags}}' "$BUILD_TAG" "$TEST_TAG" >"$WORK/logs/images.txt"
}

step_build() {
	require_images
	for stale in "$WORK/src" "$WORK/venv-build" "$WORK/dist" "$WORK/producer.txt"; do
		if [ -e "$stale" ]; then
			log "trash $stale"
			trash-put "$stale"
		fi
	done
	mkdir -p "$WORK/logs"
	container_run "$BUILD_TAG" '' inner-build >"$WORK/logs/build.log" 2>&1
	revision=$(git -C "$REPO_ROOT" rev-parse HEAD 2>/dev/null || echo unknown)
	images=$("$PODMAN" image inspect --format '{{.Id}}' "$BUILD_TAG" "$TEST_TAG" | tr '\n' ' ')
	printf 'recipe %s\nrevision %s\nimages %s\n' "$(recipe_digest)" "$revision" "${images% }" >"$WORK/producer.txt"
}

step_check() {
	require_producer
	if [ -e "$WORK/venv-test" ]; then
		trash-put "$WORK/venv-test"
	fi
	container_run "$BUILD_TAG" '' inner-elf-check >"$WORK/logs/elf-check.log" 2>&1
	container_run "$TEST_TAG" '' inner-import-check >"$WORK/logs/import-check.log" 2>&1
	container_run "$BUILD_TAG" '' inner-shadow-check >"$WORK/logs/shadow-check.log" 2>&1
}

step_gpu_check() {
	require_producer
	container_run "$TEST_TAG" nvidia.com/gpu=all inner-gpu-check >"$WORK/logs/gpu-check.log" 2>&1
}

step_clean() {
	# Removing a tagged image also removes the untagged build-cache parents
	# that only it references. The bases were pulled by digest and carry no
	# tag, so they are removed by repository@digest.
	"$PODMAN" rmi "$BUILD_TAG" "$TEST_TAG"
	"$PODMAN" rmi "${BUILD_BASE%%:*}@${BUILD_BASE#*@}" "${TEST_BASE%%:*}@${TEST_BASE#*@}"
	"$PODMAN" images -a
}

# --- steps that run inside the containers -----------------------------------

inner_build() {
	src=/work/src
	venv=/work/venv-build
	site=$venv/lib/python3.13/site-packages
	mkdir -p "$src" /work/dist
	uv venv --python 3.13.15 "$venv"
	VIRTUAL_ENV=$venv uv pip install \
		-r /recipe/aer-gpu-cu13-build-pins.txt -r /recipe/aer-gpu-cu13-runtime-pins.txt
	VIRTUAL_ENV=$venv uv pip freeze >/work/logs/venv-build-freeze.txt
	PATH=$venv/bin:/usr/local/cuda/bin:$PATH
	export PATH

	tar -xzf "/work/sources/qiskit-aer-$AER_VERSION.tar.gz" -C "$src"
	tar -xzf "/work/sources/nlohmann-json-$JSON_VERSION.tar.gz" -C "$src"

	# nlohmann_json 3.10.2, the release Aer builds against outside conan
	# (Qiskit/qiskit-aer#1742 rejects later headers).
	cmake -S "$src/json-$JSON_VERSION" -B "$src/json-build" -G Ninja \
		-D JSON_BuildTests=OFF -D JSON_MultipleHeaders=OFF \
		-D CMAKE_POLICY_VERSION_MINIMUM=3.5 -D CMAKE_INSTALL_PREFIX="$src/json-prefix" -W no-dev
	cmake --build "$src/json-build"
	cmake --install "$src/json-build"

	cd "$src/qiskit-aer-$AER_VERSION"
	# conan, cmake and ninja come from the pinned venv (--no-isolation).
	sed -i -e '/conan/d' -e '/"cmake/d' -e '/ninja/d' pyproject.toml
	# CCCL 3 headers require C++17 and nvcc accepts fmt's constexpr
	# back_insert_iterator only from C++20.
	sed -i -e 's/^\( *\)CXX_STANDARD 14$/\1CXX_STANDARD 20\n\1CUDA_STANDARD 20/' cmake/FindPybind11.cmake
	grep -q 'CUDA_STANDARD 20' cmake/FindPybind11.cmake
	patch -Np1 -i /host-recipe/aer-cccl3-unary-function.patch
	patch -Np1 -i /recipe/aer-cu13-pip-layout.patch

	export DISABLE_CONAN=ON
	export nlohmann_json_DIR="$src/json-prefix/lib/cmake/nlohmann_json"
	export CUDACXX=/usr/local/cuda/bin/nvcc
	# fmt 9 (spdlog's formatter) turns format strings into consteval checks
	# whenever the host compiler is GCC 10 or later under C++20; nvcc's front
	# end cannot constant-evaluate them, so the CUDA translation units take
	# fmt's own FMT_CONSTEVAL override and check format strings at run time.
	export CUDAFLAGS="-DFMT_CONSTEVAL="
	export AER_THRUST_BACKEND=CUDA
	export AER_CUDA_ARCH="7.5 8.9"
	export AER_PYTHON_CUDA_ROOT="$venv"
	export QISKIT_AER_PACKAGE_NAME=qiskit-aer-gpu-cu13
	export QISKIT_AER_CUDA_MAJOR=13
	export CMAKE_GENERATOR=Ninja
	export CMAKE_BUILD_PARALLEL_LEVEL="$AER_BUILD_JOBS"
	export MAKEFLAGS="-j$AER_BUILD_JOBS"
	export CMAKE_VERBOSE_MAKEFILE=ON
	test -d "$site/cuquantum/include" && test -d "$site/cutensor/include"
	nice -n 19 python -m build --wheel --no-isolation --outdir "$src/raw-dist" .

	cp _skbuild/linux-x86_64-3.13/cmake-build/CMakeCache.txt /work/logs/CMakeCache.txt
	excludes=
	for lib in $CUDA_EXCLUDES; do
		excludes="$excludes --exclude $lib"
	done
	# shellcheck disable=SC2086
	auditwheel repair $excludes -w /work/dist "$src"/raw-dist/*.whl
	auditwheel show /work/dist/*.whl >/work/logs/auditwheel-show.txt
	(cd /work/dist && sha256sum ./*.whl >SHA256SUMS)
	{
		nvcc --version
		g++ --version | head -n 1
		dpkg-query -W -f '${Package} ${Version}\n' g++ libopenblas-dev liblapack-dev \
			libspdlog-dev libfmt-dev libc6 libstdc++6 binutils \
			cuda-nvcc-13-0 cuda-cudart-dev-13-0 cuda-cccl-13-0 libcublas-dev-13-0 \
			libcusolver-dev-13-0 libcusparse-dev-13-0 libnvjitlink-dev-13-0
		uv --version
		python --version
	} >/work/logs/toolchain.txt 2>&1
}

inner_elf_check() {
	out=/work/logs/elf
	mkdir -p "$out"
	cd "$out"
	if [ -d wheel ]; then
		mv wheel "wheel.$(date +%s)"
	fi
	/work/venv-build/bin/python -I -m zipfile -e /work/dist/*.whl wheel
	site=/work/venv-build/lib/python3.13/site-packages
	{
		echo "## shared objects in the wheel"
		find wheel -name '*.so*' -type f | sort
		for so in $(find wheel -name '*.so*' -type f | sort); do
			echo "## $so"
			readelf -d "$so" | grep -E 'NEEDED|RPATH|RUNPATH|SONAME'
			printf 'max GLIBC: '
			objdump -T "$so" | grep -oE 'GLIBC_[0-9]+(\.[0-9]+)*' | sort -uV | tail -n 1
			printf 'max GLIBCXX: '
			objdump -T "$so" | grep -oE 'GLIBCXX_[0-9]+(\.[0-9]+)*' | sort -uV | tail -n 1
			printf 'max CXXABI: '
			objdump -T "$so" | grep -oE 'CXXABI_[0-9]+(\.[0-9]+)*' | sort -uV | tail -n 1
			echo
		done
		echo "## Ubuntu 24.04 ceilings"
		objdump -T /lib/x86_64-linux-gnu/libc.so.6 | grep -oE 'GLIBC_[0-9]+(\.[0-9]+)*' | sort -uV | tail -n 1
		objdump -T /lib/x86_64-linux-gnu/libstdc++.so.6 | grep -oE 'GLIBCXX_[0-9]+(\.[0-9]+)*' | sort -uV | tail -n 1
		echo "## cuobjdump --list-elf controller_wrappers"
		cuobjdump --list-elf wheel/qiskit_aer/backends/controller_wrappers*.so
		echo "## cuobjdump --list-ptx controller_wrappers"
		cuobjdump --list-ptx wheel/qiskit_aer/backends/controller_wrappers*.so || true
		for lib in "$site/cuquantum/lib/libcustatevec.so.1" "$site/cuquantum/lib/libcutensornet.so.2" \
			"$site/cutensor/lib/libcutensor.so.2"; do
			echo "## sm_75 cubins in ${lib#"$site"/}"
			cuobjdump --list-elf "$lib" | grep -c 'sm_75' || true
		done
	} >"$out/elf-report.txt" 2>&1
}

inner_import_check() {
	venv=/work/venv-test
	wheel=$(ls /work/dist/*.whl)
	uv venv --python 3.13.15 "$venv"
	# The wheel's Requires-Dist names the CUDA 13 libraries; the constraint
	# files fix their versions and the numerical stack at requirements.txt.
	VIRTUAL_ENV=$venv uv pip install \
		-c /recipe/aer-gpu-cu13-runtime-pins.txt -c /recipe-requirements.txt \
		"$wheel" qiskit numpy scipy
	VIRTUAL_ENV=$venv uv pip freeze >/work/logs/venv-test-freeze.txt
	"$venv/bin/python" -I -c 'import qiskit_aer; from qiskit_aer.backends import controller_wrappers; print("import ok", qiskit_aer.__version__, controller_wrappers.__file__)'
	LD_BIND_NOW=1 "$venv/bin/python" -I -c 'from qiskit_aer.backends import controller_wrappers; print("LD_BIND_NOW import ok")'
	module=$(ls "$venv"/lib/python3.13/site-packages/qiskit_aer/backends/controller_wrappers*.so)
	echo "## ldd $module"
	ldd "$module"
	if ldd "$module" | grep -q 'not found'; then
		echo "FAIL: unresolved library" >&2
		exit 1
	fi
	echo "## RTLD_NOW load of every CUDA library the module reaches"
	"$venv/bin/python" -I - "$module" <<'EOF'
import ctypes, os, subprocess, sys

module = sys.argv[1]
site = os.path.dirname(os.path.dirname(os.path.dirname(module)))
paths = []
for line in subprocess.run(["ldd", module], capture_output=True, text=True, check=True).stdout.splitlines():
    parts = line.split()
    if "=>" in parts and parts[2].startswith("/"):
        paths.append(os.path.realpath(parts[2]))
cuda = [p for p in paths if p.startswith(site) and "qiskit_aer" not in p]
for path in sorted(set(cuda)):
    ctypes.CDLL(path, mode=os.RTLD_NOW | os.RTLD_GLOBAL)
    print("RTLD_NOW ok", os.path.relpath(path, site))
outside = [p for p in paths if not p.startswith(site) and "/lib/x86_64-linux-gnu/" not in p and "/lib64/" not in p]
print("libraries outside site-packages and the system lib dirs:", outside)
sys.exit(1 if outside else 0)
EOF
}

inner_shadow_check() {
	# The build image holds a second copy of every CUDA 13 toolkit library in
	# /usr/local/cuda/lib64; with that directory on LD_LIBRARY_PATH, as on
	# images that ship a CUDA toolkit, every CUDA library must still resolve
	# from site-packages.
	module=$(ls /work/venv-test/lib/python3.13/site-packages/qiskit_aer/backends/controller_wrappers*.so)
	LD_LIBRARY_PATH=/usr/local/cuda/lib64 ldd "$module" | tee /work/logs/shadow-ldd.txt
	if grep -q '/usr/local/cuda' /work/logs/shadow-ldd.txt; then
		echo "FAIL: LD_LIBRARY_PATH shadows a site-packages CUDA library" >&2
		exit 1
	fi
	echo "no library resolved from /usr/local/cuda"
}

inner_gpu_check() {
	venv=/work/venv-test
	nvidia-smi --query-gpu=name,driver_version,compute_cap --format=csv || true
	"$venv/bin/python" -I - <<'EOF'
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

bell = QuantumCircuit(2)
bell.h(0)
bell.cx(0, 1)
bell.measure_all()
# statevector on Thrust, statevector on cuStateVec, and tensor_network, which
# runs through cuTensorNet, cuTENSOR, cuBLAS and cuSOLVER.
rows = (
    ("statevector", {}),
    ("statevector", {"cuStateVec_enable": True, "batched_shots_gpu": False}),
    ("tensor_network", {}),
)
for method, options in rows:
    sim = AerSimulator(method=method, device="GPU", **options)
    result = sim.run(transpile(bell, sim), shots=1024, seed_simulator=11).result()
    meta = result.results[0].metadata
    print(method, options, "success", result.success, "device", meta.get("device"),
          "cuStateVec_enable", meta.get("cuStateVec_enable"), "counts", result.get_counts())
    assert result.success and meta.get("device") == "GPU"
    if options:
        assert meta.get("cuStateVec_enable") is True
    assert set(result.get_counts()) <= {"00", "11"}
EOF
}

if [ "$#" -eq 0 ]; then
	set -- fetch images build check
fi
# Host steps re-run under flock(1) on WORK/.lock; -o closes the lock's
# descriptor before the script runs, so a container the run starts never
# holds it. Container steps (inner-*) run inside a host step's lock.
case $1 in
inner-*) ;;
*)
	if [ -z "${AER_CU13_LOCKED:-}" ]; then
		mkdir -p "$WORK"
		export AER_CU13_LOCKED=1
		status=0
		flock -n -o -E 75 "$WORK/.lock" sh "$0" "$@" || status=$?
		if [ "$status" -eq 75 ]; then
			log "another run holds $WORK/.lock"
		fi
		exit "$status"
	fi
	;;
esac
for step in "$@"; do
	case $step in
	fetch) step_fetch ;;
	images) step_images ;;
	build) step_build ;;
	check) step_check ;;
	gpu-check) step_gpu_check ;;
	clean) step_clean ;;
	inner-build) inner_build ;;
	inner-elf-check) inner_elf_check ;;
	inner-import-check) inner_import_check ;;
	inner-shadow-check) inner_shadow_check ;;
	inner-gpu-check) inner_gpu_check ;;
	*)
		log "unknown step: $step"
		exit 2
		;;
	esac
done
