"""
Nance – User Behaviour and Activity Analysis

Analyses app usage patterns, inactivity detection, streak tracking,
and user engagement classification.
"""

from datetime import date, timedelta
from typing import Dict, List, Optional
import pandas as pd

from config import TODAY


def get_activity_dates(app_activity: pd.DataFrame) -> List[date]:
    """Get sorted list of dates when user opened the app."""
    if app_activity.empty:
        return []
    return sorted(app_activity["date"].tolist())


def get_last_active_date(app_activity: pd.DataFrame) -> Optional[date]:
    """Get the most recent date the user opened the app."""
    dates = get_activity_dates(app_activity)
    return dates[-1] if dates else None


def get_days_since_last_active(
    app_activity: pd.DataFrame,
    as_of: Optional[date] = None,
) -> Optional[int]:
    """Get number of days since user last opened the app."""
    as_of = as_of or TODAY
    last = get_last_active_date(app_activity)
    if last is None:
        return None
    return (as_of - last).days


def get_current_streak(
    app_activity: pd.DataFrame,
    as_of: Optional[date] = None,
) -> int:
    """
    Calculate current consecutive-day streak.
    Counts backwards from as_of (or the last active date if as_of is not active).
    """
    as_of = as_of or TODAY
    dates = set(app_activity["date"].tolist()) if not app_activity.empty else set()

    if not dates:
        return 0

    # Start from as_of or last active date
    if as_of not in dates:
        # If user didn't open today, check yesterday
        if (as_of - timedelta(days=1)) in dates:
            current = as_of - timedelta(days=1)
        else:
            return 0
    else:
        current = as_of

    streak = 0
    while current in dates:
        streak += 1
        current -= timedelta(days=1)

    return streak


def get_longest_streak(app_activity: pd.DataFrame) -> int:
    """Calculate the longest consecutive-day streak ever."""
    dates = get_activity_dates(app_activity)
    if not dates:
        return 0

    date_set = set(dates)
    max_streak = 0
    current_streak = 0
    prev = None

    for d in sorted(date_set):
        if prev and (d - prev).days == 1:
            current_streak += 1
        else:
            current_streak = 1
        max_streak = max(max_streak, current_streak)
        prev = d

    return max_streak


