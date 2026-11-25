"""
Nance – Comprehensive Test Suite

Tests for financial calculations, insight generation, budget handling,
user behaviour analysis, challenge progress, and edge cases.
"""

import pytest
import pandas as pd
from datetime import date, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from config import TODAY, REAL_SPENDING_CATEGORIES
from data_loader import DataLoader
from transaction_processor import (
    filter_real_spending, get_spending_by_category, get_total_spending,
    get_budget_status, find_recurring_expenses, get_top_spending_categories,
    get_weekend_vs_weekday_spending, detect_unusual_spending,
    get_daily_spending, get_payment_mode_breakdown,
)
from user_behaviour import (
    classify_user_engagement, is_quiet_money_day, get_current_streak,
    get_longest_streak, get_days_since_last_active,
    get_activity_rate, get_weekly_activity_summary,
)
from insight_generator import (
    generate_daily_money_moment, generate_spending_detective_insights,
)
from challenge_engine import (
    get_challenge_status, get_challenges_summary,
    get_garden_stage, get_garden_status, get_next_recommended_challenge,
)
from ai_layer import _validate_ai_message


# ══════════════════════════════════════════════════════════════════════
# FIXTURES
# ══════════════════════════════════════════════════════════════════════

@pytest.fixture
def loader():
    return DataLoader()


@pytest.fixture
def sample_transactions():
    """Create sample transaction DataFrame for testing."""
    return pd.DataFrame([
        {"txn_id": "T1", "user_id": "user_001", "txn_date": date(2026, 11, 20),
         "amount": 500, "transaction_type": "debit", "main_category": "Food & Dining",
         "sub_category": "Food Delivery", "merchant_name": "Swiggy",
         "payment_mode": "UPI", "source": "sms", "person_name": ""},
        {"txn_id": "T2", "user_id": "user_001", "txn_date": date(2026, 11, 20),
         "amount": 1200, "transaction_type": "debit", "main_category": "Shopping",
         "sub_category": "Online Shopping", "merchant_name": "Amazon",
         "payment_mode": "card", "source": "card", "person_name": ""},
        {"txn_id": "T3", "user_id": "user_001", "txn_date": date(2026, 11, 19),
         "amount": 300, "transaction_type": "debit", "main_category": "Transportation",
         "sub_category": "Auto / Cab", "merchant_name": "Uber",
         "payment_mode": "UPI", "source": "sms", "person_name": ""},
        {"txn_id": "T4", "user_id": "user_001", "txn_date": date(2026, 11, 20),
         "amount": 65000, "transaction_type": "credit", "main_category": "Salary & Allowances",
         "sub_category": "Salary", "merchant_name": "",
         "payment_mode": "netbanking", "source": "bank", "person_name": ""},
        {"txn_id": "T5", "user_id": "user_001", "txn_date": date(2026, 11, 20),
         "amount": 10000, "transaction_type": "debit", "main_category": "Self Transfers",
         "sub_category": "Self Transfers", "merchant_name": "",
         "payment_mode": "netbanking", "source": "bank", "person_name": ""},
        {"txn_id": "T6", "user_id": "user_001", "txn_date": date(2026, 11, 18),
         "amount": 500, "transaction_type": "debit", "main_category": "Food & Dining",
         "sub_category": "Food Delivery", "merchant_name": "Swiggy",
         "payment_mode": "UPI", "source": "sms", "person_name": ""},
        {"txn_id": "T7", "user_id": "user_001", "txn_date": date(2026, 11, 15),
         "amount": 500, "transaction_type": "debit", "main_category": "Food & Dining",
         "sub_category": "Food Delivery", "merchant_name": "Swiggy",
         "payment_mode": "UPI", "source": "sms", "person_name": ""},
    ])


@pytest.fixture
def sample_budgets():
    """Create sample budget DataFrame."""
    return pd.DataFrame([
        {"budget_id": "B1", "user_id": "user_001", "main_category": "ALL",
         "period_type": "monthly", "amount": 30000,
         "from_date": date(2026, 11, 1), "to_date": date(2026, 11, 30)},
        {"budget_id": "B2", "user_id": "user_001", "main_category": "Food & Dining",
         "period_type": "monthly", "amount": 5000,
         "from_date": date(2026, 11, 1), "to_date": date(2026, 11, 30)},
    ])


