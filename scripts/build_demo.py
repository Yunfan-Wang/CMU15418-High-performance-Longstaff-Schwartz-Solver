"""Embed repository measurements into the offline HTML explorer."""

import csv
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
local = json.loads((root / "benchmarks/rtx3070-wsl.json").read_text())
rows = {(r["backend"], r["paths"]): r for r in local["rows"]}
current = []
for n in sorted({r["paths"] for r in local["rows"]}):
    cpu, gpu = rows["cpu", n], rows["cuda", n]
    current.append(
        {
            "paths": n,
            "spot": 100,
            "strike": 100,
            "type": "put",
            "cpu_ms": cpu["median_wall_ms"],
            "gpu_ms": gpu["median_wall_ms"],
            "cpu_price": cpu["samples"][0]["price"],
            "gpu_price": gpu["samples"][0]["price"],
        }
    )


def read(name):
    return {
        (int(r["paths"]), r["S0"], r["K"], r["type"]): r
        for r in csv.DictReader((root / "gpu" / name).open())
    }


cpu, gpu = read("results_baseline.csv"), read("results_gpu.csv")
history = []
for key in sorted(cpu.keys() & gpu.keys()):
    c, g = cpu[key], gpu[key]
    history.append(
        {
            "paths": key[0],
            "spot": float(key[1]),
            "strike": float(key[2]),
            "type": key[3],
            "cpu_ms": float(c["time_ms"]),
            "gpu_ms": float(g["time_ms"]),
            "cpu_price": float(c["price"]),
            "gpu_price": float(g["price"]),
        }
    )
path = root / "demo/index.html"
html = path.read_text(encoding="utf-8")
html, count = re.subn(
    r'(<script id="benchmark-data" type="application/json">).*?(</script>)',
    lambda m: m[1] + json.dumps({"local": current, "historical": history}) + m[2],
    html,
    flags=re.S,
)
assert count == 1
path.write_text(html, encoding="utf-8")
print(f"Embedded {len(current)} local and {len(history)} historical cases.")
