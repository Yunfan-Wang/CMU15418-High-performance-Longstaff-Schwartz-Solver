"""Create the small download bundles from already-built, verified executables."""

import argparse
import hashlib
import json
from pathlib import Path
import zipfile

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--windows", type=Path, required=True)
parser.add_argument("--linux-dir", type=Path, required=True)
args = parser.parse_args()
out = root / "downloads"
out.mkdir(exist_ok=True)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


guide = r"""LSM Solver quickstart

Windows: double-click lsm_cpu.exe, or run:
  .\lsm_cpu.exe --demo
  .\lsm_cpu.exe --put --paths 200000 --steps 50 --json

Linux / WSL2: chmod +x lsm_cpu lsm_cuda
  ./lsm_cpu --demo
  ./lsm_cuda --put --paths 200000 --steps 50 --warmup 1 --repeat 3 --json

The Windows binary runs on CPU. The Linux CUDA binary targets compute capability
8.6 with PTX and was tested on Ubuntu 24.04 / WSL2 with an RTX 3070 Ti Laptop GPU.
It needs a compatible NVIDIA driver and Ubuntu 24.04-era system libraries.
The CUDA runtime is linked statically; no Toolkit is needed to run this bundle.

Open index.html for an offline explorer of recorded benchmark results.
These are a finite-grid, single-asset research solver and recorded measurements.

Source and numerical limitations:
https://github.com/Yunfan-Wang/CMU15418-High-performance-Longstaff-Schwartz-Solver
"""
bundles = [
    ("lsm-windows-x64.zip", [(args.windows, "lsm_cpu.exe")], False),
    (
        "lsm-linux-x64-cuda86.zip",
        [
            (args.linux_dir / "lsm_cpu", "lsm_cpu"),
            (args.linux_dir / "lsm_cuda", "lsm_cuda"),
        ],
        True,
    ),
    ("lsm-results-explorer.zip", [], False),
]
manifest = {
    "format": 1,
    "source_files": {},
    "bundles": [],
    "windows_build": "MinGW-w64 GCC 12.2.0; -O3 -std=c++17 -static -s",
    "linux_build": "Ubuntu 24.04; GCC 13.3.0; CUDA 12.6.85; CMake Release; architecture 86",
}
for path in [
    root / "CMakeLists.txt",
    *sorted((root / "app").glob("*")),
    root / "default/src/lsm.hpp",
    root / "gpu/lsm.cu",
    root / "gpu/lsm.hpp",
]:
    manifest["source_files"][path.relative_to(root).as_posix()] = sha(path)
for name, files, cuda in bundles:
    archive = out / name
    binary_records = {label: sha(path) for path, label in files}
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for path, label in files:
            z.write(path, label)
        z.write(root / "demo/index.html", "index.html")
        z.writestr("START-HERE.txt", guide)
        z.writestr(
            "BUILD.json",
            json.dumps(
                {
                    **{k: v for k, v in manifest.items() if k != "bundles"},
                    "binary_sha256": binary_records,
                },
                indent=2,
            ),
        )
        if files:
            for path in (root / "docs/third-party").glob("GCC-*"):
                z.write(path, "licenses/" + path.name)
        if cuda:
            z.write(
                root / "docs/third-party/CUDA-LICENSE.txt", "licenses/CUDA-LICENSE.txt"
            )
    manifest["bundles"].append(
        {
            "file": name,
            "bytes": archive.stat().st_size,
            "sha256": sha(archive),
            "binaries": binary_records,
        }
    )
(out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
(out / "SHA256SUMS.txt").write_text(
    "".join(f"{b['sha256']}  {b['file']}\n" for b in manifest["bundles"]),
    encoding="ascii",
)
for b in manifest["bundles"]:
    print(b["file"], b["bytes"], "bytes")
