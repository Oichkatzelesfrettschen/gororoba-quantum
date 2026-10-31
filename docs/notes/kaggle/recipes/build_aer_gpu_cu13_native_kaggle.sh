#!/bin/sh
# Runs the inner_build, check and gpu-check steps of build_aer_gpu_cu13_wheel.sh
# directly on a Kaggle T4 session, with the CUDA 13.0 apt packages of NVIDIA's
# ubuntu2404 repository in place of the cuda:13.0.3-devel image.
# /kaggle/tmp/recipe holds this script, the two pin files, both Aer patches
# (aer-cccl3-unary-function.patch from docs/notes/build_host/recipes),
# requirements.txt and gpu_check.py (the Python heredoc of inner_gpu_check in
# build_aer_gpu_cu13_wheel.sh); the wheel, SHA256SUMS and logs land in
# /kaggle/working.
set -eux
R=/kaggle/tmp/recipe; W=/kaggle/tmp/work; OUT=/kaggle/working; JOBS=4
mkdir -p $W/sources $W/dist $OUT/logs
. /etc/os-release; echo "os $ID $VERSION_ID" > $OUT/logs/os.txt
code=$(echo "$VERSION_ID" | tr -d .)
curl -fsSL -o /tmp/kr.deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu$code/x86_64/cuda-keyring_1.1-1_all.deb
# apt refuses two entries for one repository with different Signed-By keys; the Kaggle image ships its own NVIDIA entry.
grep -l 'developer.download.nvidia.com/compute/cuda' /etc/apt/sources.list /etc/apt/sources.list.d/* 2>/dev/null | while read -r f; do
  case $f in /etc/apt/sources.list) sed -i '/developer.download.nvidia.com\/compute\/cuda/d' "$f" ;; *) mv "$f" "$f.disabled" ;; esac
done
dpkg -i /tmp/kr.deb; apt-get update -q
DEBIAN_FRONTEND=noninteractive apt-get install -y -q --no-install-recommends g++ make patch binutils \
  libopenblas-dev liblapack-dev libspdlog-dev libfmt-dev cuda-nvcc-13-0 cuda-cudart-dev-13-0 cuda-cccl-13-0 \
  libcublas-dev-13-0 libcusolver-dev-13-0 libcusparse-dev-13-0 libnvjitlink-dev-13-0 cuda-cuobjdump-13-0
curl -LsSf https://github.com/astral-sh/uv/releases/download/0.13.0/uv-x86_64-unknown-linux-gnu.tar.gz | tar -xz -C /usr/local/bin --strip-components=1
uv python install 3.13.15
for spec in "qiskit-aer-0.18.2.tar.gz https://github.com/Qiskit/qiskit-aer/archive/0.18.2.tar.gz ab4fa46a70836bff24e95078b10dc316e2c36d85a029de2f5817de41ed746810" \
  "nlohmann-json-3.10.2.tar.gz https://github.com/nlohmann/json/archive/refs/tags/v3.10.2.tar.gz 081ed0f9f89805c2d96335c3acfa993b39a0a5b4b4cef7edb68dd2210a13458c"; do
  set -- $spec; curl -fsSL -o $W/sources/$1 $2; printf '%s  %s\n' $3 $W/sources/$1 | sha256sum -c -
done
src=$W/src; venv=$W/venv-build; site=$venv/lib/python3.13/site-packages; mkdir -p $src
uv venv --python 3.13.15 $venv
uv pip install --python $venv/bin/python -r $R/aer-gpu-cu13-build-pins.txt -r $R/aer-gpu-cu13-runtime-pins.txt
uv pip freeze --python $venv/bin/python > $OUT/logs/venv-build-freeze.txt
$venv/bin/python -c "import build, setuptools, skbuild"
PATH=$venv/bin:/usr/local/cuda-13.0/bin:$PATH; export PATH
tar -xzf $W/sources/qiskit-aer-0.18.2.tar.gz -C $src; tar -xzf $W/sources/nlohmann-json-3.10.2.tar.gz -C $src
cmake -S $src/json-3.10.2 -B $src/json-build -G Ninja -D JSON_BuildTests=OFF -D JSON_MultipleHeaders=OFF \
  -D CMAKE_POLICY_VERSION_MINIMUM=3.5 -D CMAKE_INSTALL_PREFIX=$src/json-prefix -W no-dev
cmake --build $src/json-build; cmake --install $src/json-build
cd $src/qiskit-aer-0.18.2
sed -i -e '/conan/d' -e '/"cmake/d' -e '/ninja/d' pyproject.toml
sed -i -e 's/^\( *\)CXX_STANDARD 14$/\1CXX_STANDARD 20\n\1CUDA_STANDARD 20/' cmake/FindPybind11.cmake
grep -q 'CUDA_STANDARD 20' cmake/FindPybind11.cmake
patch -Np1 -i $R/aer-cccl3-unary-function.patch; patch -Np1 -i $R/aer-cu13-pip-layout.patch
export DISABLE_CONAN=ON nlohmann_json_DIR=$src/json-prefix/lib/cmake/nlohmann_json CUDACXX=/usr/local/cuda-13.0/bin/nvcc \
  CUDAFLAGS="-DFMT_CONSTEVAL=" AER_THRUST_BACKEND=CUDA AER_CUDA_ARCH="7.5 8.9" AER_PYTHON_CUDA_ROOT=$venv \
  QISKIT_AER_PACKAGE_NAME=qiskit-aer-gpu-cu13 QISKIT_AER_CUDA_MAJOR=13 CMAKE_GENERATOR=Ninja \
  CMAKE_BUILD_PARALLEL_LEVEL=$JOBS MAKEFLAGS=-j$JOBS
test -d $site/cuquantum/include && test -d $site/cutensor/include
python -m build --wheel --no-isolation --outdir $src/raw-dist . > $OUT/logs/build.log 2>&1
cp _skbuild/linux-x86_64-3.13/cmake-build/CMakeCache.txt $OUT/logs/
ex=; for l in libcudart.so.13 libcublas.so.13 libcublasLt.so.13 libcusolver.so.12 libcusolverMg.so.12 libcusparse.so.12 libnvJitLink.so.13 libcustatevec.so.1 libcutensornet.so.2 libcutensor.so.2 libcutensorMg.so.2 libcuda.so.1; do ex="$ex --exclude $l"; done
auditwheel repair $ex -w $W/dist $src/raw-dist/*.whl; auditwheel show $W/dist/*.whl > $OUT/logs/auditwheel-show.txt
cp $W/dist/*.whl $OUT/; (cd $OUT && sha256sum ./*.whl > SHA256SUMS)
{ nvcc --version; g++ --version | head -1; uv --version; python --version; } > $OUT/logs/toolchain.txt 2>&1
tv=$W/venv-test; uv venv --python 3.13.15 $tv
uv pip install --python $tv/bin/python -c $R/aer-gpu-cu13-runtime-pins.txt -c $R/requirements.txt $W/dist/*.whl qiskit numpy scipy
mod=$(ls $tv/lib/python3.13/site-packages/qiskit_aer/backends/controller_wrappers*.so); ldd $mod > $OUT/logs/ldd.txt
cuobjdump --list-elf $mod > $OUT/logs/cuobjdump.txt 2>&1 || true
! grep -q 'not found' $OUT/logs/ldd.txt
nvidia-smi --query-gpu=name,driver_version,compute_cap --format=csv > $OUT/logs/gpu.txt || true
$tv/bin/python -I $R/gpu_check.py > $OUT/logs/gpu-check.log 2>&1
echo BUILD_AND_GPU_CHECK_OK
