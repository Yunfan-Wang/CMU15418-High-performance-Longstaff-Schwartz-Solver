# Benchmark methodology

## Three different clocks

| Field | Scope |
|---|---|
| wall_ms | Solver invocation, including allocation/free; excludes process startup and device discovery |
| device_pipeline_ms | CUDA events from after allocations to final result copy; includes the host-solve gaps in the recorded timeline |
| path_simulation_ms | CUDA path-generation kernel interval |

The benchmark JSON additionally records process_total_ms for the entire command, including startup, warmup, repeated invocations and shutdown. Do not divide it by repetitions and call the result steady-state solver latency.

Each benchmark command uses one warmup and three repetitions by default. The default workload is an at-the-money put, 50 exercise dates, degree 2, rate .05, volatility .2, maturity 1, seed 42. Raw repetitions, parameters, binary SHA-256, GPU/driver and host platform are recorded.

## Local observation

The checked-in rtx3070-wsl.json was measured on an RTX 3070 Ti Laptop GPU through WSL2, with GCC 13.3 and CUDA 12.6. The laptop was not an isolated benchmarking appliance; power limits, temperature and concurrent desktop activity can affect latency. Medians from three runs are descriptive, not confidence intervals.

The data remains tied to the recorded binary hashes. Rebuilding with a different compiler, architecture or optimization level creates a new experiment.

## Historical observation

gpu/results_baseline.csv and gpu/results_gpu.csv contain 24 matched records: four path counts and six spot/strike/type combinations. gpu/summary.csv summarizes case-wise timing ratios and price differences.

The historical GPU timer excludes allocation and initialization, whereas the original CPU timer wraps the pricing function. Hardware/compiler details are incomplete. The historical ratios are retained for provenance, not used as the quickstart's measured headline.

## Regenerate presentation assets

```bash
python -m pip install matplotlib
python scripts/plot_results.py
python scripts/build_demo.py
```

These use checked-in records. They do not silently rerun or replace the experiment. New runs should use a new JSON output path.
