"""
Nance – Synthetic Data Generator

Generates realistic Indian personal finance data for 5 demo users.
Reproducible via fixed random seed.

Usage: python generate_data.py
"""

import random
import csv
import os
from datetime import date, datetime, timedelta, time
from pathlib import Path
import uuid

# Fixed seed for reproducibility
random.seed(42)

# ── Paths ────────────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

START_DATE = date(2026, 8, 1)
END_DATE = date(2026, 11, 23)

# ── Category taxonomy (from assignment) ──────────────────────────────────
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

MONEY_MOVEMENT = [
    "Self Transfers", "Credit Card Payments",
    "Credit Card Settlements", "Investments (Outflow)",
    "Cash Withdrawals", "Lend", "Borrow", "Friends & Family",
]

INCOME_CATEGORIES = [
    "Salary & Allowances", "Refunds", "Cashback & Rewards",
    "Interest & Dividends", "Business Income", "Freelance",
    "Rental Income",
]

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

MERCHANTS = {
    "Food Delivery": ["Swiggy", "Zomato"],
    "Restaurants": ["Barbeque Nation", "Dominos", "Haldirams", "Local Restaurant"],
    "Cafes": ["Starbucks", "Third Wave Coffee", "Chai Point"],
    "Online Shopping": ["Amazon", "Flipkart", "Myntra", "Meesho"],
    "Supermarket": ["DMart", "More Supermarket", "Reliance Fresh"],
    "Online Grocery": ["BigBasket", "Blinkit", "Zepto", "Swiggy Instamart"],
    "Auto / Cab": ["Ola", "Uber", "Rapido"],
    "Streaming": ["Netflix", "Hotstar", "Amazon Prime", "Spotify"],
    "Mobile Recharge": ["Jio", "Airtel", "Vi"],
    "Electricity": ["TSSPDCL", "BESCOM", "MSEDCL"],
    "Flights": ["IndiGo", "Air India", "SpiceJet"],
    "Train": ["IRCTC"],
}

PAYMENT_MODES = ["UPI", "card", "netbanking", "cash", "auto-debit"]
SOURCES = ["bank", "card", "sms", "email", "cash"]

PERSON_NAMES = [
    "Ravi", "Priya", "Kiran", "Anitha", "Deepak",
    "Meena", "Suresh", "Lakshmi",
]


def generate_txn_id():
    return f"TXN-{uuid.uuid4().hex[:12].upper()}"


def random_time():
    h = random.choices(range(24), weights=[
        1, 1, 1, 1, 1, 2, 3, 5, 8, 10, 10, 8,
        7, 6, 5, 5, 6, 8, 10, 12, 10, 8, 5, 2,
    ])[0]
    m = random.randint(0, 59)
    s = random.randint(0, 59)
    return time(h, m, s)


def arrived_delay(txn_date, txn_time_obj, source):
    """Simulate delayed arrival of transaction data."""
    base = datetime.combine(txn_date, txn_time_obj)
    if source == "sms":
        delay = timedelta(minutes=random.randint(1, 30))
    elif source == "email":
        delay = timedelta(hours=random.randint(1, 48))
    elif source == "bank":
        delay = timedelta(hours=random.randint(0, 6))
    elif source == "card":
        delay = timedelta(hours=random.randint(0, 4))
    else:
        delay = timedelta(hours=random.randint(0, 24))
    return base + delay


def pick_payment_mode(category, sub_cat):
    if sub_cat in ["Streaming", "Music", "Cloud Storage", "News"]:
        return "auto-debit"
    if sub_cat in ["Auto / Cab", "Food Delivery", "Online Shopping", "Online Grocery"]:
        return random.choice(["UPI", "card"])
    if category == "Rent":
        return random.choice(["netbanking", "UPI"])
    if sub_cat == "Street Food":
        return random.choice(["UPI", "cash"])
    return random.choice(PAYMENT_MODES)


def pick_source(payment_mode):
    if payment_mode == "card":
        return random.choice(["card", "sms"])
    if payment_mode == "UPI":
        return random.choice(["bank", "sms"])
    if payment_mode == "auto-debit":
        return random.choice(["bank", "email"])
    if payment_mode == "cash":
        return "cash"
    return random.choice(SOURCES)