def get_activity_rate(
    app_activity: pd.DataFrame,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> float:
    """
    Calculate the percentage of days the user opened the app in a period.
    """
    if app_activity.empty:
        return 0.0

    start = start_date or min(app_activity["date"])
    end = end_date or TODAY
    total_days = (end - start).days + 1

    if total_days <= 0:
        return 0.0

    active_days = app_activity[
        (app_activity["date"] >= start) & (app_activity["date"] <= end)
    ].shape[0]

    return round(active_days / total_days * 100, 1)


def classify_user_engagement(
    app_activity: pd.DataFrame,
    as_of: Optional[date] = None,
) -> Dict:
    """
    Classify user's engagement level and determine appropriate experience.

    Returns:
        Dict with engagement_level, days_inactive, needs_comeback,
        is_new_user, activity_rate, etc.
    """
    as_of = as_of or TODAY
    days_inactive = get_days_since_last_active(app_activity, as_of)
    streak = get_current_streak(app_activity, as_of)
    total_active_days = len(get_activity_dates(app_activity))

    # Determine engagement level
    if total_active_days == 0:
        engagement = "new"
        needs_comeback = False
        is_new = True
    elif days_inactive is None:
        engagement = "new"
        needs_comeback = False
        is_new = True
    elif days_inactive >= 7:
        engagement = "inactive"
        needs_comeback = True
        is_new = False
    elif days_inactive >= 3:
        engagement = "lapsing"
        needs_comeback = True
        is_new = False
    elif streak >= 5:
        engagement = "highly_active"
        needs_comeback = False
        is_new = False
    elif streak >= 2:
        engagement = "active"
        needs_comeback = False
        is_new = False
    else:
        engagement = "casual"
        needs_comeback = False
        is_new = False

    # Recent activity rate (last 14 days)
    recent_start = as_of - timedelta(days=13)
    recent_rate = get_activity_rate(app_activity, recent_start, as_of)

    return {
        "engagement_level": engagement,
        "days_inactive": days_inactive if days_inactive is not None else 0,
        "needs_comeback": needs_comeback,
        "is_new_user": is_new,
        "current_streak": streak,
        "longest_streak": get_longest_streak(app_activity),
        "total_active_days": total_active_days,
        "recent_activity_rate": recent_rate,
    }


def is_quiet_money_day(
    transactions: pd.DataFrame,
    check_date: Optional[date] = None,
) -> Dict:
    """
    Determine if a date is a "quiet money day" (no transactions recorded).

    Important: We distinguish between:
    - No transactions recorded (may be delayed sync, cash purchases, etc.)
    - Verified no-spend day (only if data strongly supports it)

    Returns dict with is_quiet, reason, and confidence.
    """
    check_date = check_date or TODAY

    if transactions.empty:
        return {
            "is_quiet": True,
            "has_transactions": False,
            "reason": "no_transactions_recorded",
            "is_verified_no_spend": False,
            "message": "No transactions recorded for this day.",
            "note": "This doesn't necessarily mean no spending occurred. "
                    "Transactions may be delayed or not yet synced.",
        }

    day_txns = transactions[transactions["txn_date"] == check_date]

    if day_txns.empty:
        # Check if nearby days have transactions (to gauge data freshness)
        yesterday = check_date - timedelta(days=1)
        tomorrow = check_date + timedelta(days=1)
        has_yesterday = not transactions[transactions["txn_date"] == yesterday].empty
        has_tomorrow = not transactions[transactions["txn_date"] == tomorrow].empty

        if has_yesterday and has_tomorrow:
            confidence = "medium"
            note = ("Adjacent days have recorded transactions, "
                    "so this may be a genuinely quieter day.")
        else:
            confidence = "low"
            note = ("Not enough surrounding data to confirm this was a no-spend day. "
                    "Transactions may be delayed or pending sync.")

        return {
            "is_quiet": True,
            "has_transactions": False,
            "reason": "no_transactions_recorded",
            "is_verified_no_spend": False,
            "confidence": confidence,
            "message": "A quieter day in your recorded transactions.",
            "note": note,
        }

    # Has transactions — check if only credits/money movement
    debits = day_txns[day_txns["transaction_type"] == "debit"]
    real_spending = debits[debits["main_category"].isin(
        set(["Food & Dining", "Groceries", "Shopping", "Bills", "Travel",
             "Transportation", "Entertainment", "Subscriptions", "Personal Care",
             "Hospitals & Pharmacy", "Education", "Fitness & Wellness",
             "Fuel / EV Charging", "Software Tools & Apps", "Housing & Utilities",
             "Rent", "Kids", "Pets", "Sports", "Gifts & Donations",
             "Electronics", "Vehicle", "Insurance Premiums", "Taxes",
             "Banking & Fees", "EMIs & Loans"])
    )]

    if real_spending.empty:
        return {
            "is_quiet": True,
            "has_transactions": True,
            "reason": "only_non_spending",
            "is_verified_no_spend": False,
            "message": "No real spending recorded today — just money movement or income.",
            "note": "Only credits or transfers were recorded. "
                    "Cash or delayed transactions may not be reflected.",
        }

    return {
        "is_quiet": False,
        "has_transactions": True,
        "reason": "has_spending",
        "is_verified_no_spend": False,
        "total_spending": round(real_spending["amount"].sum()),
        "transaction_count": len(real_spending),
    }


def get_weekly_activity_summary(
    app_activity: pd.DataFrame,
    as_of: Optional[date] = None,
    weeks: int = 4,
) -> List[Dict]:
    """Get week-by-week activity summary."""
    as_of = as_of or TODAY
    summaries = []

    for w in range(weeks):
        week_end = as_of - timedelta(days=7 * w)
        week_start = week_end - timedelta(days=6)

        active_dates = app_activity[
            (app_activity["date"] >= week_start) & (app_activity["date"] <= week_end)
        ] if not app_activity.empty else pd.DataFrame()

        summaries.append({
            "week_start": week_start,
            "week_end": week_end,
            "days_active": len(active_dates),
            "rate_pct": round(len(active_dates) / 7 * 100, 1),
        })

    return summaries