@pytest.fixture
def active_user_activity():
    """App activity for a highly active user."""
    dates = []
    d = date(2026, 11, 1)
    while d <= date(2026, 11, 23):
        dates.append({"user_id": "user_001", "date": d})
        d += timedelta(days=1)
    return pd.DataFrame(dates)


@pytest.fixture
def inactive_user_activity():
    """App activity for a user who hasn't opened for 10 days."""
    dates = []
    d = date(2026, 11, 1)
    while d <= date(2026, 11, 13):
        dates.append({"user_id": "user_001", "date": d})
        d += timedelta(days=1)
    return pd.DataFrame(dates)


@pytest.fixture
def empty_activity():
    """Empty app activity (new user)."""
    return pd.DataFrame(columns=["user_id", "date"])


@pytest.fixture
def sample_challenges():
    """Sample challenge progress."""
    return pd.DataFrame([
        {"user_id": "user_001", "challenge_id": "know_your_money",
         "challenge_name": "Know Your Money", "progress": 5, "target": 5,
         "started_on": "2026-09-01", "completed_on": "2026-10-15"},
        {"user_id": "user_001", "challenge_id": "subscription_detective",
         "challenge_name": "Subscription Detective", "progress": 2, "target": 3,
         "started_on": "2026-09-01", "completed_on": ""},
        {"user_id": "user_001", "challenge_id": "weekend_explorer",
         "challenge_name": "Weekend Explorer", "progress": 0, "target": 3,
         "started_on": "2026-09-01", "completed_on": ""},
        {"user_id": "user_001", "challenge_id": "money_reflection",
         "challenge_name": "Money Reflection", "progress": 7, "target": 7,
         "started_on": "2026-09-01", "completed_on": "2026-11-01"},
        {"user_id": "user_001", "challenge_id": "expense_awareness",
         "challenge_name": "Expense Awareness", "progress": 3, "target": 5,
         "started_on": "2026-09-01", "completed_on": ""},
    ])


# ══════════════════════════════════════════════════════════════════════
# TRANSACTION PROCESSING TESTS
# ══════════════════════════════════════════════════════════════════════

class TestFilterRealSpending:
    """Test that only real spending transactions are included."""

    def test_excludes_credits(self, sample_transactions):
        result = filter_real_spending(sample_transactions)
        assert all(r == "debit" for r in result["transaction_type"])

    def test_excludes_self_transfers(self, sample_transactions):
        result = filter_real_spending(sample_transactions)
        assert "Self Transfers" not in result["main_category"].values

    def test_excludes_salary(self, sample_transactions):
        result = filter_real_spending(sample_transactions)
        assert "Salary & Allowances" not in result["main_category"].values

    def test_includes_food_dining(self, sample_transactions):
        result = filter_real_spending(sample_transactions)
        assert "Food & Dining" in result["main_category"].values

    def test_includes_shopping(self, sample_transactions):
        result = filter_real_spending(sample_transactions)
        assert "Shopping" in result["main_category"].values

    def test_empty_dataframe(self):
        empty = pd.DataFrame()
        result = filter_real_spending(empty)
        assert result.empty


class TestSpendingByCategory:
    def test_basic_spending(self, sample_transactions):
        cats = get_spending_by_category(sample_transactions)
        assert "Food & Dining" in cats
        assert cats["Food & Dining"] == 1500  # 500 + 500 + 500

    def test_date_filtering(self, sample_transactions):
        cats = get_spending_by_category(
            sample_transactions,
            start_date=date(2026, 11, 20),
            end_date=date(2026, 11, 20),
        )
        assert cats.get("Food & Dining", 0) == 500

    def test_empty_transactions(self):
        empty = pd.DataFrame()
        assert get_spending_by_category(empty) == {}


class TestTotalSpending:
    def test_total_excludes_non_spending(self, sample_transactions):
        total = get_total_spending(sample_transactions)
        # Should include Food (1500) + Shopping (1200) + Transport (300) = 3000
        # Should exclude Salary (65000) and Self Transfer (10000)
        assert total == 3000

    def test_total_with_date_range(self, sample_transactions):
        total = get_total_spending(
            sample_transactions,
            start_date=date(2026, 11, 20),
            end_date=date(2026, 11, 20),
        )
        assert total == 1700  # 500 (food) + 1200 (shopping)


