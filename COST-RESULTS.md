# Executed annual cost stress

Prediction committed before execution at [713dbbb](https://github.com/shreyofficial2006-art/FIN43900-Lab20-Fall2026/commit/713dbbb9e0d486cc526d4b084daea5654b13ae90). Both commands ran from that revision on November 17, 2026.

## Baseline with 10 bp annual cost

Training: 2021-10 to 2025-09 (48 months)
Evaluation: October 2025 to September 2026. Market snapshot retrieved October 22, 2026.
Net return objective 6.50% | BIL floor 10.00% | annual cost 10 bp
Training BIL return adjustment: +0.00 percentage points

| Portfolio | BIL / IEF / LQD / VT | Net estimate | Volatility | Verdict | Evaluation net return | Max drawdown |
|---|---|---:|---:|---|---:|---:|
| Equal weight | 25.00% / 25.00% / 25.00% / 25.00% | 3.18% | 8.04% | FAIL: return objective | 2.98% | -2.65% |
| Inverse volatility | 86.30% / 5.97% / 4.58% / 3.15% | 3.26% | 1.57% | FAIL: return objective | 3.17% | -0.20% |
| 40/60 reference | 0.00% / 0.00% / 40.00% / 60.00% | 6.40% | 13.04% | FAIL: return objective, BIL reserve floor | 8.15% | -4.63% |
| Constrained minimum volatility | 55.00% / 0.00% / 0.00% / 45.00% | 6.76% | 7.04% | PASS | 9.31% | -2.75% |

Constrained decision: PILOT ONLY

GS2 as of 2025-09-30: 3.70% (measured August 2025, vintage 2025-09-30)

GS2 as of 2026-09-30: 4.22% (measured August 2026, vintage 2026-09-30)

## Changed input with 75 bp annual cost

Training: 2021-10 to 2025-09 (48 months)
Evaluation: October 2025 to September 2026. Market snapshot retrieved October 22, 2026.
Net return objective 6.50% | BIL floor 10.00% | annual cost 75 bp
Training BIL return adjustment: +0.00 percentage points

| Portfolio | BIL / IEF / LQD / VT | Net estimate | Volatility | Verdict | Evaluation net return | Max drawdown |
|---|---|---:|---:|---|---:|---:|
| Equal weight | 25.00% / 25.00% / 25.00% / 25.00% | 2.53% | 8.04% | FAIL: return objective | 2.31% | -2.70% |
| Inverse volatility | 86.30% / 5.97% / 4.58% / 3.15% | 2.61% | 1.57% | FAIL: return objective | 2.50% | -0.26% |
| 40/60 reference | 0.00% / 0.00% / 40.00% / 60.00% | 5.75% | 13.04% | FAIL: return objective, BIL reserve floor | 7.45% | -4.68% |
| Constrained minimum volatility | 45.00% / 0.00% / 0.00% / 55.00% | 6.83% | 8.57% | PASS | 9.87% | -3.45% |

Constrained decision: PILOT ONLY

GS2 as of 2025-09-30: 3.70% (measured August 2025, vintage 2025-09-30)

GS2 as of 2026-09-30: 4.22% (measured August 2026, vintage 2026-09-30)
