# Pre-run prediction for the annual cost stress

**Starting point.** The Maple Education Fund baseline at a 10 basis point annual cost holds 55% BIL and 45% VT. Its modeled net annual return is 6.76% and annualized volatility is 7.04%.

**Changed input.** Raise annual cost from **10 to 75 basis points**, an increase of 65 basis points per year. Keep the **6.50% net annual return target**, the **10% BIL reserve floor**, the estimation window, the price snapshot, and the five-point allocation grid fixed.

**Prediction.** The original mix will fail the return rule because a 0.65 percentage point deduction puts its estimate near **6.11%**. I expect the constrained search to remain feasible, reduce BIL, and increase VT and volatility as it looks for a mix that regains the target. The optimizer may recover the required expected net return by changing weights. I make no directional prediction for the realized return of the newly optimized mix because its holdings change in addition to its fee.

**Decision.** Continue paper pilot only if the search finds a feasible portfolio. Reject the scenario if no grid portfolio clears both mandate rules. Maintain the existing stability condition for any approval to trade.

**Execution plan.** Run `python readiness.py` and `python readiness.py --cost-bps 75` from the commit containing this note. Compare the passing allocation, its net return and volatility, and the unchanged baseline mix under the higher cost.
