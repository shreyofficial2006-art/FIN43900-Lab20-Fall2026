"""FIN 43900 Lab 15: reusable, standard-library-only portfolio engine.

Returns, volatilities, and weights are decimals inside the engine (0.065 = 6.5%).
Run `python portfolio.py` for the three Lab 14 training baselines.
"""
from dataclasses import dataclass
from datetime import date
import csv
import io
import math
from pathlib import Path
import statistics

# Editable course-authored training inputs, NOT observed market estimates.
MERIDIAN_ASSETS = ('Treasury bills', 'Treasury 10-year note',
                   'Investment-grade bonds', 'Global equity')
MERIDIAN_RETURNS = (0.035, 0.043, 0.050, 0.080)
MERIDIAN_VOLATILITIES = (0.005, 0.070, 0.060, 0.160)
MERIDIAN_CORRELATIONS = [
    [1.00, 0.10, 0.05, 0.00],
    [0.10, 1.00, 0.80, -0.10],
    [0.05, 0.80, 1.00, 0.25],  # IG-equity: edit this and the matching cell below.
    [0.00, -0.10, 0.25, 1.00],
]
MERIDIAN_OBJECTIVE = 0.065
MERIDIAN_RESERVE_MINIMUM = 0.03
MERIDIAN_RESERVE_ELIGIBLE = (True, True, False, False)
EPS = 1e-12


@dataclass(frozen=True)
class MarketInputs:
    assets: tuple
    expected_returns: tuple
    volatilities: tuple
    correlations: tuple
    label: str = 'estimate'
    months: int = 0
    first_return_month: str = ''
    last_return_month: str = ''


@dataclass(frozen=True)
class PortfolioResult:
    weights: tuple
    expected_return: float
    volatility: float
    reserve_weight: float
    tested_mixes: int = 0
    feasible_mixes: int = 0


def meridian_inputs():
    """Read editable training constants each time this function is called."""
    return MarketInputs(MERIDIAN_ASSETS, MERIDIAN_RETURNS, MERIDIAN_VOLATILITIES,
                        tuple(tuple(row) for row in MERIDIAN_CORRELATIONS),
                        label='course-authored training values')


def validate_correlations(correlations, n):
    """Reject bad dimensions, bounds, asymmetry, or an impossible risk matrix."""
    if len(correlations) != n or any(len(row) != n for row in correlations):
        raise ValueError('Correlation table must be a square matrix matching the assets.')
    for i in range(n):
        for j in range(n):
            value = correlations[i][j]
            if not math.isfinite(value) or not -1 <= value <= 1:
                raise ValueError('Every correlation must be finite and between -1 and 1.')
            if abs(value - correlations[j][i]) > EPS:
                raise ValueError('Correlation table must be symmetric; edit both matching cells.')
        if abs(correlations[i][i] - 1) > EPS:
            raise ValueError('Every diagonal correlation must equal 1.')
    # A semidefinite Cholesky check also accepts singular, valid correlations.
    lower = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            residual = correlations[i][j] - sum(lower[i][k] * lower[j][k] for k in range(j))
            if i == j:
                if residual < -1e-10:
                    raise ValueError('Correlation matrix must be positive semidefinite.')
                lower[i][j] = math.sqrt(max(0.0, residual))
            elif lower[j][j] > 1e-10:
                lower[i][j] = residual / lower[j][j]
            elif abs(residual) > 1e-10:
                raise ValueError('Correlation matrix must be positive semidefinite.')


def covariance_matrix(inputs):
    n = len(inputs.assets)
    if not 3 <= n <= 6 or len(set(inputs.assets)) != n:
        raise ValueError('Use three to six uniquely named assets.')
    if len(inputs.expected_returns) != n or len(inputs.volatilities) != n:
        raise ValueError('Each asset needs one return and one volatility.')
    if any(not math.isfinite(x) for x in inputs.expected_returns):
        raise ValueError('Expected returns must be finite.')
    if any(not math.isfinite(x) or x < 0 for x in inputs.volatilities):
        raise ValueError('Volatilities must be finite and nonnegative.')
    validate_correlations(inputs.correlations, n)
    return tuple(tuple(inputs.correlations[i][j] * inputs.volatilities[i]
                       * inputs.volatilities[j] for j in range(n)) for i in range(n))