# ── User profiles ────────────────────────────────────────────────────────

USERS = [
    {
        "user_id": "user_001",
        "name": "Sneha",
        "city": "Hyderabad",
        "joined_on": "2026-05-15",
        "profile": "disciplined",
    },
    {
        "user_id": "user_002",
        "name": "Hari",
        "city": "Bangalore",
        "joined_on": "2026-06-01",
        "profile": "overspender",
    },
    {
        "user_id": "user_003",
        "name": "Sravani",
        "city": "Chennai",
        "joined_on": "2026-07-10",
        "profile": "returning",
    },
    {
        "user_id": "user_004",
        "name": "Pallavi",
        "city": "Mumbai",
        "joined_on": "2026-09-20",
        "profile": "minimal",
    },
    {
        "user_id": "user_005",
        "name": "Srujith",
        "city": "Pune",
        "joined_on": "2026-06-15",
        "profile": "challenger",
    },
]


def generate_spending_txns_for_day(user, d):
    """Generate spending transactions for a user on a given day."""
    txns = []
    profile = user["profile"]
    is_weekend = d.weekday() >= 5

    if profile == "disciplined":
        n_txns = random.choices([0, 1, 2, 3], weights=[5, 40, 35, 20])[0]
        cats_weights = {
            "Food & Dining": 25, "Groceries": 15, "Transportation": 15,
            "Bills": 10, "Shopping": 10, "Entertainment": 5,
            "Subscriptions": 5, "Personal Care": 5, "Education": 5,
            "Hospitals & Pharmacy": 3, "Fitness & Wellness": 2,
        }
        amount_range = (50, 2000)

    elif profile == "overspender":
        n_txns = random.choices([1, 2, 3, 4, 5], weights=[10, 25, 30, 25, 10])[0]
        cats_weights = {
            "Food & Dining": 45, "Shopping": 15, "Entertainment": 15,
            "Transportation": 10, "Groceries": 5, "Bills": 5,
            "Subscriptions": 3, "Electronics": 2,
        }
        amount_range = (80, 3500)

    elif profile == "returning":
        inactive_start = date(2026, 10, 20)
        inactive_end = date(2026, 11, 3)
        if inactive_start <= d <= inactive_end:
            n_txns = random.choices([0, 1], weights=[60, 40])[0]
        else:
            n_txns = random.choices([0, 1, 2, 3], weights=[10, 35, 35, 20])[0]
        cats_weights = {
            "Food & Dining": 20, "Groceries": 20, "Shopping": 15,
            "Bills": 10, "Transportation": 10, "Entertainment": 10,
            "Personal Care": 5, "Hospitals & Pharmacy": 5,
            "Education": 5,
        }
        amount_range = (40, 2500)

    elif profile == "minimal":
        if d < date(2026, 9, 20):
            return []  # Not joined yet
        n_txns = random.choices([0, 0, 0, 1, 1, 2], weights=[30, 25, 15, 15, 10, 5])[0]
        cats_weights = {
            "Food & Dining": 25, "Bills": 20, "Transportation": 15,
            "Groceries": 15, "Shopping": 10, "Personal Care": 10,
            "Subscriptions": 5,
        }
        amount_range = (30, 1500)

    elif profile == "challenger":
        if is_weekend:
            n_txns = random.choices([2, 3, 4, 5], weights=[15, 30, 35, 20])[0]
        else:
            n_txns = random.choices([0, 1, 2, 3], weights=[10, 30, 40, 20])[0]
        cats_weights = {
            "Food & Dining": 20, "Entertainment": 20, "Shopping": 15,
            "Transportation": 10, "Groceries": 10, "Subscriptions": 10,
            "Fitness & Wellness": 5, "Sports": 5, "Travel": 5,
        }
        amount_range = (60, 3000)
    else:
        return []

    cats = list(cats_weights.keys())
    weights = list(cats_weights.values())

    for _ in range(n_txns):
        cat = random.choices(cats, weights=weights)[0]
        sub_cats = SUB_CATEGORIES.get(cat, [cat])
        sub_cat = random.choice(sub_cats)

        # Amount varies by category
        if cat == "Rent":
            amount = random.choice([8000, 10000, 12000, 15000])
        elif cat in ("Bills", "EMIs & Loans"):
            amount = random.randint(200, 5000)
        elif cat == "Subscriptions":
            amount = random.choice([149, 199, 299, 499, 799])
        elif sub_cat == "Food Delivery":
            amount = random.randint(150, 800)
            if profile == "overspender":
                amount = random.randint(250, 1200)
        elif sub_cat in ("Flights", "Hotels"):
            amount = random.randint(2000, 15000)
        elif sub_cat == "Auto / Cab":
            amount = random.randint(50, 500)
        else:
            lo, hi = amount_range
            amount = random.randint(lo, hi)

        # Merchant
        merchant = None
        if sub_cat in MERCHANTS:
            merchant = random.choice(MERCHANTS[sub_cat])

        pm = pick_payment_mode(cat, sub_cat)
        src = pick_source(pm)
        t = random_time()

        txns.append({
            "txn_id": generate_txn_id(),
            "user_id": user["user_id"],
            "txn_date": d.isoformat(),
            "txn_time": t.strftime("%H:%M:%S"),
            "amount": amount,
            "transaction_type": "debit",
            "payment_mode": pm,
            "main_category": cat,
            "sub_category": sub_cat,
            "merchant_name": merchant or "",
            "person_name": "",
            "source": src,
            "arrived_at": arrived_delay(d, t, src).strftime("%Y-%m-%d %H:%M:%S"),
        })

    return txns


