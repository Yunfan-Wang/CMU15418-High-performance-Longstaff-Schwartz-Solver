# Contributing

Include a minimal command, platform/compiler/GPU details, expected result and observed output.

For changes to numerical code:

1. Build the CPU target and run CTest.
2. Run scripts/verify.py against the CPU binary.
3. If CUDA changes, compile it and run the same executable checks on real GPU hardware.
4. Report price changes alongside timings, including seeds, path counts and timing boundaries.
5. Keep historical artifacts separate from newly measured results.

Avoid claiming exactness, unbiasedness or universal speedups from a small benchmark. Do not replace the original research report or measurements.