def expected_return(weights, returns):
    return sum(weight * value for weight, value in zip(weights, returns))


def portfolio_variance(weights, covariance):
    return sum(weights[i] * weights[j] * covariance[i][j]
               for i in range(len(weights)) for j in range(len(weights)))


def portfolio_volatility(weights, covariance):
    variance = portfolio_variance(weights, covariance)
    if variance < -EPS:
        raise ValueError('Negative portfolio variance: check the risk inputs.')
    return math.sqrt(max(0.0, variance))


def reserve_weight(weights, eligible):
    return sum(weight for weight, counts in zip(weights, eligible) if counts)


def evaluate_portfolio(weights, inputs, eligible):
    if len(weights) != len(inputs.assets) or len(eligible) != len(weights):
        raise ValueError('Weights and reserve flags must match the assets.')
    if any(not math.isfinite(w) or w < 0 for w in weights) or abs(sum(weights) - 1) > EPS:
        raise ValueError('Long-only weights must be nonnegative and sum to 100%.')
    covariance = covariance_matrix(inputs)
    return PortfolioResult(tuple(weights), expected_return(weights, inputs.expected_returns),
                           portfolio_volatility(weights, covariance), reserve_weight(weights, eligible))


def inverse_volatility_weights(volatilities):
    if any(vol <= 0 for vol in volatilities):
        raise ValueError('Inverse-volatility weights require positive volatilities.')
    inverse = [1 / vol for vol in volatilities]
    return tuple(value / sum(inverse) for value in inverse)


def grid_units(total, assets):
    """Yield each allocation of integer units exactly once, with no shorting."""
    if assets == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in grid_units(total - first, assets - 1):
            yield (first,) + rest


def search_lowest_risk(inputs, objective, eligible, minimum_reserve, step_points=5):
    """Exhaust all long-only grid mixes; return the least volatile feasible mix.

    The reserve rule is >=, not an exact equality. A 3% minimum therefore requires
    at least 5% on a 5-percentage-point grid. None means infeasible on this grid.
    """
    covariance = covariance_matrix(inputs)                  # Validate once, before searching.
    n = len(inputs.assets)
    if len(eligible) != n:
        raise ValueError('One reserve-eligibility flag is required per asset.')
    if not math.isfinite(objective) or not math.isfinite(minimum_reserve) or not 0 <= minimum_reserve <= 1:
        raise ValueError('Use a finite objective and a reserve minimum from 0% to 100%.')
    if not isinstance(step_points, int) or step_points <= 0 or 100 % step_points:
        raise ValueError('The grid step must be a positive integer dividing 100.')
    units = 100 // step_points
    best = None
    best_variance = math.inf
    tested = feasible = 0
    for allocation in grid_units(units, n):                 # Enumerate every mix summing to 100%.
        tested += 1
        weights = tuple(value / units for value in allocation)
        ret = expected_return(weights, inputs.expected_returns)
        reserve = reserve_weight(weights, eligible)
        if ret + EPS < objective or reserve + EPS < minimum_reserve:
            continue                                      # Discard a failed mandate rule.
        feasible += 1
        variance = portfolio_variance(weights, covariance)
        if variance < best_variance - 1e-15:               # Strict improvement; ties keep first.
            best_variance = variance
            best = (weights, ret, math.sqrt(max(0.0, variance)), reserve)
    if best is None:
        return None                                       # Do not lower the objective.
    return PortfolioResult(*best, tested_mixes=tested, feasible_mixes=feasible)


def largest_weight_change(first, second):
    """Percentage points, not relative percent. Missing mix -> not applicable."""
    if first is None or second is None:
        return None
    if len(first.weights) != len(second.weights):
        raise ValueError('Compare the same asset universe.')
    return max(abs(a - b) for a, b in zip(first.weights, second.weights)) * 100


