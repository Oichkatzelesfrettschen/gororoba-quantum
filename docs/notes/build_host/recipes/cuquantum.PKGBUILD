# Maintainer: eirikr <eirikr@localhost>
#
# NVIDIA cuQuantum SDK redistributable for CUDA 13 (cuStateVec, cuTensorNet,
# cuDensityMat, cuPauliProp, cuStabilizer). The vendor archive and its sha256
# come from the release manifest
# https://developer.download.nvidia.com/compute/cuquantum/redist/redistrib_26.09.0.json
# (cuquantum 26.09.0.8, "cuda13" entry). Shared libraries and headers install
# under /usr in the layout cutensor already uses on this host, so a consumer
# links with CUQUANTUM_ROOT=/usr and needs no ld.so.conf.d entry.

pkgname=cuquantum
pkgver=26.09.0.8
pkgrel=1
pkgdesc="NVIDIA cuQuantum SDK libraries for CUDA 13: cuStateVec, cuTensorNet, cuDensityMat, cuPauliProp, cuStabilizer"
arch=(x86_64)
url="https://developer.nvidia.com/cuquantum-sdk"
license=(LicenseRef-NVIDIA-cuQuantum)
depends=(
    'cuda>=13'
    'cuda<14'
    'cutensor>=2.8'
)
provides=(
    libcustatevec.so=1-64
    libcutensornet.so=2-64
    libcudensitymat.so=0-64
    libcupauliprop.so=0-64
    libcustabilizer.so=0-64
)
options=(!strip !debug)
_archive=cuquantum-linux-x86_64-${pkgver}_cuda13-archive
source=(
    "https://developer.download.nvidia.com/compute/cuquantum/redist/cuquantum/linux-x86_64/$_archive.tar.xz"
)
sha256sums=('92ecbba2b5783db20a966aa67e24206501eef3907ec09dd51cfb4753aea65731')

package() {
    cd "$_archive"
    install -d "$pkgdir"/usr/lib "$pkgdir"/usr/include
    # Shared objects with their soname symlinks; static archives stay out.
    cp -a lib/*.so lib/*.so.* "$pkgdir"/usr/lib/
    cp -a include/. "$pkgdir"/usr/include/
    install -Dm644 LICENSE "$pkgdir"/usr/share/licenses/$pkgname/LICENSE
}