def generate_monthly_fixed(user, month_start):
    """Generate monthly fixed expenses: rent, salary, subscriptions."""
    txns = []
    uid = user["user_id"]
    profile = user["profile"]

    # Salary (credit) on 1st of month
    if profile != "minimal":
        salary = {
            "disciplined": 65000, "overspender": 55000,
            "returning": 48000, "challenger": 72000,
        }.get(profile, 50000)
        t = time(9, 0, 0)
        txns.append({
            "txn_id": generate_txn_id(),
            "user_id": uid,
            "txn_date": month_start.isoformat(),
            "txn_time": t.strftime("%H:%M:%S"),
            "amount": salary,
            "transaction_type": "credit",
            "payment_mode": "netbanking",
            "main_category": "Salary & Allowances",
            "sub_category": "Salary",
            "merchant_name": "",
            "person_name": "",
            "source": "bank",
            "arrived_at": datetime.combine(month_start, t).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        })
    else:
        # Pallavi joined Sep 20, so no salary before that
        if month_start >= date(2026, 9, 20) and random.random() > 0.3:
            txns.append({
                "txn_id": generate_txn_id(),
                "user_id": uid,
                "txn_date": month_start.isoformat(),
                "txn_time": "09:30:00",
                "amount": 35000,
                "transaction_type": "credit",
                "payment_mode": "netbanking",
                "main_category": "Salary & Allowances",
                "sub_category": "Salary",
                "merchant_name": "",
                "person_name": "",
                "source": "bank",
                "arrived_at": f"{month_start.isoformat()} 09:30:00",
            })

    # Rent on 5th (if applicable)
    rent_day = month_start.replace(day=5)
    if rent_day <= END_DATE and profile in (
        "disciplined", "overspender", "returning", "challenger"
    ):
        rent = {
            "disciplined": 12000, "overspender": 15000,
            "returning": 10000, "challenger": 14000,
        }[profile]
        txns.append({
            "txn_id": generate_txn_id(),
            "user_id": uid,
            "txn_date": rent_day.isoformat(),
            "txn_time": "10:00:00",
            "amount": rent,
            "transaction_type": "debit",
            "payment_mode": "netbanking",
            "main_category": "Rent",
            "sub_category": "Rent",
            "merchant_name": "",
            "person_name": "",
            "source": "bank",
            "arrived_at": f"{rent_day.isoformat()} 10:30:00",
        })

    # Subscriptions (auto-debit around 10th)
    sub_day = month_start.replace(day=min(10, 28))
    if sub_day <= END_DATE:
        subs = []
        if profile in ("disciplined", "challenger", "overspender"):
            subs = [("Netflix", 649), ("Spotify", 119)]
        if profile == "overspender":
            subs.append(("Hotstar", 299))
            subs.append(("Amazon Prime", 179))
        if profile == "challenger":
            subs.append(("YouTube Premium", 149))
        if profile == "returning":
            subs = [("Netflix", 649)]

        for sname, samt in subs:
            txns.append({
                "txn_id": generate_txn_id(),
                "user_id": uid,
                "txn_date": sub_day.isoformat(),
                "txn_time": "06:00:00",
                "amount": samt,
                "transaction_type": "debit",
                "payment_mode": "auto-debit",
                "main_category": "Subscriptions",
                "sub_category": "Streaming",
                "merchant_name": sname,
                "person_name": "",
                "source": "bank",
                "arrived_at": f"{sub_day.isoformat()} 06:15:00",
            })

    # Credit card payment around 15th (money movement, not real spending)
    cc_day = month_start.replace(day=min(15, 28))
    if cc_day <= END_DATE and profile in (
        "disciplined", "overspender", "challenger"
    ):
        cc_amount = {
            "disciplined": 8000, "overspender": 18000, "challenger": 12000,
        }[profile]
        txns.append({
            "txn_id": generate_txn_id(),
            "user_id": uid,
            "txn_date": cc_day.isoformat(),
            "txn_time": "11:00:00",
            "amount": cc_amount,
            "transaction_type": "debit",
            "payment_mode": "netbanking",
            "main_category": "Credit Card Payments",
            "sub_category": "Credit Card Payments",
            "merchant_name": "",
            "person_name": "",
            "source": "bank",
            "arrived_at": f"{cc_day.isoformat()} 11:15:00",
        })

    return txns


