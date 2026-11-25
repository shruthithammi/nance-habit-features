"""
Nance – Personalised Insight Generation

Generates the "Daily Money Moment" and other personalised insights
based on transaction history, budgets, activity, and user context.
"""

import random
from datetime import date, timedelta
from typing import Dict, List, Optional
import pandas as pd

from config import TODAY, format_inr, REAL_SPENDING_CATEGORIES
from transaction_processor import (
    get_spending_by_category, get_total_spending, get_spending_trend,
    get_budget_status, find_recurring_expenses, get_top_spending_categories,
    get_weekend_vs_weekday_spending, detect_unusual_spending,
    get_daily_spending,
)
from user_behaviour import (
    classify_user_engagement, is_quiet_money_day, get_current_streak,
)


def generate_daily_money_moment(
    txns: pd.DataFrame,
    budgets: pd.DataFrame,
    app_activity: pd.DataFrame,
    as_of: Optional[date] = None,
) -> Dict:
    """
    Generate the personalised Daily Money Moment insight.

    This is the core engagement feature — a short, meaningful insight
    that gives the user a reason to open Nance.

    Returns dict with type, title, message, detail, and metadata.
    """
    as_of = as_of or TODAY
    engagement = classify_user_engagement(app_activity, as_of)
    quiet_day = is_quiet_money_day(txns, as_of)

    # ── Priority 1: Comeback experience ──────────────────────────────
    if engagement["needs_comeback"]:
        return _generate_comeback_moment(engagement, txns, as_of)

    # ── Priority 2: New user welcome ─────────────────────────────────
    if engagement["is_new_user"]:
        return _generate_new_user_moment(txns, as_of)

    # ── Priority 3: Quiet money day ──────────────────────────────────
    if quiet_day["is_quiet"]:
        return _generate_quiet_day_moment(quiet_day, txns, as_of)

    # ── Priority 4: Select the most relevant insight ─────────────────
    insights = _gather_candidate_insights(txns, budgets, as_of)

    if not insights:
        return _generate_fallback_moment(txns, as_of)

    # Pick the highest-priority insight
    insights.sort(key=lambda x: x.get("priority", 0), reverse=True)
    return insights[0]


def _generate_comeback_moment(engagement: Dict, txns: pd.DataFrame, as_of: date) -> Dict:
    """Generate a welcoming comeback experience for returning users."""
    days = engagement["days_inactive"]

    if days >= 14:
        title = "Welcome back! 👋"
        message = ("It's been a while — and that's perfectly okay. "
                   "Let's take a fresh look at your finances together.")
    elif days >= 7:
        title = "Good to see you again! 🌟"
        message = ("Your next money check-in starts right now. "
                   "One look is all it takes to stay aware.")
    else:
        title = "Hey, welcome back! ☀️"
        message = ("A few days away? No worries at all. "
                   "Let's catch up on what's been happening with your money.")

    # Provide a quick summary of what happened during absence
    absence_start = as_of - timedelta(days=days)
    total_spent = get_total_spending(txns, absence_start, as_of)

    detail = None
    if total_spent > 0:
        detail = (f"While you were away, {format_inr(total_spent)} in spending "
                  f"was recorded over {days} days. Take a moment to review when you're ready.")

    return {
        "type": "comeback",
        "title": title,
        "message": message,
        "detail": detail,
        "icon": "👋",
        "priority": 100,
    }


def _generate_new_user_moment(txns: pd.DataFrame, as_of: date) -> Dict:
    """Generate a welcoming moment for new users."""
    total_txns = len(txns) if not txns.empty else 0

    if total_txns == 0:
        message = ("Welcome to Nance! Once your transactions start appearing, "
                   "you'll get personalised insights about your money right here.")
    else:
        message = ("Welcome to your Daily Money Moment! "
                   "Each day, Nance will share something useful about your finances — "
                   "a pattern, a reflection, or a simple check-in.")

    return {
        "type": "new_user",
        "title": "Your first Money Moment ✨",
        "message": message,
        "detail": None,
        "icon": "✨",
        "priority": 100,
    }


