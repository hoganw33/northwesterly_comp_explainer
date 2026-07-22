# Northwesterly Cloud - Commission Plan Explainer & What-If Modeler

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

<img width="2038" height="807" alt="image" src="https://github.com/user-attachments/assets/2e786d5e-6036-4754-852f-859638282e84" />

## What's the plan, Stan?

The default plan follows recognized SaaS compensation best practice rather than
arbitrary numbers, aligned with widely recognized SaaS comp practice (e.g., WorldatWork, ZS):

| Attainment | Payout factor (x variable target) | Rationale |
|---|---|---|
| < 50% | 0 - threshold gate | Avoids paying commission to sellers not covering their cost |
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
zero, ~44% landing within 90–115% of quota, and ~13% reaching the President's Club
tier.

## Features

- **Live what-if levers**  gate, tier ceiling, both accelerators, and an
  optional cap. The whole population updates dynamically. KPIs show spend delta
  versus the best practice baseline.
  <img width="366" height="756" alt="image" src="https://github.com/user-attachments/assets/aefc839d-c25b-4e1e-9bb7-2f3a50ae0969" />

- **Population dashboard** - earnings distribution by role, payout curve versus
  baseline, per-band breakdown, top earner by role.
  <img width="835" height="408" alt="image" src="https://github.com/user-attachments/assets/1dd6a256-d9e7-4ab4-a32b-6c4f221291fe" />

- **Seller explainer** - pick any seller and see an auditable, step-by-step
  payout calculation.
  <img width="936" height="534" alt="image" src="https://github.com/user-attachments/assets/4c39f872-7c15-46d4-9d52-df77f67eb3aa" />
  
- **Claude Q&A layer (optional, bring-your-own-key)** - ask natural-language
  questions like "who would be underwater if we capped at 130%?" or "How does the plan work for an AE?" 
  The model answers against the priced data and current plan rules. Your key is used only
  for the request and never stored.
   <img width="907" height="411" alt="image" src="https://github.com/user-attachments/assets/18957332-efc7-4fbe-bcba-071d308a682f" />

## Getting started (first-time setup)

This app runs on your own computer. If you've never used Python before, follow
these steps in order.

### 1. Install Python

Download Python (3.9 or newer) from https://www.python.org/downloads/ and run
the installer.

**Important (Windows):** on the first screen of the installer, check the box
**"Add Python to PATH"** before clicking Install. This lets your computer find
Python from the terminal.

Verify it worked by opening a terminal and running:

    python --version

You should see a version number like `Python 3.12.x`. (On Mac, use `python3`.)

### 2. Get the files

Download this repository (green **Code** button → **Download ZIP**) and unzip
it, or clone it with git. Keep all the files together in one folder -
`northwesterly_cloud_comp_data.xlsx` must sit next to `app.py`.

### 3. Open a terminal in the project folder

- **Windows:** open the folder in File Explorer, click the address bar, type
  `cmd`, and press Enter.
- **Mac:** right-click the folder → **New Terminal at Folder**.

### 4. Install the dependencies (one time)

    pip install -r requirements.txt

### 5. Run the app

    python -m streamlit run app.py

The app opens automatically in your web browser. If your first launch asks for
an email address, just press Enter to skip it - it's optional.

To stop the app later, click the terminal and press `Ctrl + C`.

### 6. (Optional) Enable the Claude Q&A feature

The calculator and dashboard work with no setup. The natural-language Q&A box at
the bottom needs an Anthropic API key, which you enter in the app at runtime -
it is never stored. Get a key at https://console.anthropic.com.

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