def generate_edge_case_txns(user):
    """Generate edge-case transactions."""
    txns = []
    uid = user["user_id"]
    profile = user["profile"]

    # Refund for Sneha
    if profile == "disciplined":
        txns.append({
            "txn_id": generate_txn_id(),
            "user_id": uid,
            "txn_date": "2026-10-15",
            "txn_time": "14:30:00",
            "amount": 1299,
            "transaction_type": "credit",
            "payment_mode": "UPI",
            "main_category": "Refunds",
            "sub_category": "Refunds",
            "merchant_name": "Amazon",
            "person_name": "",
            "source": "sms",
            "arrived_at": "2026-10-15 14:45:00",
        })

    # Missing category for Hari
    if profile == "overspender":
        txns.append({
            "txn_id": generate_txn_id(),
            "user_id": uid,
            "txn_date": "2026-11-05",
            "txn_time": "19:30:00",
            "amount": 2500,
            "transaction_type": "debit",
            "payment_mode": "UPI",
            "main_category": "Uncategorized",
            "sub_category": "",
            "merchant_name": "",
            "person_name": "",
            "source": "sms",
            "arrived_at": "2026-11-05 19:45:00",
        })

    # Self transfer for Sravani
    if profile == "returning":
        txns.append({
            "txn_id": generate_txn_id(),
            "user_id": uid,
            "txn_date": "2026-09-20",
            "txn_time": "10:00:00",
            "amount": 20000,
            "transaction_type": "debit",
            "payment_mode": "netbanking",
            "main_category": "Self Transfers",
            "sub_category": "Self Transfers",
            "merchant_name": "",
            "person_name": "",
            "source": "bank",
            "arrived_at": "2026-09-20 10:30:00",
        })

    # P2P for Srujith
    if profile == "challenger":
        for pname in ["Ravi", "Priya"]:
            txns.append({
                "txn_id": generate_txn_id(),
                "user_id": uid,
                "txn_date": "2026-10-25",
                "txn_time": "20:00:00",
                "amount": random.randint(500, 2000),
                "transaction_type": "debit",
                "payment_mode": "UPI",
                "main_category": "Friends & Family",
                "sub_category": "Friends & Family",
                "merchant_name": "",
                "person_name": pname,
                "source": "sms",
                "arrived_at": "2026-10-25 20:15:00",
            })

    # Cashback for Sneha
    if profile == "disciplined":
        txns.append({
            "txn_id": generate_txn_id(),
            "user_id": uid,
            "txn_date": "2026-11-01",
            "txn_time": "12:00:00",
            "amount": 150,
            "transaction_type": "credit",
            "payment_mode": "UPI",
            "main_category": "Cashback & Rewards",
            "sub_category": "Cashback & Rewards",
            "merchant_name": "Paytm",
            "person_name": "",
            "source": "sms",
            "arrived_at": "2026-11-01 12:10:00",
        })

    # Investment for Srujith
    if profile == "challenger":
        txns.append({
            "txn_id": generate_txn_id(),
            "user_id": uid,
            "txn_date": "2026-09-05",
            "txn_time": "09:00:00",
            "amount": 5000,
            "transaction_type": "debit",
            "payment_mode": "netbanking",
            "main_category": "Investments (Outflow)",
            "sub_category": "Investments (Outflow)",
            "merchant_name": "Groww",
            "person_name": "",
            "source": "bank",
            "arrived_at": "2026-09-05 09:30:00",
        })

    return txns


