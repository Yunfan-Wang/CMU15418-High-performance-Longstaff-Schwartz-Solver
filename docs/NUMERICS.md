# Numerical scope

The quickstart estimates a finite-exercise-grid value for a vanilla American call or put under single-asset risk-neutral GBM. It uses polynomial least squares to approximate continuation values.

## What the implementation guarantees in software

- The CLI validates finite numbers, positive spot/strike/maturity, nonnegative volatility, bounded dimensions and the CUDA basis-array limit.
- Zero volatility uses an explicit deterministic exercise-grid calculation.
- The CPU and CUDA implementations compare the estimated continuation policy value with immediate exercise at time zero.
- A singular CUDA regression skips the exercise update for that date instead of treating a partially eliminated right-hand side as coefficients.

## What remains approximate

Monte Carlo error, finite exercise dates, basis selection and regression conditioning all affect the estimate. Training and evaluating the exercise rule on the same paths can introduce look-ahead bias; this implementation does not produce an unbiased estimator or a certified lower bound. Normal equations in raw spot powers become poorly conditioned at high degree; start with degree 2.

CPU and GPU random-number generators differ. CUDA's parallel atomic accumulation order also changes floating-point rounding. Equal seeds therefore do not imply identical results or bitwise reproducibility across backends.

The automated price-range checks are broad regression safeguards, not a financial-model certification. The single-asset model has no dividends, calibration, transaction costs or multi-asset correlation.

## Research variants

The iterative MPI and block-local CUDA variants are separate algorithms/estimators, not drop-in evidence of equivalent precision. Their historical performance should be paired with independent accuracy evaluation before comparison.
