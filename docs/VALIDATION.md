# Local validation

Validated September 22, 2026 (local time).

| Check | Result |
|---|---|
| Windows x64, MinGW-w64 GCC 12.2, static executable | Build and executable checks pass |
| Ubuntu 24.04 / WSL2, GCC 13.3, CMake Release | Build and all three CTest checks pass |
| CUDA 12.6, RTX 3070 Ti Laptop GPU, driver 560.94 | Build and actual GPU executable checks pass |
| CPU/CUDA comparison | Default put estimates differ by approximately 0.033, within the 0.4 regression tolerance |
| Deterministic zero-volatility input | Expected immediate-exercise value reproduced |
| Invalid input and oversized workload rejection | Pass |
| Sparse/high-degree regression case | Finite bounded output; no invalid coefficient propagation |
| Windows and Linux ZIP contents | Extracted binaries executed successfully |
| Offline explorer | Local and historical dataset controls verified in browser |
| Benchmarks | Three path counts × two backends × three measured repetitions after warmup |

Numerical checks additionally exercise a known linear-system solution, repeatability and immediate exercise. These are regression checks, not certified error bounds.

The optional iterative MPI target compiled and completed a two-rank run, but produced approximately 2.99 for a put configuration expected near 6. It is retained as an experimental research artifact and excluded from the quickstart downloads.

Remote GitHub Actions, native Windows CUDA compilation and other GPU architectures have not been validated in this local run. The checked-in CI configuration covers CPU execution on Windows/Linux and CUDA compilation.
