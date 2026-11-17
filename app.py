"""Streamlit controls for the Maple Education Fund readiness review."""

import streamlit as st

from readiness import AS_OF, EVALUATION_END, gs2_snapshot, pct, run, weights_text


st.set_page_config(page_title="Maple Education Fund", layout="wide")
st.title("Maple Education Fund")
st.caption("Project 2 readiness · Educational analysis")

with st.sidebar:
    st.header("Mandate and assumptions")
    target = st.number_input("Net annual return target (%)", -10.0, 30.0, 6.50, 0.25)
    reserve = st.slider("Minimum BIL reserve (%)", 0, 100, 10, 5)
    cost = st.number_input("Annual cost (basis points)", 0, 500, 10, 5)
    recent = st.toggle("Use the last 36 training months")
    bil_shock = st.number_input("BIL annual return adjustment (percentage points)", -10.0, 10.0, 0.0, 0.25)

inputs, results = run(target / 100, reserve / 100, cost / 10000, recent, bil_shock / 100)
selected = results[-1][1]
st.subheader("Reject for this mandate" if selected is None else "Pilot only")
st.write(f"Training {inputs.first_return_month} to {inputs.last_return_month}. Evaluation October 2025 to September 2026.")
st.dataframe([
    {
        "Portfolio": name, "BIL / IEF / LQD / VT": weights_text(result.weights) if result else "—",
        "Net estimate": pct(result.expected_return if result else None),
        "Annual volatility": pct(result.volatility if result else None), "Mandate": check,
        "Evaluation net return": pct(realized), "Max drawdown": pct(drawdown),
    }
    for name, result, check, realized, drawdown in results
], hide_index=True, width="stretch")

st.subheader("Archived rate context")
for cutoff in (AS_OF, EVALUATION_END):
    vintage, month, value = gs2_snapshot(cutoff)
    st.write(f"**{cutoff} decision cutoff.** GS2 {value:.2f}% for {month:%B %Y}, archive dated {vintage}.")
st.caption("GS2 is a monitoring input. The allocation search uses the frozen fund-price estimates and the selected mandate.")
