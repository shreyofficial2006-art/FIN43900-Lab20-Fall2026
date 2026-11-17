# Lab 20 checkout — Project 2 readiness

**Committee decision.** Pilot the 55% BIL / 45% VT allocation on paper and pause if the return or reserve rule fails. Require weight changes under 20 percentage points across reasonable windows before trading. The 36-month run moved both active weights by 30 points.

## Cold run and readiness review

The repository provides a dependency-free reproduction command and an interactive app for reviewing the decision. The package combines the existing Lab 15 Maple analysis with the archived GS2 availability procedure from Lab 17.

| Item | Recorded result |
|---|---|
| Technical clean-folder run | `python readiness.py` from a fresh directory containing the lab files on November 17, 2026 |
| First failure | None. Exit code 0. |
| Elapsed time | 0.903 seconds for the baseline CLI run, excluding setup and copying |
| Where the result appears | Terminal portfolio table and the [saved results](RESULTS.md). The [app](app.py) displays the same verdict and evaluation numbers. |
| Fix or rerun | The automated clean-folder run was clean. No fix was required for that run. |
| Partner cold-run note | The partner's command, first issue, elapsed time, and output location are not linked in this record. The timed run above records the separate technical verification. |

## Changed input

The [pre-run scenario note](PREDICTION.md) raises the net annual return target from **6.50% to 7.50%**. The reserve floor, fee, training data, and five-point grid stay fixed. The technical prediction was that the feasible set would shrink, that the selected risk could not decrease, and that the surviving mix would likely hold more equity. The baseline and challenge are both in the [executed output](RESULTS.md).

| Measure | Baseline | Higher target | Change |
|---|---:|---:|---:|
| Net annual return objective | 6.50% | 7.50% | +1.00 pp |
| BIL reserve | 55.00% | 40.00% | −15.00 pp |
| VT weight | 45.00% | 60.00% | +15.00 pp |
| Estimated net annual return | 6.76% | 7.85% | +1.09 pp |
| Estimated annual volatility | 7.04% | 9.34% | +2.30 pp |
| Net return in later evaluation | 9.31% | 11.23% | +1.92 pp |
| Mandate verdict | Pass | Pass | No change |

The higher objective excludes the low-risk baseline mix. The least volatile surviving mix replaces 15 percentage points of BIL with VT, the stronger estimated return source, and annualized volatility rises by 2.30 points. The pilot-only stance holds because feasibility in this scenario leaves the window sensitivity and the short evaluation period unresolved. The higher later return is the outcome of one historical period.

**Separate student record.** The original pre-run GitHub commit is not linked in this checkout. The dated technical prediction and executed comparison document this package's reproducible sensitivity.

## Explain the decision code

1. `read_history` takes the 49 price observations through September 2025 and keeps the next 12 months for evaluation. The portfolio engine estimates annualized means and covariances on the 48 training returns.
2. `run` deducts the annual cost assumption from the return estimates. It checks equal weight, inverse volatility, the 40/60 reference, and the constrained allocation against the same target and reserve rules.
3. `search_lowest_risk` enumerates long-only portfolios on a five-point grid. It discards mixes below the return target or BIL floor, then chooses the surviving mix with the smallest `wᵀΣw`. It returns no mix if the mandate is infeasible.
4. `evaluation_return` applies the chosen starting weights to the later price path with drift and an annual fee. The later prices never select the weights.

**Walkthrough question.** Why can the 40/60 reference earn 8.15% in the later window and still fail? The mandate tests the estimated net return and reserve weight at the decision point. Its estimate is 6.40% and its BIL weight is 0%. A realized return from the following year cannot change those inputs.

## Remaining Project 2 checklist

| Item | Readiness |
|---|---|
| App, one-command run, visible outcome | Available. Both portfolio rule checks and the later evaluation are visible. |
| Decision memo and GS2 data card | Available in the [decision memo](DECISION-MEMO.md). |
| Baselines and stress cases | Available in [the results](RESULTS.md), including cost, window, reserve floor, and expected return. |
| Original partner note and locked prediction commit | Link the original records when available. |
| Videos 1–3 and transcripts | Links remain unresolved in this Lab 20 package. Verify each Project 2 link and transcript separately. |

The clean-folder run showed the visible result could be rebuilt with only the repository files. Moving the target showed that a passing verdict can still require materially more risk. Before Project 2 submission, preserve the evaluation dates, baseline rule, data vintages, and unrounded inputs. The first priority is linking the original records and comparing every recorded result to the memo and the app. [Lab 20 instructions](https://github.com/CinderZhang/FIN43900-Fall2026/blob/bb73c5fe49648b5076e8419ff3dd095ffdc13f45/lessons/week-13/lab-20-project2-readiness.md)