def generate_transactions():
    """Generate all transactions for all users."""
    all_txns = []

    for user in USERS:
        d = START_DATE
        while d <= END_DATE:
            all_txns.extend(generate_spending_txns_for_day(user, d))
            d += timedelta(days=1)

        # Monthly fixed expenses
        for m in range(8, 12):  # Aug to Nov
            month_start = date(2026, m, 1)
            if month_start <= END_DATE:
                all_txns.extend(generate_monthly_fixed(user, month_start))

        # Edge cases
        all_txns.extend(generate_edge_case_txns(user))

    all_txns.sort(key=lambda t: (t["txn_date"], t["txn_time"]))
    return all_txns


def generate_budgets():
    """Generate budget data."""
    budgets = []
    bid = 0

    for user in USERS:
        uid = user["user_id"]
        profile = user["profile"]

        if profile == "minimal":
            continue

        for m in range(8, 12):
            bid += 1
            month_start = date(2026, m, 1)
            if m == 11:
                month_end = date(2026, 11, 30)
            else:
                month_end = date(2026, m + 1, 1) - timedelta(days=1)

            overall = {
                "disciplined": 30000, "overspender": 25000,
                "returning": 22000, "challenger": 35000,
            }[profile]

            budgets.append({
                "budget_id": f"BDG-{bid:04d}",
                "user_id": uid,
                "main_category": "ALL",
                "period_type": "monthly",
                "amount": overall,
                "from_date": month_start.isoformat(),
                "to_date": month_end.isoformat(),
            })

            cat_budgets = {
                "disciplined": {
                    "Food & Dining": 6000, "Shopping": 4000,
                    "Entertainment": 3000, "Transportation": 2000,
                },
                "overspender": {
                    "Food & Dining": 5000, "Shopping": 5000,
                    "Entertainment": 4000,
                },
                "returning": {
                    "Food & Dining": 5000, "Groceries": 4000,
                    "Shopping": 3000,
                },
                "challenger": {
                    "Food & Dining": 7000, "Entertainment": 5000,
                    "Shopping": 5000, "Travel": 5000,
                },
            }

            for cat, amt in cat_budgets.get(profile, {}).items():
                bid += 1
                budgets.append({
                    "budget_id": f"BDG-{bid:04d}",
                    "user_id": uid,
                    "main_category": cat,
                    "period_type": "monthly",
                    "amount": amt,
                    "from_date": month_start.isoformat(),
                    "to_date": month_end.isoformat(),
                })

    return budgets


def generate_app_activity():
    """Generate app open dates for each user."""
    activity = []

    for user in USERS:
        uid = user["user_id"]
        profile = user["profile"]
        d = START_DATE

        while d <= END_DATE:
            opened = False

            if profile == "disciplined":
                opened = random.random() < 0.90
            elif profile == "overspender":
                opened = random.random() < 0.70
            elif profile == "returning":
                inactive_start = date(2026, 10, 20)
                inactive_end = date(2026, 11, 3)
                if inactive_start <= d <= inactive_end:
                    opened = False
                else:
                    opened = random.random() < 0.75
            elif profile == "minimal":
                if d < date(2026, 9, 20):
                    opened = False
                else:
                    opened = random.random() < 0.25
            elif profile == "challenger":
                opened = random.random() < 0.85

            if opened:
                activity.append({"user_id": uid, "date": d.isoformat()})

            d += timedelta(days=1)

    return activity


