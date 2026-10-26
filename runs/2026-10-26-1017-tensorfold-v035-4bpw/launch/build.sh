#!/bin/bash
# build.sh (inside nvcr.io/nvidia/pytorch:26.07-py3 as the host user): bertholomus TensorFold 0a0b69a (recipe v0.3.5) for GB10, Zig 0.17.0
set -e
export PATH=/zig:$PATH ZIG_GLOBAL_CACHE_DIR=/work/zigcache HOME=/work/home
mkdir -p $HOME $ZIG_GLOBAL_CACHE_DIR
cd /work/engine
zig version; date -u
zig build install native -Dtarget=aarch64-linux-gnu.2.28 -Doptimize=ReleaseFast -Dnvcc=/usr/local/cuda/bin/nvcc -Dsm=121 2>&1 | tail -40
echo "BUILD rc=${PIPESTATUS[0]}"; date -u
ls -la zig-out/bin zig-out/native/bin 2>&1 | head -30