class TestBudgetStatus:
    def test_budget_calculation(self, sample_transactions, sample_budgets):
        statuses = get_budget_status(
            sample_transactions, sample_budgets,
            as_of=date(2026, 11, 20),
        )
        assert len(statuses) > 0

    def test_overall_budget(self, sample_transactions, sample_budgets):
        statuses = get_budget_status(
            sample_transactions, sample_budgets,
            as_of=date(2026, 11, 20),
        )
        overall = [s for s in statuses if s["category"] == "ALL"]
        assert len(overall) == 1
        assert overall[0]["spent"] > 0

    def test_category_budget(self, sample_transactions, sample_budgets):
        statuses = get_budget_status(
            sample_transactions, sample_budgets,
            as_of=date(2026, 11, 20),
        )
        food = [s for s in statuses if s["category"] == "Food & Dining"]
        assert len(food) == 1

    def test_empty_budgets(self, sample_transactions):
        empty = pd.DataFrame()
        assert get_budget_status(sample_transactions, empty) == []

    def test_budget_status_values(self, sample_transactions, sample_budgets):
        statuses = get_budget_status(
            sample_transactions, sample_budgets,
            as_of=date(2026, 11, 20),
        )
        for s in statuses:
            assert s["status"] in ("healthy", "on_track", "warning", "exceeded")
            assert s["spent"] >= 0
            assert s["limit"] > 0
            assert 0 <= s["days_remaining"]


class TestRecurringExpenses:
    def test_finds_recurring_swiggy(self, sample_transactions):
        recurring = find_recurring_expenses(sample_transactions, min_occurrences=2)
        swiggy = [r for r in recurring if r["merchant"] == "Swiggy"]
        assert len(swiggy) == 1
        assert swiggy[0]["occurrences"] >= 2

    def test_empty_transactions(self):
        empty = pd.DataFrame()
        assert find_recurring_expenses(empty) == []


class TestDailySpending:
    def test_daily_amounts(self, sample_transactions):
        daily = get_daily_spending(sample_transactions)
        assert date(2026, 11, 20) in daily
        assert daily[date(2026, 11, 20)] == 1700  # 500 + 1200


class TestWeekendWeekday:
    def test_comparison(self, sample_transactions):
        result = get_weekend_vs_weekday_spending(sample_transactions)
        assert "weekday_avg" in result
        assert "weekend_avg" in result
        assert "ratio" in result


# ══════════════════════════════════════════════════════════════════════
# USER BEHAVIOUR TESTS
# ══════════════════════════════════════════════════════════════════════

class TestUserEngagement:
    def test_active_user(self, active_user_activity):
        result = classify_user_engagement(active_user_activity, date(2026, 11, 23))
        assert result["engagement_level"] in ("highly_active", "active")
        assert not result["needs_comeback"]
        assert not result["is_new_user"]

    def test_inactive_user(self, inactive_user_activity):
        result = classify_user_engagement(inactive_user_activity, date(2026, 11, 23))
        assert result["needs_comeback"] is True
        assert result["days_inactive"] == 10

    def test_new_user(self, empty_activity):
        result = classify_user_engagement(empty_activity, date(2026, 11, 23))
        assert result["is_new_user"] is True
        assert result["engagement_level"] == "new"

    def test_lapsing_user(self):
        """User who was active 4 days ago."""
        dates = [{"user_id": "u", "date": date(2026, 11, 19)}]
        activity = pd.DataFrame(dates)
        result = classify_user_engagement(activity, date(2026, 11, 23))
        assert result["engagement_level"] == "lapsing"
        assert result["needs_comeback"] is True


class TestQuietMoneyDay:
    def test_no_transactions(self):
        empty = pd.DataFrame(columns=[
            "txn_id", "user_id", "txn_date", "amount",
            "transaction_type", "main_category",
        ])
        result = is_quiet_money_day(empty, date(2026, 11, 23))
        assert result["is_quiet"] is True
        assert result["is_verified_no_spend"] is False

    def test_has_spending(self, sample_transactions):
        result = is_quiet_money_day(sample_transactions, date(2026, 11, 20))
        assert result["is_quiet"] is False
        assert result["has_transactions"] is True

    def test_only_credits(self):
        """Day with only credit transactions."""
        txns = pd.DataFrame([
            {"txn_id": "T1", "user_id": "u", "txn_date": date(2026, 11, 23),
             "amount": 65000, "transaction_type": "credit",
             "main_category": "Salary & Allowances"},
        ])
        result = is_quiet_money_day(txns, date(2026, 11, 23))
        assert result["is_quiet"] is True
        assert result["reason"] == "only_non_spending"

    def test_no_transactions_on_date(self, sample_transactions):
        """No transactions on a specific date but data exists."""
        result = is_quiet_money_day(sample_transactions, date(2026, 11, 22))
        assert result["is_quiet"] is True
        assert result["has_transactions"] is False