def generate_challenges_progress():
    """Generate challenge progress for users."""
    challenges = [
        ("know_your_money", "Know Your Money", 5),
        ("subscription_detective", "Subscription Detective", 3),
        ("weekend_explorer", "Weekend Explorer", 3),
        ("money_reflection", "Money Reflection", 7),
        ("expense_awareness", "Expense Awareness", 5),
    ]

    progress = []

    for user in USERS:
        uid = user["user_id"]
        profile = user["profile"]

        for cid, cname, target in challenges:
            if profile == "minimal":
                p = random.randint(0, 1)
            elif profile == "challenger":
                p = min(target, random.randint(target - 2, target))
            elif profile == "disciplined":
                p = random.randint(target // 2, target)
            elif profile == "overspender":
                p = random.randint(1, target - 1)
            else:
                p = random.randint(0, target // 2 + 1)

            started = "2026-09-01" if profile != "minimal" else "2026-10-15"
            completed = ""
            if p >= target:
                completed = f"2026-{random.choice(['10', '11'])}-{random.randint(1, 20):02d}"

            progress.append({
                "user_id": uid,
                "challenge_id": cid,
                "challenge_name": cname,
                "progress": p,
                "target": target,
                "started_on": started,
                "completed_on": completed,
            })

    return progress


def generate_garden_progress():
    """Generate Money Garden XP progress."""
    garden = []
    for user in USERS:
        uid = user["user_id"]
        profile = user["profile"]

        xp = {
            "disciplined": random.randint(70, 95),
            "overspender": random.randint(30, 50),
            "returning": random.randint(20, 40),
            "minimal": random.randint(0, 12),
            "challenger": random.randint(85, 120),
        }[profile]

        checkins = {
            "disciplined": random.randint(60, 80),
            "overspender": random.randint(35, 55),
            "returning": random.randint(25, 40),
            "minimal": random.randint(3, 10),
            "challenger": random.randint(55, 75),
        }[profile]

        reviews = {
            "disciplined": random.randint(15, 30),
            "overspender": random.randint(5, 15),
            "returning": random.randint(5, 12),
            "minimal": random.randint(0, 3),
            "challenger": random.randint(20, 35),
        }[profile]

        garden.append({
            "user_id": uid,
            "total_xp": xp,
            "checkins": checkins,
            "category_reviews": reviews,
            "challenges_completed": len(
                [1 for _ in range(5) if random.random() < (xp / 120)]
            ),
        })

    return garden


def write_csv(filename, data, fieldnames):
    path = DATA_DIR / filename
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"  Written: {path} ({len(data)} rows)")


def main():
    print("Nance – Synthetic Data Generator")
    print("=" * 40)

    users_data = [
        {
            "user_id": u["user_id"],
            "name": u["name"],
            "city": u["city"],
            "joined_on": u["joined_on"],
        }
        for u in USERS
    ]
    write_csv("users.csv", users_data, ["user_id", "name", "city", "joined_on"])

    txns = generate_transactions()
    write_csv("transactions.csv", txns, [
        "txn_id", "user_id", "txn_date", "txn_time", "amount",
        "transaction_type", "payment_mode", "main_category", "sub_category",
        "merchant_name", "person_name", "source", "arrived_at",
    ])

    budgets = generate_budgets()
    write_csv("budgets.csv", budgets, [
        "budget_id", "user_id", "main_category", "period_type",
        "amount", "from_date", "to_date",
    ])

    activity = generate_app_activity()
    write_csv("app_activity.csv", activity, ["user_id", "date"])

    challenges = generate_challenges_progress()
    write_csv("challenges_progress.csv", challenges, [
        "user_id", "challenge_id", "challenge_name", "progress",
        "target", "started_on", "completed_on",
    ])

    garden = generate_garden_progress()
    write_csv("garden_progress.csv", garden, [
        "user_id", "total_xp", "checkins", "category_reviews",
        "challenges_completed",
    ])

    print(f"\nTotal transactions: {len(txns)}")
    print(f"Total users: {len(users_data)}")
    print(f"Total budgets: {len(budgets)}")
    print(f"Total app activity records: {len(activity)}")
    print("Done!")


if __name__ == "__main__":
    main()
