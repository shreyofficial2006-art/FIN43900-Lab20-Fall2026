"""Reproduce the Maple Education Fund allocation and readiness checks."""

import argparse
import csv
from dataclasses import replace
from datetime import date, datetime
import io
import math
from pathlib import Path

import portfolio as engine


ROOT = Path(__file__).resolve().parent
ASSETS = ("BIL", "IEF", "LQD", "VT")
ELIGIBLE = (True, False, False, False)
TARGET = 0.065
RESERVE = 0.10
COST = 0.0010
AS_OF = date(2025, 9, 30)
EVALUATION_END = date(2026, 9, 30)
BENCHMARK = (0.0, 0.0, 0.4, 0.6)


def read_history():
    with (ROOT / "prices.csv").open(newline="", encoding="utf-8-sig") as file:
        reader = csv.reader(file)
        header = next(reader)
        if tuple(header) != ("Date", *ASSETS):
            raise ValueError("Unexpected fund universe in prices.csv.")
        rows = list(reader)
    training = [row for row in rows if date.fromisoformat(row[0]) <= AS_OF]
    later = [row for row in rows if AS_OF < date.fromisoformat(row[0]) <= EVALUATION_END]
    if len(training) != 49 or len(later) != 12 or training[-1][0] != AS_OF.isoformat():
        raise ValueError("The frozen price window does not match the audit dates.")
    training_csv = io.StringIO()
    csv.writer(training_csv).writerows([header, *training])
    training_csv.seek(0)
    evaluation = [tuple(map(float, row[1:])) for row in [training[-1], *later]]
    return training_csv, evaluation


def gs2_snapshot(cutoff):
    """Return the last published month from the archived table selected by cutoff."""
    with (ROOT / f"GS2-{cutoff}.csv").open(newline="", encoding="utf-8-sig") as file:
        reader = csv.reader(file)
        date_label, series = next(reader)
        vintage = datetime.strptime(series.removeprefix("GS2_"), "%Y%m%d").date()
        if date_label not in ("DATE", "observation_date") or vintage > cutoff:
            raise ValueError("The GS2 download does not prove availability at the cutoff.")
        valid = [(date.fromisoformat(month), float(value)) for month, value in reader
                 if value not in ("", ".") and date.fromisoformat(month) <= cutoff]
    month, value = max(valid)
    return vintage, month, value


def verdict(result, target, reserve):
    rules = []
    if result.expected_return + engine.EPS < target:
        rules.append("return objective")
    if result.reserve_weight + engine.EPS < reserve:
        rules.append("BIL reserve floor")
    return "FAIL: " + ", ".join(rules) if rules else "PASS"


def evaluation_return(weights, prices, cost):
    """Hold the fixed starting mix for 12 months with weight drift and an annual fee."""
    monthly_net = (1.0 - cost) ** (1 / 12)
    nav = [sum(weight * close / initial for weight, close, initial in zip(weights, row, prices[0]))
           * monthly_net ** month for month, row in enumerate(prices)]
    peak = nav[0]
    drawdown = 0.0
    for value in nav:
        peak = max(peak, value)
        drawdown = min(drawdown, value / peak - 1)
    return nav[-1] - 1, drawdown


def run(target=TARGET, reserve=RESERVE, cost=COST, recent=False, bil_shock=0.0):
    if not all(map(math.isfinite, (target, reserve, cost, bil_shock))) or not 0 <= cost < 1:
        raise ValueError("Use finite inputs and an annual cost from 0% up to 100%.")
    training, prices = read_history()
    inputs = engine.estimate_from_csv(training, last_36=recent)
    net_returns = tuple(value - cost + (bil_shock if asset == "BIL" else 0)
                        for asset, value in zip(ASSETS, inputs.expected_returns))
    model = replace(inputs, expected_returns=net_returns)
    mixes = {
        "Equal weight": engine.evaluate_portfolio((0.25,) * 4, model, ELIGIBLE),
        "Inverse volatility": engine.evaluate_portfolio(engine.inverse_volatility_weights(model.volatilities), model, ELIGIBLE),
        "40/60 reference": engine.evaluate_portfolio(BENCHMARK, model, ELIGIBLE),
        "Constrained minimum volatility": engine.search_lowest_risk(model, target, ELIGIBLE, reserve),
    }
    results = []
    for name, mix in mixes.items():
        if mix is None:
            results.append((name, None, "FAIL: no feasible mix", None, None))
        else:
            performance, drawdown = evaluation_return(mix.weights, prices, cost)
            results.append((name, mix, verdict(mix, target, reserve), performance, drawdown))
    return model, results


def pct(value):
    return "—" if value is None else f"{value:.2%}"


def weights_text(weights):
    return " / ".join(f"{weight:.2%}" for weight in weights)


def render_report(target, reserve, cost, recent=False, bil_shock=0.0):
    inputs, results = run(target, reserve, cost, recent, bil_shock)
    print(f"Training: {inputs.first_return_month} to {inputs.last_return_month} ({inputs.months} months)")
    print("Evaluation: October 2025 to September 2026. Market snapshot retrieved October 22, 2026.")
    print(f"Net return objective {pct(target)} | BIL floor {pct(reserve)} | annual cost {cost * 10000:g} bp")
    print(f"Training BIL return adjustment: {bil_shock * 100:+.2f} percentage points")
    print()
    print(f"| Portfolio | {' / '.join(ASSETS)} | Net estimate | Volatility | Verdict | Evaluation net return | Max drawdown |")
    print("|---|---|---:|---:|---|---:|---:|")
    for name, mix, check, realized, drawdown in results:
        if mix is None:
            print(f"| {name} | — | — | — | {check} | — | — |")
        else:
            print(f"| {name} | {weights_text(mix.weights)} | {pct(mix.expected_return)} | "
                  f"{pct(mix.volatility)} | {check} | {pct(realized)} | {pct(drawdown)} |")
    best = results[-1][1]
    print()
    print("Constrained decision: " + ("REJECT FOR THIS MANDATE" if best is None else "PILOT ONLY"))
    for cutoff in (AS_OF, EVALUATION_END):
        vintage, month, value = gs2_snapshot(cutoff)
        print(f"\nGS2 as of {cutoff}: {value:.2f}% (measured {month:%B %Y}, vintage {vintage})")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=float, default=TARGET * 100, help="annual net return target in percent")
    parser.add_argument("--reserve", type=float, default=RESERVE * 100, help="BIL floor in percent of portfolio")
    parser.add_argument("--cost-bps", type=float, default=COST * 10000, help="annual cost in basis points")
    parser.add_argument("--recent-36", action="store_true", help="use the last 36 training returns")
    parser.add_argument("--bil-shock", type=float, default=0.0, help="BIL return adjustment in percentage points")
    args = parser.parse_args()
    render_report(args.target / 100, args.reserve / 100, args.cost_bps / 10000, args.recent_36, args.bil_shock / 100)


if __name__ == "__main__":
    main()