class TestStreak:
    def test_active_streak(self, active_user_activity):
        streak = get_current_streak(active_user_activity, date(2026, 11, 23))
        assert streak >= 1

    def test_broken_streak(self, inactive_user_activity):
        streak = get_current_streak(inactive_user_activity, date(2026, 11, 23))
        assert streak == 0

    def test_empty_streak(self, empty_activity):
        streak = get_current_streak(empty_activity)
        assert streak == 0

    def test_longest_streak(self, active_user_activity):
        longest = get_longest_streak(active_user_activity)
        assert longest >= 1


class TestActivityRate:
    def test_full_activity(self, active_user_activity):
        rate = get_activity_rate(active_user_activity, date(2026, 11, 1), date(2026, 11, 23))
        assert rate == 100.0

    def test_no_activity(self, empty_activity):
        rate = get_activity_rate(empty_activity)
        assert rate == 0.0


# ══════════════════════════════════════════════════════════════════════
# INSIGHT GENERATION TESTS
# ══════════════════════════════════════════════════════════════════════

class TestDailyMoneyMoment:
    def test_comeback_for_inactive_user(self, sample_transactions, sample_budgets, inactive_user_activity):
        moment = generate_daily_money_moment(
            sample_transactions, sample_budgets,
            inactive_user_activity, date(2026, 11, 23),
        )
        assert moment["type"] == "comeback"
        assert "welcome" in moment["title"].lower() or "back" in moment["title"].lower() or "good" in moment["title"].lower()

    def test_new_user_moment(self, sample_transactions, sample_budgets, empty_activity):
        moment = generate_daily_money_moment(
            sample_transactions, sample_budgets,
            empty_activity, date(2026, 11, 23),
        )
        assert moment["type"] == "new_user"

    def test_has_required_fields(self, sample_transactions, sample_budgets, active_user_activity):
        moment = generate_daily_money_moment(
            sample_transactions, sample_budgets,
            active_user_activity, date(2026, 11, 23),
        )
        assert "type" in moment
        assert "title" in moment
        assert "message" in moment
        assert "icon" in moment

    def test_moment_never_shames(self, sample_transactions, sample_budgets, active_user_activity):
        moment = generate_daily_money_moment(
            sample_transactions, sample_budgets,
            active_user_activity, date(2026, 11, 23),
        )
        shame_words = ["bad", "terrible", "wasteful", "irresponsible", "failed"]
        message = moment["message"].lower()
        for word in shame_words:
            assert word not in message, f"Moment message contains shaming word: {word}"


class TestSpendingDetective:
    def test_generates_insights(self, sample_transactions):
        insights = generate_spending_detective_insights(sample_transactions, date(2026, 11, 23))
        assert isinstance(insights, list)

    def test_insight_types(self, sample_transactions):
        insights = generate_spending_detective_insights(sample_transactions, date(2026, 11, 23))
        valid_types = {"top_categories", "weekend_vs_weekday", "recurring", "unusual"}
        for insight in insights:
            assert insight["type"] in valid_types


# ══════════════════════════════════════════════════════════════════════
# CHALLENGE ENGINE TESTS
# ══════════════════════════════════════════════════════════════════════

class TestChallenges:
    def test_challenge_count(self, sample_challenges):
        statuses = get_challenge_status(sample_challenges)
        assert len(statuses) == 5

    def test_completed_challenge(self, sample_challenges):
        statuses = get_challenge_status(sample_challenges)
        know = [s for s in statuses if s["id"] == "know_your_money"]
        assert len(know) == 1
        assert know[0]["is_complete"] is True
        assert know[0]["percentage"] == 100

    def test_in_progress_challenge(self, sample_challenges):
        statuses = get_challenge_status(sample_challenges)
        sub = [s for s in statuses if s["id"] == "subscription_detective"]
        assert sub[0]["status"] == "in_progress"
        assert sub[0]["progress"] == 2
        assert sub[0]["target"] == 3

    def test_not_started_challenge(self, sample_challenges):
        statuses = get_challenge_status(sample_challenges)
        wk = [s for s in statuses if s["id"] == "weekend_explorer"]
        assert wk[0]["status"] == "not_started"

    def test_summary(self, sample_challenges):
        summary = get_challenges_summary(sample_challenges)
        assert summary["completed"] == 2
        assert summary["in_progress"] == 2
        assert summary["not_started"] == 1
        assert summary["total"] == 5

    def test_empty_challenges(self):
        empty = pd.DataFrame()
        statuses = get_challenge_status(empty)
        assert len(statuses) == 5
        assert all(s["progress"] == 0 for s in statuses)

    def test_next_recommended(self, sample_challenges):
        rec = get_next_recommended_challenge(sample_challenges)
        assert rec is not None
        assert rec["status"] == "in_progress"


