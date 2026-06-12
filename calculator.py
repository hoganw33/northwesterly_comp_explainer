"""Northwesterly Cloud — deterministic commission calculator.

One payout curve for all roles for simplicity. Role differentiation comes from each seller's
variable target (pay mix / leverage), not the curve. Design follows recognized
SaaS best practice from ZS and WorldAtWork: a threshold gate, proportional pay to quota, tiered
accelerators above quota, and (by default) an uncapped top tier. In practice, strategic hueristics
would be predetermined and included in the desired outcome.

The Plan object holds all tunable levers so a UI can run what-if scenarios.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Plan:
    """All tunable plan levers. Defaults are the Northwesterly best-practice plan."""
    gate: float = 0.50          # below this attainment fraction, payout = 0
    tier1_mult: float = 1.50    # marginal multiplier from 100% to tier1_top
    tier1_top: float = 1.10     # attainment fraction where tier 1 ends
    tier2_mult: float = 2.00    # marginal multiplier above tier1_top
    cap: Optional[float] = None # optional cap on the payout factor (None = uncapped)

    def label(self) -> str:
        c = "uncapped" if self.cap is None else f"capped {self.cap:.2f}x"
        return (f"gate {self.gate:.0%} | {self.tier1_mult:.2f}x to "
                f"{self.tier1_top:.0%} | {self.tier2_mult:.2f}x above | {c}")


DEFAULT_PLAN = Plan()


def payout_factor(attainment_pct: float, plan: Plan = DEFAULT_PLAN) -> float:
    """Payout as a multiple of variable target for a given attainment %."""
    a = attainment_pct / 100.0
    if a < plan.gate:
        return 0.0
    if a <= 1.0:
        f = a                                   # proportional to quota
    else:
        f = 1.0
        f += plan.tier1_mult * (min(a, plan.tier1_top) - 1.0)
        if a > plan.tier1_top:
            f += plan.tier2_mult * (a - plan.tier1_top)
    if plan.cap is not None:
        f = min(f, plan.cap)
    return f


@dataclass
class Payout:
    seller_id: str
    attainment_pct: float
    variable_target: float
    factor: float
    commission: float
    steps: list


def compute(seller: dict, plan: Plan = DEFAULT_PLAN) -> Payout:
    """Commission for one seller row plus an auditable step breakdown."""
    a = seller["attainment_pct"]
    vt = seller["variable_target"]
    f = payout_factor(a, plan)
    comm = round(vt * f)
    return Payout(seller["seller_id"], a, vt, round(f, 4), comm,
                  _explain(a, vt, f, comm, plan))


def _explain(a_pct, vt, f, comm, plan):
    a = a_pct / 100.0
    s = [f"Attainment: {a_pct:.1f}%  |  Variable target: ${vt:,.0f}"]
    if a < plan.gate:
        s.append(f"Below the {plan.gate:.0%} threshold gate -> no commission earned.")
        s.append("Commission = $0")
        return s
    if a <= 1.0:
        s.append("At or below quota: proportional pay.")
        s.append(f"Factor = attainment = {a:.3f}")
    else:
        s.append("Above quota: proportional base plus tiered accelerators.")
        s.append("  Base to 100%: 1.000x")
        t1 = plan.tier1_mult * (min(a, plan.tier1_top) - 1.0)
        s.append(f"  100-{plan.tier1_top:.0%} tier @ {plan.tier1_mult}x: +{t1:.3f}x")
        if a > plan.tier1_top:
            t2 = plan.tier2_mult * (a - plan.tier1_top)
            s.append(f"  {plan.tier1_top:.0%}+ tier @ {plan.tier2_mult}x: +{t2:.3f}x")
        raw = 1.0 + t1 + (plan.tier2_mult * (a - plan.tier1_top) if a > plan.tier1_top else 0)
        if plan.cap is not None and raw > plan.cap:
            s.append(f"  Capped at {plan.cap:.3f}x (raw {raw:.3f}x)")
        s.append(f"  Total factor = {f:.3f}x")
    s.append(f"Commission = ${vt:,.0f} x {f:.3f} = ${comm:,.0f}")
    return s
