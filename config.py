"""
Nance – Central configuration and constants.
"""

from pathlib import Path
from datetime import date

# ── Paths ────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"

# ── Date range for synthetic data ────────────────────────────────────
DATA_START_DATE = date(2026, 8, 1)
DATA_END_DATE = date(2026, 11, 23)  # "today" for the demo
TODAY = DATA_END_DATE

# ── Category taxonomy ────────────────────────────────────────────────
SPENDING_CATEGORIES = [
    "Food & Dining", "Groceries", "Shopping", "Bills",
    "Travel", "Transportation", "Fuel / EV Charging",
    "Entertainment", "Subscriptions", "Software Tools & Apps",
    "Housing & Utilities", "Rent", "Personal Care",
    "Hospitals & Pharmacy", "Fitness & Wellness", "Education",
    "Kids", "Pets", "Sports", "Gifts & Donations",
    "Electronics", "Vehicle", "Insurance Premiums", "Taxes",
    "Banking & Fees", "EMIs & Loans",
]

MONEY_MOVEMENT_CATEGORIES = [
    "Self Transfers", "Credit Card Payments",
    "Credit Card Settlements", "Investments (Outflow)",
    "Cash Withdrawals", "Lend", "Borrow", "Friends & Family",
]

INCOME_CATEGORIES = [
    "Salary & Allowances", "Refunds", "Cashback & Rewards",
    "Interest & Dividends", "Business Income", "Freelance",
    "Rental Income",
]

OTHER_CATEGORIES = ["Uncategorized", "Miscellaneous"]

ALL_CATEGORIES = (
    SPENDING_CATEGORIES
    + MONEY_MOVEMENT_CATEGORIES
    + INCOME_CATEGORIES
    + OTHER_CATEGORIES
)

# Categories that represent real spending (not money movement / income)
REAL_SPENDING_CATEGORIES = set(SPENDING_CATEGORIES)

# Categories to exclude from spending analysis
NON_SPENDING_CATEGORIES = set(
    MONEY_MOVEMENT_CATEGORIES + INCOME_CATEGORIES + OTHER_CATEGORIES
)

# ── Sub-categories ───────────────────────────────────────────────────
SUB_CATEGORIES = {
    "Food & Dining": ["Food Delivery", "Restaurants", "Cafes", "Street Food"],
    "Groceries": ["Supermarket", "Vegetables & Fruits", "Online Grocery"],
    "Shopping": ["Online Shopping", "Clothing", "Accessories", "Home Decor"],
    "Bills": ["Electricity", "Water", "Gas", "Internet", "Mobile Recharge"],
    "Travel": ["Flights", "Hotels", "Train", "Bus"],
    "Transportation": ["Auto / Cab", "Metro", "Bus Pass"],
    "Entertainment": ["Movies", "OTT Subscription", "Events", "Gaming"],
    "Subscriptions": ["Streaming", "News", "Cloud Storage", "Music"],
    "Personal Care": ["Salon", "Skincare", "Grooming"],
    "Hospitals & Pharmacy": ["Doctor Visit", "Medicines", "Lab Tests"],
    "Education": ["Courses", "Books", "Exam Fees"],
}

# ── Merchants ────────────────────────────────────────────────────────
MERCHANTS = {
    "Food Delivery": ["Swiggy", "Zomato"],
    "Restaurants": ["Barbeque Nation", "Dominos", "Local Restaurant"],
    "Cafes": ["Starbucks", "Third Wave Coffee", "Chai Point"],
    "Online Shopping": ["Amazon", "Flipkart", "Myntra", "Meesho"],
    "Supermarket": ["DMart", "BigBasket", "More Supermarket"],
    "Online Grocery": ["BigBasket", "Blinkit", "Zepto", "Swiggy Instamart"],
    "Auto / Cab": ["Ola", "Uber", "Rapido"],
    "Streaming": ["Netflix", "Hotstar", "Amazon Prime"],
    "Mobile Recharge": ["Jio", "Airtel", "Vi"],
    "Electricity": ["TSSPDCL", "BESCOM"],
}

# ── Payment modes ────────────────────────────────────────────────────
PAYMENT_MODES = ["UPI", "card", "netbanking", "cash", "auto-debit"]

# ── Transaction sources ──────────────────────────────────────────────
TRANSACTION_SOURCES = ["bank", "card", "sms", "email", "cash"]

# ── Currency ─────────────────────────────────────────────────────────
CURRENCY_SYMBOL = "₹"


def format_inr(amount: float) -> str:
    """Format amount in Indian Rupee style with commas."""
    if amount < 0:
        return f"-{CURRENCY_SYMBOL}{abs(amount):,.0f}"
    return f"{CURRENCY_SYMBOL}{amount:,.0f}"


# ── Challenge definitions ────────────────────────────────────────────
CHALLENGES = [
    {
        "id": "know_your_money",
        "name": "Know Your Money",
        "description": "Review your spending across 5 different categories",
        "target": 5,
        "unit": "categories reviewed",
        "icon": "📊",
    },
    {
        "id": "subscription_detective",
        "name": "Subscription Detective",
        "description": "Identify and review 3 recurring payments",
        "target": 3,
        "unit": "subscriptions reviewed",
        "icon": "🔍",
    },
    {
        "id": "weekend_explorer",
        "name": "Weekend Explorer",
        "description": "Reflect on your weekend spending for 3 weekends",
        "target": 3,
        "unit": "weekends reviewed",
        "icon": "🗓️",
    },
    {
        "id": "money_reflection",
        "name": "Money Reflection",
        "description": "Complete 7 daily money check-ins",
        "target": 7,
        "unit": "check-ins completed",
        "icon": "🪞",
    },
    {
        "id": "expense_awareness",
        "name": "Expense Awareness",
        "description": "Review your recent transactions 5 times",
        "target": 5,
        "unit": "reviews completed",
        "icon": "👁️",
    },
]

# ── Money Garden stages ──────────────────────────────────────────────
GARDEN_STAGES = [
    {"name": "Seed", "min_xp": 0, "emoji": "🌱"},
    {"name": "Sprout", "min_xp": 10, "emoji": "🌿"},
    {"name": "Sapling", "min_xp": 30, "emoji": "🌳"},
    {"name": "Bloom", "min_xp": 60, "emoji": "🌸"},
    {"name": "Garden", "min_xp": 100, "emoji": "🏡"},
]

# ── XP awards ────────────────────────────────────────────────────────
XP_DAILY_CHECKIN = 2
XP_CATEGORY_REVIEW = 1
XP_SUBSCRIPTION_REVIEW = 2
XP_CHALLENGE_COMPLETE = 5
XP_WEEKEND_REVIEW = 3