def _generate_quiet_day_moment(quiet_info: Dict, txns: pd.DataFrame, as_of: date) -> Dict:
    """Generate insight for a quiet money day."""
    reason = quiet_info["reason"]

    if reason == "no_transactions_recorded":
        title = "A quieter day 🍃"
        message = quiet_info["message"]
        detail = quiet_info.get("note", "")
    elif reason == "only_non_spending":
        title = "No spending recorded today 🍃"
        message = quiet_info["message"]
        detail = quiet_info.get("note", "")
    else:
        title = "A quiet moment 🍃"
        message = "Take a moment to review your recent spending."
        detail = None

    # Add a reflection prompt
    reflection = random.choice([
        "A good day to review your recent transactions.",
        "Take a moment to check your budget progress.",
        "Perhaps review a subscription or recurring payment?",
        "Your money check-in is still valuable, even on quiet days.",
    ])

    return {
        "type": "quiet_day",
        "title": title,
        "message": message,
        "detail": detail,
        "reflection": reflection,
        "icon": "🍃",
        "priority": 90,
    }


def _gather_candidate_insights(
    txns: pd.DataFrame,
    budgets: pd.DataFrame,
    as_of: date,
) -> List[Dict]:
    """Gather all possible insights and score them."""
    insights = []

    # ── Budget progress insight ──────────────────────────────────────
    budget_statuses = get_budget_status(txns, budgets, as_of)
    for bs in budget_statuses:
        if bs["status"] == "exceeded":
            cat_label = "overall spending" if bs["category"] == "ALL" else bs["category"]
            insights.append({
                "type": "budget_alert",
                "title": f"Budget check: {cat_label} 📊",
                "message": (
                    f"Your {cat_label} spending ({format_inr(bs['spent'])}) "
                    f"has passed your {format_inr(bs['limit'])} budget. "
                    f"One tough period doesn't define your financial journey."
                ),
                "detail": (
                    f"{bs['days_remaining']} days left in this budget period. "
                    "Understanding where you are is the first step."
                ),
                "icon": "📊",
                "priority": 85,
            })
        elif bs["status"] == "warning":
            cat_label = "overall spending" if bs["category"] == "ALL" else bs["category"]
            insights.append({
                "type": "budget_progress",
                "title": f"Budget update: {cat_label} 📋",
                "message": (
                    f"You've used {bs['utilisation_pct']}% of your {cat_label} budget "
                    f"({format_inr(bs['spent'])} of {format_inr(bs['limit'])})."
                ),
                "detail": f"{bs['days_remaining']} days remaining in this period.",
                "icon": "📋",
                "priority": 75,
            })

    # ── Spending trend insight ───────────────────────────────────────
    week_end = as_of
    week_start = as_of - timedelta(days=6)
    prev_end = week_start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=6)

    trends = get_spending_trend(txns, week_start, week_end, prev_start, prev_end)
    for cat, trend in trends.items():
        if trend["direction"] == "up" and trend["change_pct"] > 30 and trend["current"] > 500:
            insights.append({
                "type": "spending_trend",
                "title": f"Spending trend: {cat} 📈",
                "message": (
                    f"Your {cat} spending is up {trend['change_pct']}% this week "
                    f"compared to last week ({format_inr(trend['current'])} vs "
                    f"{format_inr(trend['previous'])})."
                ),
                "detail": "Worth noticing — you can decide if it needs attention.",
                "icon": "📈",
                "priority": 65,
            })
        elif trend["direction"] == "down" and trend["change_pct"] < -30 and trend["previous"] > 500:
            insights.append({
                "type": "spending_trend",
                "title": f"Spending shift: {cat} 📉",
                "message": (
                    f"Your {cat} spending decreased by {abs(trend['change_pct'])}% "
                    f"this week. That's a noticeable change."
                ),
                "detail": None,
                "icon": "📉",
                "priority": 55,
            })

    # ── Unusual spending detection ───────────────────────────────────
    unusual = detect_unusual_spending(txns, as_of=as_of)
    for u in unusual[:2]:  # Top 2
        if u["direction"] == "higher":
            insights.append({
                "type": "unusual_spending",
                "title": f"Pattern spotted: {u['category']} 🔍",
                "message": (
                    f"Your recent {u['category']} spending "
                    f"({format_inr(u['recent_daily'])}/day) is notably higher than "
                    f"your usual pattern ({format_inr(u['historical_daily'])}/day)."
                ),
                "detail": "This might be intentional — just making sure you've noticed.",
                "icon": "🔍",
                "priority": 60,
            })

    # ── Recurring expense reminder ───────────────────────────────────
    recurring = find_recurring_expenses(txns)
    if recurring:
        sub = [r for r in recurring if r["is_subscription"]]
        if sub:
            top_sub = sub[0]
            insights.append({
                "type": "recurring_expense",
                "title": f"Subscription check: {top_sub['merchant']} 🔄",
                "message": (
                    f"You're paying ~{format_inr(top_sub['avg_amount'])} to "
                    f"{top_sub['merchant']} regularly ({top_sub['occurrences']} times "
                    f"recently). Still using it?"
                ),
                "detail": "Reviewing subscriptions helps you stay on top of recurring costs.",
                "icon": "🔄",
                "priority": 50,
            })

    # ── Weekend spending insight ─────────────────────────────────────
    if as_of.weekday() == 0:  # Monday
        weekend_data = get_weekend_vs_weekday_spending(
            txns, as_of - timedelta(days=9), as_of - timedelta(days=1)
        )
        if weekend_data["weekend_avg"] > 0:
            insights.append({
                "type": "weekend_review",
                "title": "Weekend spending review 🗓️",
                "message": (
                    f"This past weekend, you averaged "
                    f"{format_inr(weekend_data['weekend_avg'])}/day in spending "
                    f"(weekday average: {format_inr(weekend_data['weekday_avg'])}/day)."
                ),
                "detail": None,
                "icon": "🗓️",
                "priority": 45,
            })

    # ── Yesterday's spending summary ─────────────────────────────────
    yesterday = as_of - timedelta(days=1)
    daily = get_daily_spending(txns, yesterday, yesterday)
    if yesterday in daily and daily[yesterday] > 0:
        insights.append({
            "type": "daily_summary",
            "title": "Yesterday's spending 📝",
            "message": f"You recorded {format_inr(daily[yesterday])} in spending yesterday.",
            "detail": "Quick check-ins like this keep you in touch with your money.",
            "icon": "📝",
            "priority": 40,
        })

    return insights


