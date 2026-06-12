# Northwesterly Cloud — Commission Plan Explainer & What-If Modeler

An interactive tool that explains every seller's commission payout in plain
language and lets you stress test the plan against real performance data in
real time. Built on synthetic data for a very real B2B cloud company
("Northwesterly Cloud") that I made up. No real company data is used.

![status](https://img.shields.io/badge/status-demo-blue)

## What am I trying to accomplish?

Sellers routinely can't calculate their own commission, and comp teams can't
easily see what a plan change does to total spend until after the fact. This
tool does both: a deterministic calculator that shows the math seller by seller,
plus adjustable plan levers that reprice all 200 sellers live so you can see the
distribution and budget impact of any change before you ship it.

## What's the plan, Stan?

The default plan follows recognized SaaS compensation best practice rather than
arbitrary numbers, using public information from ZS and WorldAtWork:

| Attainment | Payout factor (x variable target) | Rationale |
|---|---|---|
| < 50% | 0 — threshold gate | Avoids paying commission to sellers not covering their cost |
| 50–100% | proportional | Standard ramp to quota |
| 100–110% | +1.5x on each marginal point | First accelerator tier, reachable by the majority |
| 110%+ | +2.0x on each marginal point, uncapped | Rewards overperformance; top tier ≈ President's Club |

Design choices grounded in practice:

- **One curve for all roles.** Role differentiation lives in each seller's
  variable target (pay mix / leverage), not in the curve. Closing roles (AEs)
  carry a richer variable; overlay/specialist roles run a more conservative mix.
  This is why a top AE earns more than a top Sales Engineer. Typically this is by
  design.
- **No hard cap by default.** Most SaaS plans are uncapped; caps are widely
  considered demotivating. A cap toggle is included so you can model the
  trade-off. Typically you would focus on how the multipliers work or quota setting
  if sellers tend to earn higher than forecasted/planned.
- **A thin gated bottom bucket** supports a pay-for-performance distribution
  without penalizing the broad middle.

Validated against the 200-seller dataset, the default plan yields ~3% gated to
zero, ~44% landing within +/-15% of quota, and ~13% reaching the President's Club
tier.

## Features

- **Live what-if levers** — gate, tier ceiling, both accelerators, and an
  optional cap. The whole population updates dynamically. KPIs show spend delta
  versus the best practice baseline.
- **Population dashboard** — earnings distribution by role, payout curve versus
  baseline, per-band breakdown, top earner by role.
- **Seller explainer** — pick any seller and see an auditable, step-by-step
  payout calculation.
- **Claude Q&A layer (optional, bring-your-own-key)** — ask natural-language
  questions like "who would be underwater if we capped at 130%?" or "How does the plan work for an AE?" 
  The model answers against the priced data and current plan rules. Your key is used only
  for the request and never stored.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL Streamlit prints (usually http://localhost:8501).

## Deploy free on Streamlit Community Cloud

1. Push this repo to GitHub.
2. At share.streamlit.io, create a new app pointing at `app.py`.
3. The calculator and dashboard run free for everyone. The Claude Q&A layer
   prompts each visitor for their own Anthropic API key, so there are no API
   costs to the host.

## Files

| File | Purpose |
|---|---|
| `app.py` | Streamlit UI: levers, dashboard, explainer, Q&A |
| `calculator.py` | Deterministic payout engine (`Plan`, `payout_factor`, `compute`) |
| `northwesterly_cloud_comp_data.xlsx` | Synthetic 200-seller dataset |
| `requirements.txt` | Dependencies |

## Data dictionary

`seller_id, full_name, role, segment, region, tenure_months, base_salary,
variable_target, annual_quota, attainment_pct, ytd_bookings`

All data is synthetic and fictional. Northwesterly Cloud is not a real company. Yet. And Don't get any ideas either.
