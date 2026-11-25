"""
Nance – Transaction Processing and Financial Calculations

Core financial logic: spending aggregation, budget analysis,
pattern detection, and category insights.
"""

import pandas as pd
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

from config import (
    TODAY, REAL_SPENDING_CATEGORIES, NON_SPENDING_CATEGORIES,
    MONEY_MOVEMENT_CATEGORIES, format_inr,
)


def filter_real_spending(txns: pd.DataFrame) -> pd.DataFrame:
    """Filter to only real spending transactions (debits in spending categories)."""
    if txns.empty:
        return txns
    mask = (
        (txns["transaction_type"] == "debit")
        & (txns["main_category"].isin(REAL_SPENDING_CATEGORIES))
    )
    return txns[mask].copy()


def get_spending_by_category(
    txns: pd.DataFrame,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> Dict[str, float]:
    """Get total spending per category in a date range."""
    spending = filter_real_spending(txns)
    if spending.empty:
        return {}
    if start_date:
        spending = spending[spending["txn_date"] >= start_date]
    if end_date:
        spending = spending[spending["txn_date"] <= end_date]
    if spending.empty:
        return {}
    return spending.groupby("main_category")["amount"].sum().to_dict()


def get_total_spending(
    txns: pd.DataFrame,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> float:
    """Get total real spending in a date range."""
    cats = get_spending_by_category(txns, start_date, end_date)
    return sum(cats.values())


def get_daily_spending(
    txns: pd.DataFrame,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> Dict[date, float]:
    """Get spending per day."""
    spending = filter_real_spending(txns)
    if spending.empty:
        return {}
    if start_date:
        spending = spending[spending["txn_date"] >= start_date]
    if end_date:
        spending = spending[spending["txn_date"] <= end_date]
    if spending.empty:
        return {}
    return spending.groupby("txn_date")["amount"].sum().to_dict()


def get_spending_trend(
    txns: pd.DataFrame,
    current_start: date,
    current_end: date,
    previous_start: date,
    previous_end: date,
) -> Dict[str, Dict]:
    """
    Compare spending between two periods by category.
    Returns dict of category -> {current, previous, change_pct, direction}.
    """
    current = get_spending_by_category(txns, current_start, current_end)
    previous = get_spending_by_category(txns, previous_start, previous_end)

    all_cats = set(list(current.keys()) + list(previous.keys()))
    trends = {}

    for cat in all_cats:
        curr_amt = current.get(cat, 0)
        prev_amt = previous.get(cat, 0)

        if prev_amt > 0:
            change_pct = ((curr_amt - prev_amt) / prev_amt) * 100
        elif curr_amt > 0:
            change_pct = 100.0  # New spending
        else:
            change_pct = 0.0

        if change_pct > 5:
            direction = "up"
        elif change_pct < -5:
            direction = "down"
        else:
            direction = "stable"

        trends[cat] = {
            "current": curr_amt,
            "previous": prev_amt,
            "change_pct": round(change_pct, 1),
            "direction": direction,
        }

    return trends


def get_budget_status(
    txns: pd.DataFrame,
    budgets: pd.DataFrame,
    as_of: Optional[date] = None,
) -> List[Dict]:
    """
    Calculate budget utilisation for active budgets.
    Returns list of dicts with budget info and spending status.
    """
    if budgets.empty:
        return []

    as_of = as_of or TODAY
    active = budgets[(budgets["from_date"] <= as_of) & (budgets["to_date"] >= as_of)]

    if active.empty:
        return []

    results = []
    spending = filter_real_spending(txns)

    for _, budget in active.iterrows():
        cat = budget["main_category"]
        limit = budget["amount"]
        start = budget["from_date"]
        end = budget["to_date"]

        if cat == "ALL":
            if not spending.empty:
                period_spending = spending[
                    (spending["txn_date"] >= start) & (spending["txn_date"] <= as_of)
                ]
                spent = period_spending["amount"].sum()
            else:
                spent = 0
        else:
            if not spending.empty:
                period_spending = spending[
                    (spending["txn_date"] >= start)
                    & (spending["txn_date"] <= as_of)
                    & (spending["main_category"] == cat)
                ]
                spent = period_spending["amount"].sum()
            else:
                spent = 0

        # Calculate days remaining in period
        total_days = (end - start).days + 1
        days_elapsed = (as_of - start).days + 1
        days_remaining = max(0, (end - as_of).days)

        utilisation = (spent / limit * 100) if limit > 0 else 0

        if utilisation > 100:
            status = "exceeded"
        elif utilisation > 80:
            status = "warning"
        elif utilisation > 50:
            status = "on_track"
        else:
            status = "healthy"

        # Projected spending at current rate
        if days_elapsed > 0:
            daily_rate = spent / days_elapsed
            projected = daily_rate * total_days
        else:
            projected = 0

        results.append({
            "budget_id": budget["budget_id"],
            "category": cat,
            "limit": limit,
            "spent": round(spent),
            "remaining": round(max(0, limit - spent)),
            "utilisation_pct": round(utilisation, 1),
            "status": status,
            "days_remaining": days_remaining,
            "days_elapsed": days_elapsed,
            "total_days": total_days,
            "projected": round(projected),
            "period_type": budget["period_type"],
        })

    return results


def find_recurring_expenses(txns: pd.DataFrame, min_occurrences: int = 2) -> List[Dict]:
    """
    Identify recurring expenses based on merchant and amount patterns.
    """
    spending = filter_real_spending(txns)
    if spending.empty:
        return []

    # Group by merchant + approximate amount
    recurring = []
    merchants = spending[spending["merchant_name"] != ""].groupby("merchant_name")

    for merchant, group in merchants:
        if len(group) < min_occurrences:
            continue

        # Check if amounts are similar (within 20%)
        amounts = group["amount"].values
        mean_amt = amounts.mean()
        if mean_amt == 0:
            continue

        std_pct = (amounts.std() / mean_amt * 100) if len(amounts) > 1 else 0

        if std_pct < 25:  # Fairly consistent amount
            dates = sorted(group["txn_date"].tolist())
            recurring.append({
                "merchant": merchant,
                "category": group["main_category"].mode().iloc[0],
                "avg_amount": round(mean_amt),
                "occurrences": len(group),
                "last_date": max(dates),
                "is_subscription": group["payment_mode"].mode().iloc[0] == "auto-debit",
                "consistency": "high" if std_pct < 10 else "medium",
            })

    recurring.sort(key=lambda x: x["occurrences"], reverse=True)
    return recurring


def get_top_spending_categories(
    txns: pd.DataFrame,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    top_n: int = 5,
) -> List[Dict]:
    """Get the top N spending categories by amount."""
    cats = get_spending_by_category(txns, start_date, end_date)
    if not cats:
        return []

    total = sum(cats.values())
    sorted_cats = sorted(cats.items(), key=lambda x: x[1], reverse=True)[:top_n]

    return [
        {
            "category": cat,
            "amount": round(amt),
            "percentage": round(amt / total * 100, 1) if total > 0 else 0,
        }
        for cat, amt in sorted_cats
    ]


def get_weekend_vs_weekday_spending(
    txns: pd.DataFrame,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> Dict:
    """Compare weekend vs weekday spending."""
    spending = filter_real_spending(txns)
    if spending.empty:
        return {"weekday_avg": 0, "weekend_avg": 0, "ratio": 0}

    if start_date:
        spending = spending[spending["txn_date"] >= start_date]
    if end_date:
        spending = spending[spending["txn_date"] <= end_date]

    if spending.empty:
        return {"weekday_avg": 0, "weekend_avg": 0, "ratio": 0}

    spending = spending.copy()
    spending["is_weekend"] = spending["txn_date"].apply(lambda d: d.weekday() >= 5)

    weekend = spending[spending["is_weekend"]]["amount"]
    weekday = spending[~spending["is_weekend"]]["amount"]

    # Count days
    all_dates = set()
    if start_date and end_date:
        d = start_date
        while d <= end_date:
            all_dates.add(d)
            d += timedelta(days=1)
    else:
        all_dates = set(spending["txn_date"].unique())

    weekend_days = sum(1 for d in all_dates if d.weekday() >= 5) or 1
    weekday_days = sum(1 for d in all_dates if d.weekday() < 5) or 1

    weekend_avg = weekend.sum() / weekend_days if not weekend.empty else 0
    weekday_avg = weekday.sum() / weekday_days if not weekday.empty else 0

    ratio = weekend_avg / weekday_avg if weekday_avg > 0 else 0

    return {
        "weekday_avg": round(weekday_avg),
        "weekend_avg": round(weekend_avg),
        "weekday_total": round(weekday.sum()) if not weekday.empty else 0,
        "weekend_total": round(weekend.sum()) if not weekend.empty else 0,
        "ratio": round(ratio, 2),
    }


def detect_unusual_spending(
    txns: pd.DataFrame,
    lookback_days: int = 7,
    comparison_days: int = 30,
    threshold_pct: float = 50.0,
    as_of: Optional[date] = None,
) -> List[Dict]:
    """
    Detect categories where recent spending is unusual compared to historical average.
    """
    as_of = as_of or TODAY
    recent_start = as_of - timedelta(days=lookback_days)
    history_start = as_of - timedelta(days=comparison_days + lookback_days)
    history_end = recent_start - timedelta(days=1)

    recent = get_spending_by_category(txns, recent_start, as_of)
    historical = get_spending_by_category(txns, history_start, history_end)

    if not recent or not historical:
        return []

    # Normalise to daily averages
    unusual = []
    for cat, recent_total in recent.items():
        hist_total = historical.get(cat, 0)
        recent_daily = recent_total / lookback_days
        hist_daily = hist_total / comparison_days if comparison_days > 0 else 0

        if hist_daily > 0:
            change_pct = ((recent_daily - hist_daily) / hist_daily) * 100
            if abs(change_pct) >= threshold_pct:
                unusual.append({
                    "category": cat,
                    "recent_daily": round(recent_daily),
                    "historical_daily": round(hist_daily),
                    "change_pct": round(change_pct, 1),
                    "direction": "higher" if change_pct > 0 else "lower",
                })

    unusual.sort(key=lambda x: abs(x["change_pct"]), reverse=True)
    return unusual


def get_payment_mode_breakdown(txns: pd.DataFrame) -> Dict[str, float]:
    """Get spending breakdown by payment mode."""
    spending = filter_real_spending(txns)
    if spending.empty:
        return {}
    return spending.groupby("payment_mode")["amount"].sum().to_dict()