def _generate_fallback_moment(txns: pd.DataFrame, as_of: date) -> Dict:
    """Generate a fallback insight when nothing specific stands out."""
    # Simple financial reflection
    reflections = [
        {
            "title": "Daily money check-in ☀️",
            "message": "Take a moment to notice your spending today. Even a quick look counts.",
        },
        {
            "title": "Financial awareness moment 💡",
            "message": "Understanding your money starts with small, consistent check-ins.",
        },
        {
            "title": "Your money, your pace 🌱",
            "message": "No major patterns to flag today. Your regular check-in is keeping you aware.",
        },
    ]

    choice = reflections[as_of.toordinal() % len(reflections)]

    return {
        "type": "reflection",
        "title": choice["title"],
        "message": choice["message"],
        "detail": None,
        "icon": "💡",
        "priority": 10,
    }


def generate_spending_detective_insights(
    txns: pd.DataFrame,
    as_of: Optional[date] = None,
) -> List[Dict]:
    """
    Generate Spending Pattern Detective insights.
    Helps users understand patterns in their spending.
    """
    as_of = as_of or TODAY
    insights = []

    # ── Top categories ───────────────────────────────────────────────
    month_start = as_of.replace(day=1)
    top_cats = get_top_spending_categories(txns, month_start, as_of)
    if top_cats:
        insights.append({
            "type": "top_categories",
            "title": "Your top spending categories this month",
            "data": top_cats,
            "icon": "📊",
        })

    # ── Weekend vs weekday ───────────────────────────────────────────
    wk_data = get_weekend_vs_weekday_spending(txns, month_start, as_of)
    if wk_data["weekday_avg"] > 0 or wk_data["weekend_avg"] > 0:
        insights.append({
            "type": "weekend_vs_weekday",
            "title": "Weekend vs weekday spending",
            "data": wk_data,
            "icon": "📅",
        })

    # ── Recurring expenses ───────────────────────────────────────────
    recurring = find_recurring_expenses(txns)
    if recurring:
        insights.append({
            "type": "recurring",
            "title": "Your recurring expenses",
            "data": recurring[:5],
            "icon": "🔄",
        })

    # ── Unusual patterns ─────────────────────────────────────────────
    unusual = detect_unusual_spending(txns, as_of=as_of)
    if unusual:
        insights.append({
            "type": "unusual",
            "title": "Unusual spending patterns",
            "data": unusual[:3],
            "icon": "🔍",
        })

    return insights
