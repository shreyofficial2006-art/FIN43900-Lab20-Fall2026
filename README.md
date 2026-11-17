# FIN 43900 Lab 20 — Project 2 Readiness

**Pilot the Maple Education Fund allocation in a paper portfolio.** The baseline assigns 55% to BIL and 45% to VT, clears the 6.50% modeled net return target and 10% BIL reserve floor, and estimates 7.04% annualized volatility. Pause the pilot if either mandate rule fails. Require changes under 20 percentage points across reasonable estimation windows before implementing it. The 36-month check crosses that threshold.

| Start here | Contents |
|---|---|
| [Lab 20 checkout](CHECKOUT.md) | Cold-run record, changed-input comparison, walkthrough, readiness gaps, and decision line |
| [Executed results](RESULTS.md) | Baselines, mandate verdicts, later evaluation, and five sensitivity runs |
| [Prediction](PREDICTION.md) | Technical scenario recorded before execution |
| [Decision memo](DECISION-MEMO.md) | Mandate, rates data card, monitoring, and reversal conditions |

## Reproduce the result

From the repository root, run this command with Python 3.12. It reads the bundled snapshots and prints the modeled portfolio decisions and reserve verdicts.

```sh
python readiness.py
```

For the web app, install the dependencies once and launch Streamlit. The app uses bundled data and needs no credentials.

```sh
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Leave the target at **6.50%** to see the baseline, then set **Net annual return target (%)** to **7.50%**. The constrained mix should move from **55% BIL / 45% VT** to **40% BIL / 60% VT**. The CLI equivalent is `python readiness.py --target 7.5`.

[Lab 20 instructions](https://github.com/CinderZhang/FIN43900-Fall2026/blob/bb73c5fe49648b5076e8419ff3dd095ffdc13f45/lessons/week-13/lab-20-project2-readiness.md) · [Lab 15 source](https://github.com/shreyofficial2006-art/FIN43900-Lab15-Fall2026/tree/d6f417babe73fda4eb79f855be2c2ca0434023dd) · [Lab 17 rate audit](https://github.com/shreyofficial2006-art/FIN43900-Lab17-Fall2026)
