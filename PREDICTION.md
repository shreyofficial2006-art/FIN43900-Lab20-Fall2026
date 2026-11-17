# Lab 20 changed input prediction

Increase the minimum modeled **net annual return** from **6.50% to 7.50%**. Keep the 10% BIL reserve floor, the training window, fund prices, five-point weight grid, and 10 basis point annual cost assumption fixed.

A higher target removes portfolios from the feasible set. If any portfolio remains feasible, its minimum attainable volatility should be at least as high as the baseline's, and its estimated net return must meet 7.50%. I expect a higher equity weight if there is a feasible mix. If the constrained search finds no feasible mix, the decision should be **reject for this mandate**. If it finds a feasible but less stable mix, the decision should remain **pilot only**, subject to the same stability and data checks. Later realized returns can move in either direction.

Recorded on November 17, 2026, before the paired technical runs in this package. See [the checkout](CHECKOUT.md) for the separate student record status.
