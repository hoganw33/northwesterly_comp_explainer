"""Northwesterly Cloud — Commission Plan Explainer & What-If Modeler.

A deterministic payout calculator with adjustable plan levers, a live
population dashboard, and an optional Claude-powered Q&A layer (bring your
own Anthropic API key). Built on synthetic data for a very real company I made up.
"""

import pandas as pd
import streamlit as st
import altair as alt
from calculator import Plan, payout_factor, compute, DEFAULT_PLAN

st.set_page_config(page_title="Northwesterly Comp Explainer",
                   page_icon="📊", layout="wide")

# ---------------------------------------------------------------- data
@st.cache_data
def load_data(path="northwesterly_cloud_comp_data.xlsx"):
    return pd.read_excel(path)

def price(df, plan):
    d = df.copy()
    d["factor"] = d["attainment_pct"].apply(lambda a: payout_factor(a, plan))
    d["commission"] = (d["variable_target"] * d["factor"]).round()
    d["total_comp"] = d["base_salary"] + d["commission"]
    return d

df = load_data()

# ---------------------------------------------------------------- sidebar levers
st.sidebar.title("Plan Levers")
st.sidebar.caption("Adjust the plan and watch the whole 200-seller "
                   "population change live.")
gate = st.sidebar.slider("Threshold gate (% attainment)", 0, 90, 50, 5,
                         help="Below this, no commission is earned.") / 100
t1_top = st.sidebar.slider("Tier-1 ceiling (% attainment)", 105, 150, 110, 5) / 100
t1 = st.sidebar.slider("Tier-1 accelerator (100%–ceiling)", 1.0, 3.0, 1.5, 0.1)
t2 = st.sidebar.slider("Tier-2 accelerator (above ceiling)", 1.0, 4.0, 2.0, 0.1)
capped = st.sidebar.checkbox("Apply a hard cap", value=False,
                             help="Industry best practice: most SaaS plans are uncapped.")
cap = st.sidebar.slider("Cap (× variable target)", 1.0, 4.0, 1.55, 0.05) if capped else None

plan = Plan(gate=gate, tier1_mult=t1, tier1_top=t1_top, tier2_mult=t2, cap=cap)
base = price(df, DEFAULT_PLAN)
cur = price(df, plan)

st.sidebar.divider()
if st.sidebar.button("Reset to default"):
    st.rerun()

# ---------------------------------------------------------------- header
st.title("Northwesterly Cloud — Commission Plan Explainer")
st.caption(f"Current plan: {plan.label()}")

# ---------------------------------------------------------------- KPIs
n = len(cur)
spend = cur["commission"].sum()
base_spend = base["commission"].sum()
near = ((cur.attainment_pct >= 90) & (cur.attainment_pct <= 115)).mean()
club = (cur.attainment_pct >= 130).mean()
gated = (cur.factor == 0).mean()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total commission spend", f"${spend/1e6:.2f}M",
          f"{(spend-base_spend)/1e6:+.2f}M vs best-practice")
c2.metric("Near target (90–115%)", f"{near:.0%}")
c3.metric("President's Club (≥130%)", f"{club:.0%}")
c4.metric("Gated to $0", f"{gated:.0%}")

st.divider()
left, right = st.columns([3, 2])

# ---------------------------------------------------------------- distribution
with left:
    st.subheader("Earnings Distribution")
    chart = alt.Chart(cur).mark_bar(opacity=0.85).encode(
        x=alt.X("commission:Q", bin=alt.Bin(maxbins=30), title="Commission ($)"),
        y=alt.Y("count()", title="Sellers"),
        color=alt.Color("role:N", legend=alt.Legend(title="Role")),
        tooltip=["role:N", alt.Tooltip("count()", title="sellers")],
    ).properties(height=300)
    st.altair_chart(chart, use_container_width=True)

    st.subheader("Payout Curve")
    pts = pd.DataFrame({"attainment_pct": range(0, 200)})
    pts["Current plan"] = pts.attainment_pct.apply(lambda a: payout_factor(a, plan))
    pts["Best practice"] = pts.attainment_pct.apply(lambda a: payout_factor(a, DEFAULT_PLAN))
    curve = pts.melt("attainment_pct", var_name="plan", value_name="factor")
    line = alt.Chart(curve).mark_line().encode(
        x=alt.X("attainment_pct:Q", title="Attainment (%)"),
        y=alt.Y("factor:Q", title="Payout factor (× target)"),
        color=alt.Color("plan:N", title=""),
        strokeDash=alt.StrokeDash("plan:N", legend=None),
    ).properties(height=240)
    st.altair_chart(line, use_container_width=True)

