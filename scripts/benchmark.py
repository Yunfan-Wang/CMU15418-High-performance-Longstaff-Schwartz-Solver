"""Benchmark CPU and optional CUDA executables with explicit timing boundaries."""

import argparse
import hashlib
import json
import platform
import statistics
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cpu", required=True, type=Path)
    parser.add_argument("--cuda", type=Path)
    parser.add_argument("--paths", nargs="+", type=int, default=[25000, 50000, 200000])
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Choose a new output path; measurements are not overwritten.")
    rows = []
    for backend, binary in [("cpu", args.cpu), ("cuda", args.cuda)]:
        if binary is None:
            continue
        for count in args.paths:
            command = [
                str(binary.resolve()),
                "--put",
                "--paths",
                str(count),
                "--steps",
                "50",
                "--warmup",
                "1",
                "--repeat",
                str(args.repeats),
                "--json",
            ]
            start = perf_counter()
            result = subprocess.run(
                command, capture_output=True, text=True, timeout=300, check=True
            )
            samples = [json.loads(line) for line in result.stdout.splitlines()]
            assert len(samples) == args.repeats
            rows.append(
                {
                    "backend": backend,
                    "paths": count,
                    "samples": samples,
                    "median_wall_ms": statistics.median(x["wall_ms"] for x in samples),
                    "process_total_ms": (perf_counter() - start) * 1000,
                    "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
                }
            )
    try:
        gpu = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout.strip()
    except FileNotFoundError:
        gpu = "not available"
    payload = {
        "measured_at_utc": datetime.now(timezone.utc).isoformat(),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "gpu": gpu,
        "warmup_calls": 1,
        "repeats": args.repeats,
        "timing": "wall_ms covers solver including allocation/free; excludes process startup and device discovery. process_total_ms covers startup, warmup, repeats and exit.",
        "rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Saved {len(rows)} cases to {args.output}")


if __name__ == "__main__":
    main()
