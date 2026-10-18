# Two images for build_aer_gpu_cu13_wheel.sh, both on Ubuntu 24.04 (glibc
# 2.39), the base of the Kaggle GPU image. The build stage carries the CUDA
# 13.0 toolkit, whose runtime the T4 driver (580, CUDA 13.0) accepts; the
# test stage carries no CUDA library, so every CUDA library the module loads
# there comes from pip wheels in site-packages.

ARG BUILD_BASE=docker.io/nvidia/cuda:13.0.3-devel-ubuntu24.04@sha256:7d56ebe2b7cd864a60dca3c8b2d0a39f8fc110417e8253e32505c3387f59119c
ARG TEST_BASE=docker.io/library/ubuntu:noble-20260917@sha256:f610ab94648195aa356059f5b41d6085c9d4d903c072430cdd1af7bdb646106b

FROM ${BUILD_BASE} AS build
# OpenBLAS, spdlog and fmt link into the module and auditwheel grafts their
# shared objects into the wheel; binutils supplies readelf and objdump.
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      g++ make patch ca-certificates binutils \
      libopenblas-dev liblapack-dev libspdlog-dev libfmt-dev \
 && apt-get clean && rm -rf /var/lib/apt/lists/*
ADD --checksum=sha256:1468ebd5a5541121837c5a2817b9972ba6090fa6caa3d142620850a47fb75154 \
    https://github.com/astral-sh/uv/releases/download/0.13.0/uv-x86_64-unknown-linux-gnu.tar.gz /tmp/uv.tar.gz
ENV UV_PYTHON_INSTALL_DIR=/opt/python UV_PYTHON_PREFERENCE=only-managed
RUN tar -xzf /tmp/uv.tar.gz -C /usr/local/bin --strip-components=1 \
 && rm /tmp/uv.tar.gz \
 && uv python install 3.13.15

FROM ${TEST_BASE} AS test
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ca-certificates \
 && apt-get clean && rm -rf /var/lib/apt/lists/*
ADD --checksum=sha256:1468ebd5a5541121837c5a2817b9972ba6090fa6caa3d142620850a47fb75154 \
    https://github.com/astral-sh/uv/releases/download/0.13.0/uv-x86_64-unknown-linux-gnu.tar.gz /tmp/uv.tar.gz
ENV UV_PYTHON_INSTALL_DIR=/opt/python UV_PYTHON_PREFERENCE=only-managed
RUN tar -xzf /tmp/uv.tar.gz -C /usr/local/bin --strip-components=1 \
 && rm /tmp/uv.tar.gz \
 && uv python install 3.13.15