class TestGarden:
    def test_seed_stage(self):
        stage = get_garden_stage(0)
        assert stage["stage_name"] == "Seed"

    def test_sprout_stage(self):
        stage = get_garden_stage(15)
        assert stage["stage_name"] == "Sprout"

    def test_garden_stage(self):
        stage = get_garden_stage(120)
        assert stage["stage_name"] == "Garden"
        assert stage["next_stage"] is None

    def test_progress_to_next(self):
        stage = get_garden_stage(20)  # Sprout (10-29)
        assert stage["stage_name"] == "Sprout"
        assert stage["next_stage"] == "Sapling"
        assert 0 <= stage["progress_to_next"] <= 100

    def test_garden_status(self):
        data = {
            "user_id": "u", "total_xp": 65,
            "checkins": 30, "category_reviews": 10,
            "challenges_completed": 3,
        }
        status = get_garden_status(data)
        assert status["stage"]["stage_name"] == "Bloom"
        assert len(status["activities"]) > 0

    def test_garden_status_none(self):
        status = get_garden_status(None)
        assert status["total_xp"] == 0
        assert status["stage"]["stage_name"] == "Seed"


# ══════════════════════════════════════════════════════════════════════
# AI LAYER TESTS
# ══════════════════════════════════════════════════════════════════════

class TestAIValidation:
    def test_accepts_kind_message(self):
        assert _validate_ai_message("Great job staying on track this week!") is True

    def test_rejects_shaming_message(self):
        assert _validate_ai_message("You are irresponsible with money.") is False

    def test_rejects_spending_encouragement(self):
        assert _validate_ai_message("You deserve to shop! Treat yourself!") is False

    def test_rejects_comparison(self):
        assert _validate_ai_message("You are worse than other users.") is False

    def test_accepts_normal_insight(self):
        assert _validate_ai_message(
            "Your food spending is up 20% this week. Worth noticing."
        ) is True


# ══════════════════════════════════════════════════════════════════════
# DATA LOADER INTEGRATION TESTS
# ══════════════════════════════════════════════════════════════════════

class TestDataLoader:
    def test_loads_users(self, loader):
        users = loader.users
        assert len(users) == 5
        assert "Sneha" in users["name"].values

    def test_loads_transactions(self, loader):
        txns = loader.transactions
        assert len(txns) > 0
        assert "txn_id" in txns.columns

    def test_loads_budgets(self, loader):
        budgets = loader.budgets
        assert len(budgets) > 0

    def test_user_spending_filter(self, loader):
        spending = loader.get_user_spending("user_001")
        if not spending.empty:
            assert all(spending["transaction_type"] == "debit")
            assert all(c in REAL_SPENDING_CATEGORIES for c in spending["main_category"])

    def test_get_user_name_map(self, loader):
        name_map = loader.get_user_name_map()
        assert name_map["user_001"] == "Sneha"
        assert name_map["user_002"] == "Hari"

    def test_nonexistent_user(self, loader):
        assert loader.get_user("user_999") is None


# ══════════════════════════════════════════════════════════════════════
# EDGE CASE TESTS
# ══════════════════════════════════════════════════════════════════════

