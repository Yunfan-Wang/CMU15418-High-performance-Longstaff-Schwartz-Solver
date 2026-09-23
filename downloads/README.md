# Download bundles

These are locally built quickstart artifacts, not a signed or published GitHub Release. Push this folder with the code to make the README's download links work.

| Bundle | Contents |
|---|---|
| lsm-windows-x64.zip | Standalone CPU executable, offline explorer, instructions, build metadata |
| lsm-linux-x64-cuda86.zip | Linux CPU and CUDA executables, explorer, instructions, runtime notices |
| lsm-results-explorer.zip | Standalone HTML explorer; no binary or server required |

## Verify

SHA256SUMS.txt records each archive's SHA-256. manifest.json includes archive sizes, binary hashes and source-file hashes. Each executable bundle also contains BUILD.json.

Windows PowerShell:

```powershell
Get-FileHash .\lsm-windows-x64.zip -Algorithm SHA256
```

Linux:

```bash
sha256sum -c SHA256SUMS.txt
```

Compare only files you downloaded; the full check expects all three ZIPs.

## Build provenance

Windows: MinGW-w64 GCC 12.2.0, C++17, optimization -O3, static runtime, stripped executable.

```sh
g++ -O3 -std=c++17 -static -s -Iapp -Idefault/src app/main.cpp -o build-windows/lsm_cpu.exe
```

Linux: Ubuntu 24.04 / GCC 13.3 / CUDA 12.6.85, root CMake Release build, architecture 86. CUDA runtime linked statically; glibc and libstdc++ remain system dependencies. Tested GPU: RTX 3070 Ti Laptop, driver 560.94 through WSL2.

The CUDA compiler/runtime components were obtained from [NVIDIA's official CUDA 12.6.3 redistribution manifest](https://developer.download.nvidia.com/compute/cuda/redist/redistrib_12.6.3.json), with archive SHA-256 verification. CUDA and GCC runtime notices are included under licenses in the applicable ZIPs; these do not select a project-wide software license.

Repackage after building and verifying:

```sh
python scripts/build_demo.py
python scripts/package.py --windows build-windows/lsm_cpu.exe --linux-dir build-linux
```

Rebuild benchmark records separately if solver binaries change. Do not treat old binary hashes as provenance for a new build.