# ---------------------------------------------------------------- band table
with right:
    st.subheader("By Attainment Band")
    bands = [(0, 50), (50, 90), (90, 100), (100, 110), (110, 130), (130, 1000)]
    rows = []
    for lo, hi in bands:
        m = (cur.attainment_pct >= lo) & (cur.attainment_pct < hi)
        if m.any():
            rows.append({
                "Band": f"{lo}–{hi if hi < 1000 else '+'}%",
                "Sellers": int(m.sum()),
                "Avg factor": f"{cur.loc[m, 'factor'].mean():.2f}x",
                "Avg comm": f"${cur.loc[m, 'commission'].mean():,.0f}",
            })
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

    st.subheader("Top Earner By Role")
    top = cur.loc[cur.groupby("role").total_comp.idxmax()]
    st.dataframe(
        top[["role", "attainment_pct", "total_comp"]]
        .assign(total_comp=lambda d: d.total_comp.map("${:,.0f}".format),
                attainment_pct=lambda d: d.attainment_pct.map("{:.1f}%".format))
        .rename(columns={"role": "Role", "attainment_pct": "Attain.",
                         "total_comp": "Total comp"}),
        hide_index=True, use_container_width=True)

st.divider()

# ---------------------------------------------------------------- seller explainer
st.subheader("Explain a seller's payout")
sel = st.selectbox("Seller", cur.seller_id + " — " + cur.full_name)
sid = sel.split(" — ")[0]
row = df[df.seller_id == sid].iloc[0].to_dict()
p = compute(row, plan)
a, b = st.columns([1, 1])
with a:
    st.markdown(f"**{row['full_name']}** · {row['role']} · {row['segment']} · {row['region']}")
    st.code("\n".join(p.steps), language="text")
with b:
    st.metric("Commission", f"${p.commission:,.0f}")
    st.metric("Total comp", f"${row['base_salary'] + p.commission:,.0f}")

st.divider()

# ---------------------------------------------------------------- Claude Q&A
st.subheader("Ask Claude about the plan")
st.caption("Bring your own Anthropic API key. Nothing is stored. "
           "Try: \"Who would be underwater if we capped at 130%?\"")
key = st.text_input("Anthropic API key", type="password",
                    placeholder="sk-ant-...")
q = st.text_input("Question")
if st.button("Ask") and q:
    if not key:
        st.warning("Enter an API key to use the Q&A layer.")
    else:
        try:
            import anthropic
            ctx = cur[["seller_id", "full_name", "role", "segment", "region",
                       "tenure_months", "base_salary", "variable_target",
                       "annual_quota", "attainment_pct", "commission",
                       "total_comp"]].to_csv(index=False)
            system = (
                "You are a sales compensation analyst for Northwesterly Cloud, "
                "a fictional B2B cloud company. Answer using ONLY the plan rules "
                "and Excel data provided. Be concise and show the math. "
                f"Plan rules: {plan.label()}. Below the gate, payout is $0; "
                "from gate to 100% payout is proportional to attainment; above "
                "100% tiered accelerators apply to each marginal point.\n\n"
                f"Seller data (already priced under the current plan):\n{ctx}"
            )
            client = anthropic.Anthropic(api_key=key)
            with st.spinner("Hmm, let me think on that..."):
                msg = client.messages.create(
                    model="claude-sonnet-4-6", max_tokens=1024,
                    system=system,
                    messages=[{"role": "user", "content": q}])
            st.markdown("".join(b.text for b in msg.content if b.type == "text"))
        except Exception as e:
            st.error(f"Error: {e}")