class TestEdgeCases:
    def test_credit_card_payment_excluded(self, loader):
        """Credit card payments should not count as spending."""
        txns = loader.get_user_transactions("user_001")
        spending = filter_real_spending(txns)
        assert "Credit Card Payments" not in spending["main_category"].values

    def test_self_transfer_excluded(self, loader):
        """Self transfers should not count as spending."""
        txns = loader.get_user_transactions("user_003")
        spending = filter_real_spending(txns)
        assert "Self Transfers" not in spending["main_category"].values

    def test_refund_excluded_from_spending(self, loader):
        """Refunds (credits) should not count as spending."""
        txns = loader.get_user_transactions("user_001")
        spending = filter_real_spending(txns)
        assert "Refunds" not in spending["main_category"].values

    def test_uncategorized_excluded(self, loader):
        """Uncategorized transactions should not count as spending."""
        txns = loader.get_user_transactions("user_002")
        spending = filter_real_spending(txns)
        assert "Uncategorized" not in spending["main_category"].values

    def test_investment_excluded(self, loader):
        """Investment outflows should not count as spending."""
        txns = loader.get_user_transactions("user_005")
        spending = filter_real_spending(txns)
        assert "Investments (Outflow)" not in spending["main_category"].values

    def test_no_budget_user(self, loader):
        """Pallavi (minimal) has no budgets."""
        budgets = loader.get_user_budgets("user_004")
        assert budgets.empty

    def test_zero_amount_handling(self):
        """Handle zero or missing amounts gracefully."""
        txns = pd.DataFrame([
            {"txn_id": "T1", "user_id": "u", "txn_date": date(2026, 11, 20),
             "amount": 0, "transaction_type": "debit",
             "main_category": "Food & Dining", "sub_category": "",
             "merchant_name": "", "payment_mode": "UPI",
             "source": "sms", "person_name": ""},
        ])
        total = get_total_spending(txns)
        assert total == 0

    def test_returning_user_scenario(self, loader):
        """Sravani should have an inactive period."""
        activity = loader.get_user_app_activity("user_003")
        dates = set(activity["date"].tolist())
        # Should have no activity between Oct 20 and Nov 3
        for d_offset in range(0, 15):
            check = date(2026, 10, 20) + timedelta(days=d_offset)
            if check <= date(2026, 11, 3):
                assert check not in dates, f"Sravani should be inactive on {check}"

    def test_minimal_user_scenario(self, loader):
        """Pallavi should have very few transactions."""
        txns = loader.get_user_transactions("user_004")
        # Pallavi joined Sep 20, so no txns before that
        early_txns = txns[txns["txn_date"] < date(2026, 9, 20)]
        assert len(early_txns) == 0


class TestUserScenarios:
    """Test all 5 user scenarios work end-to-end."""

    def test_sneha_disciplined(self, loader):
        """Sneha: regular, disciplined user."""
        txns = loader.get_user_transactions("user_001")
        activity = loader.get_user_app_activity("user_001")
        assert len(txns) > 50
        assert len(activity) > 50  # Very active

    def test_hari_overspender(self, loader):
        """Hari: overspends on food delivery."""
        txns = loader.get_user_transactions("user_002")
        food = txns[txns["main_category"] == "Food & Dining"]
        other = txns[txns["main_category"] != "Food & Dining"]
        spending = filter_real_spending(txns)
        # Food should be a major category for Hari
        if not spending.empty and not food.empty:
            food_pct = food[food["transaction_type"] == "debit"]["amount"].sum() / \
                       spending["amount"].sum() * 100
            assert food_pct > 20  # Food is significant for Hari

    def test_sravani_returning(self, loader):
        """Sravani: returned after inactivity."""
        activity = loader.get_user_app_activity("user_003")
        # Should have activity before and after the gap
        before = activity[activity["date"] < date(2026, 10, 20)]
        after = activity[activity["date"] > date(2026, 11, 3)]
        assert len(before) > 0
        assert len(after) > 0

    def test_pallavi_minimal(self, loader):
        """Pallavi: minimal engagement."""
        activity = loader.get_user_app_activity("user_004")
        txns = loader.get_user_transactions("user_004")
        # Should have far fewer transactions than others
        sneha_txns = loader.get_user_transactions("user_001")
        assert len(txns) < len(sneha_txns)

    def test_srujith_challenger(self, loader):
        """Srujith: active challenge completer."""
        challenges = loader.get_user_challenges("user_005")
        completed = challenges[challenges["progress"] >= challenges["target"]]
        assert len(completed) > 0  # Should have completed at least one


# ══════════════════════════════════════════════════════════════════════
# CONFIG AND FORMATTING TESTS
# ══════════════════════════════════════════════════════════════════════

class TestFormatting:
    def test_format_inr(self):
        from config import format_inr
        assert format_inr(1000) == "₹1,000"
        assert format_inr(50000) == "₹50,000"
        assert format_inr(0) == "₹0"

    def test_format_inr_negative(self):
        from config import format_inr
        assert format_inr(-500) == "-₹500"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
