"""Regenerate the README's two-panel benchmark figure."""

import csv
import json
from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parents[1]
local = json.loads((root / "benchmarks/rtx3070-wsl.json").read_text())
history = list(csv.DictReader((root / "gpu/summary.csv").open()))
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
fig, axes = plt.subplots(1, 2, figsize=(12, 4.7), facecolor="#f6f8fb")
for ax in axes:
    ax.set_facecolor("#f6f8fb")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.2)
for backend, color in [("cpu", "#8c9db0"), ("cuda", "#147d92")]:
    rows = [r for r in local["rows"] if r["backend"] == backend]
    axes[0].plot(
        [r["paths"] / 1000 for r in rows],
        [r["median_wall_ms"] for r in rows],
        marker="o",
        linewidth=2.5,
        color=color,
        label=backend.upper(),
    )
axes[0].set(
    title="Measured here · solver wall time",
    xlabel="Paths (thousands)",
    ylabel="Median latency (ms)",
)
axes[0].legend(frameon=False)
axes[1].plot(
    [int(r["paths"]) / 1000 for r in history],
    [float(r["avg_speedup"]) for r in history],
    marker="o",
    linewidth=2.5,
    color="#986c3d",
)
axes[1].set(
    title="Historical experiment · pipeline timing",
    xlabel="Paths (thousands)",
    ylabel="Mean reported CPU / GPU ratio",
)
fig.text(
    0.06,
    0.04,
    "Left: RTX 3070 Ti Laptop GPU · WSL2 · 50 steps · put · median of 3 warm runs.\nRight: six contracts per size; original hardware/compiler provenance incomplete. Timing scopes differ.",
    fontsize=9,
    color="#536474",
)
fig.suptitle(
    "Longstaff–Schwartz • where parallel paths pay off", fontsize=16, fontweight="bold"
)
fig.tight_layout(rect=(0, 0.13, 1, 0.92))
(root / "docs/assets").mkdir(parents=True, exist_ok=True)
fig.savefig(root / "docs/assets/performance.png", dpi=180)