def estimate_from_csv(source, last_36=False):
    """Sample moments from monthly adjusted prices, using 60 or last 36 returns.

    `source` is a file path, bytes, or a readable file. No filling of missing prices.
    Sample standard deviations and correlations use the same return observations.
    """
    if hasattr(source, 'read'):
        text = source.read()
    elif isinstance(source, bytes):
        text = source
    else:
        text = Path(source).read_bytes()
    if isinstance(text, bytes):
        text = text.decode('utf-8-sig')
    rows = list(csv.reader(io.StringIO(text)))
    if len(rows) < 4:
        raise ValueError('CSV needs a header and at least three monthly price rows.')
    assets = tuple(name.strip() for name in rows[0][1:])
    if not 3 <= len(assets) <= 6 or len(set(assets)) != len(assets) or any(not a for a in assets):
        raise ValueError('CSV needs three to six unique, nonempty ticker columns after Date.')
    if rows[0][0].strip().lower() != 'date':
        raise ValueError('The first CSV column must be Date (YYYY-MM-DD).')
    dates, prices = [], []
    previous_month = None
    for line, row in enumerate(rows[1:], start=2):
        if len(row) != len(assets) + 1:
            raise ValueError(f'CSV row {line}: missing or extra columns; no prices are filled.')
        try:
            stamp = date.fromisoformat(row[0])
            values = tuple(float(value) for value in row[1:])
        except ValueError as error:
            raise ValueError(f'CSV row {line}: use ISO dates and numeric adjusted prices.') from error
        if any(not math.isfinite(value) or value <= 0 for value in values):
            raise ValueError(f'CSV row {line}: adjusted prices must be finite and positive.')
        month = stamp.year * 12 + stamp.month
        if previous_month is not None and month != previous_month + 1:
            raise ValueError('Use exactly one price per month, oldest first, with no missing months.')
        dates.append(stamp.isoformat())
        prices.append(values)
        previous_month = month
    returns = [tuple(current[i] / previous[i] - 1 for i in range(len(assets)))
               for previous, current in zip(prices, prices[1:])]
    if last_36:
        if len(returns) < 36:
            raise ValueError('Last-36-month mode requires at least 37 monthly prices.')
        returns = returns[-36:]
    columns = list(zip(*returns))
    means = tuple(statistics.mean(column) for column in columns)
    stds = tuple(statistics.stdev(column) for column in columns)
    correlations = tuple(tuple(
        1.0 if i == j else
        (max(-1.0, min(1.0, statistics.correlation(columns[i], columns[j])))
         if stds[i] > 0 and stds[j] > 0 else 0.0)
        for j in range(len(assets))) for i in range(len(assets)))
    inputs = MarketInputs(assets, tuple(value * 12 for value in means),
                          tuple(value * math.sqrt(12) for value in stds), correlations,
                          'historical arithmetic estimate; not a forecast', len(returns),
                          dates[-len(returns)][:7], dates[-1][:7])
    covariance_matrix(inputs)
    return inputs


def main():
    inputs = meridian_inputs()
    baselines = (
        ('Benchmark', (0, 0, 0.4, 0.6)),
        ('Equal weight', (0.25,) * 4),
        ('Inverse volatility', inverse_volatility_weights(inputs.volatilities)),
    )
    print('Meridian baselines | course-authored training values')
    print('Weights: bills / 10-year / IG / equity; objective: 6.50%')
    for name, weights in baselines:
        result = evaluate_portfolio(weights, inputs, MERIDIAN_RESERVE_ELIGIBLE)
        print(f'{name}: ' + ' / '.join(f'{w * 100:.1f}' for w in weights))
        print(f'  Return {result.expected_return * 100:.2f}% | '
              f'Volatility {result.volatility * 100:.2f}% | '
              f'Reserve {result.reserve_weight * 100:.1f}% | '
              f'Meets objective: {"yes" if result.expected_return + EPS >= MERIDIAN_OBJECTIVE else "no"}')


if __name__ == '__main__':
    try:
        main()
    except ValueError as error:
        raise SystemExit(f'Input error: {error}')
