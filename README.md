# Nance – Daily Money Moment
### Habit-Building Features for Personal Finance (AI Intern Assessment)

## 📌 Executive Summary

**Nance** is a personal finance application designed for Indian users. It aggregates transactions across bank accounts, credit cards, SMS, and emails, categorises spending, and tracks budgets.

### The Core Problem
Personal finance applications suffer from high churn and low engagement because:
1. **No compelling daily reason to open:** Users feel nothing is waiting for them if they skip a day.
2. **Avoidance after bad spending:** Users avoid opening the app after exceeding a budget or spending heavily ("ostrich effect").
3. **Good behaviour leaves no trace:** Days without spending or disciplined management generate zero feedback or celebration.
4. **Challenge fatigue:** Monolithic, one-time challenges lose appeal once novelties fade.

### The Solution: "Daily Money Moment"
> *"Nance doesn't reward users for spending less money. It rewards them for understanding their money better."*

Built upon three fundamental pillars:
- **NOTICE:** Uncover meaningful spending and recurring patterns without overwhelming tables.
- **REFLECT:** Present non-judgmental, guilt-free evaluations of financial habits.
- **RECOGNISE:** Acknowledge consistency, daily check-ins, and financial awareness, never penalising users for essential living costs.

---

## 🚀 Features Implemented

### 1. Daily Money Moment
A lightweight, daily dynamic card greeting the user with an actionable, data-backed insight:
- **Spending Shifts:** Highlights categories where spending moved >30% compared to previous periods.
- **Budget Health:** Transparent tracking with zero shame when budgets are exceeded.
- **Recurring Payment Reviews:** Identifies auto-debits and subscriptions up for reflection.
- **Quiet Day Acknowledgment:** Marks quieter recorded spending days with an awareness prompt.

### 2. Comeback Without Guilt
- For users inactive for multiple days (e.g., 3 to 14+ days), the system presents a warm, guilt-free welcome.
- Instead of showing broken streaks or missed-day alerts, it presents: *"Welcome back! One difficult spending week doesn't define your financial journey. Your next money check-in starts today."*
- Summarises aggregate spending that occurred during absence without judgement.

### 3. Quiet Money Day Classification
- Distinguishes between **no transactions recorded** (which could stem from delayed SMS sync, cash transactions, or pending bank imports) and **verified zero-spend**.
- Never assumes silence equals perfection, avoiding incentives that encourage users to stop logging expenses.

### 4. Spending Pattern Detective
- **Top Categories:** Real-time breakdown of current month's spending.
- **Weekend vs. Weekday Patterns:** Evaluates behavioural lifestyle trends.
- **Recurring & Subscription Tracker:** Detects consistent recurring debits across merchants (Swiggy, Netflix, Spotify, etc.) and analyzes variance.
- **Unusual Pattern Detection:** Compares rolling 7-day daily velocity against 30-day baselines.

### 5. Evolving Money Challenges
Progressive, awareness-focused challenges:
- **Know Your Money:** Review spending across 5 categories.
- **Subscription Detective:** Inspect 3 recurring payments.
- **Weekend Explorer:** Reflect on weekend spending for 3 weekends.
- **Money Reflection:** Complete 7 daily money check-ins.
- **Expense Awareness:** Review recent transactions and categories.

### 6. Money Garden (Engagement & Awareness Recognition)
- Visual progression mechanism: **Seed 🌱 → Sprout 🌿 → Sapling 🌳 → Bloom 🌸 → Garden 🏡**.
- **Crucial Rule:** XP is earned exclusively through awareness activities (checking in, reviewing a subscription, inspecting a budget), **never** for spending money, making purchases, or artificially cutting essentials.

---

## 👥 Demo User Personas & Scenarios

The system generates 5 realistic personas highlighting diverse behavioural and financial edge cases:

| User | City | Profile & Scenario Demonstrated |
| :--- | :--- | :--- |
| **Sneha** | Hyderabad | **Disciplined & Consistent:** Regular daily app opens (~90%), balanced budget utilisation across Food, Shopping, Transport. Demonstrates healthy streaks and Money Garden progression. |
| **Hari** | Bangalore | **Budget Exceeded / Food Delivery Overspender:** Heavy food delivery transactions (Swiggy/Zomato), frequently breaches dining budgets. Demonstrates the **Guilt-Free Budget Alert** and constructive reflections. |
| **Sravani** | Chennai | **Lapsing & Returning User:** Completely inactive on the app for two weeks (Oct 20 – Nov 3). Demonstrates the **Comeback Without Guilt** experience and non-punitive streak handling. |
| **Pallavi** | Mumbai | **Minimal Activity / Quiet Days:** Low transaction count, irregular app opens, joined more recently (Sep 20), no active budgets. Demonstrates **Quiet Money Days** and unverified zero-spend safeguards. |
| **Srujith** | Pune | **Challenge Champion & Weekend Spender:** High engagement, completes challenges, higher weekend spending ratio, diverse payment modes (P2P UPI, investments). Demonstrates **Challenge Engine** and **Weekend vs Weekday Detective**. |

---

## 🛡️ Ground Rules & Responsible Financial Principles

1. **Share Effort, Never Money:** Visual feedback celebrates showing up (streaks, check-ins, challenge completion), never net worth, salary, or balance.
2. **Zero Shaming:** No negative visual cues (no harsh red banners, no guilt-tripping notifications). Budget overruns are framed neutrally.
3. **Never Reward Spending:** No points, cashback, or badges for buying products or unlocking transaction tiers.
4. **Never Reward Artificial Deprivation:** No incentives to skip essentials (groceries, medicine, bills).
5. **Real Spending vs. Money Movement:**
   - Excludes **Self Transfers**, **Credit Card Bill Payments**, **Investments**, and **Cash Withdrawals** from spending metrics to prevent double counting.
   - Accurately captures **Refunds** and **Cashback** as non-spending credits.

---

## 🤖 Meaningful Use of AI

Nance incorporates an AI layer using **Google Gemini** with automatic fallback to deterministic rule engines:

### Where AI is Used:
1. **Dynamic Tone Personalisation:** Rephrasing insight cards according to user engagement state.
2. **Contextual Comeback Messages:** Generating compassionate return greetings based on days elapsed.
3. **Challenge Milestone Encouragement:** Personalized congratulatory notes upon challenge milestones.

### AI Safety & Privacy Guardrails (`ai_layer.py`):
- **Deterministic Financial Calculations:** All numbers, percentages, and amounts are computed deterministically in Python (`transaction_processor.py`). AI is never allowed to fabricate or calculate financial figures.
- **Safety Lexicon Filter:** Every AI response passes through `_validate_ai_message()` to ensure no shaming keywords ("wasteful", "irresponsible", "failed"), no peer comparisons ("worse than others"), and no spending triggers ("treat yourself").
- **Graceful Fallback:** If `GEMINI_API_KEY` is not present or an API call fails, the app seamlessly defaults to curated, deterministic templates with zero downtime.

---

## 📐 Data Schema & Extensions

### Existing Schema Adherence:
- `users`: `user_id`, `name`, `city`, `joined_on`
- `transactions`: `txn_id`, `user_id`, `txn_date`, `txn_time`, `amount`, `transaction_type`, `payment_mode`, `main_category`, `sub_category`, `merchant_name`, `person_name`, `source`, `arrived_at`
- `budgets`: `budget_id`, `user_id`, `main_category`, `period_type`, `amount`, `from_date`, `to_date`
- `app_activity`: `user_id`, `date`

### Extended Tables Added:
- `challenges_progress`: `user_id`, `challenge_id`, `challenge_name`, `progress`, `target`, `started_on`, `completed_on`
  - *Reason:* Tracks multi-day user awareness challenges, enabling progressive engagement.
- `garden_progress`: `user_id`, `total_xp`, `checkins`, `category_reviews`, `challenges_completed`
  - *Reason:* Persists non-monetary effort metrics to power the Money Garden visual progression.

---

## 🏗️ Project Architecture & Modularity

```
nance-assignment/
├── app.py                     # Streamlit interactive dashboard
├── config.py                  # Global configurations, categories, thresholds, and challenges
├── data_loader.py             # Data ingestion, schema validation, and user caching
├── transaction_processor.py   # Deterministic financial calculations & pattern detection
├── user_behaviour.py          # Streak, inactivity, and quiet-day analysis
├── insight_generator.py       # Daily Money Moment & detective insights orchestration
├── challenge_engine.py        # Challenge progression and Money Garden logic
├── ai_layer.py                # Gemini integration, prompt safety checks, and fallbacks
├── generate_data.py           # Reproducible synthetic data generator (Seed: 42)
├── test_nance.py              # 80 automated unit & integration tests
├── requirements.txt           # Project dependencies
├── README.md                  # Documentation
└── data/                      # Generated CSV datasets
    ├── users.csv
    ├── transactions.csv
    ├── budgets.csv
    ├── app_activity.csv
    ├── challenges_progress.csv
    └── garden_progress.csv
```

---

## 🛠️ Installation & Setup Instructions

### 1. Clone & Set Up Virtual Environment
```bash
git clone <repo-url>
cd nance-assignment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. (Optional) Configure Gemini API Key
To enable live AI message generation (otherwise deterministic rule-based mode is active):
```bash
# Windows PowerShell:
$env:GEMINI_API_KEY="your-api-key-here"
# Linux/macOS:
export GEMINI_API_KEY="your-api-key-here"
```

### 4. Regenerate Synthetic Data
The repository includes pre-generated synthetic datasets. To regenerate from scratch:
```bash
python generate_data.py
```

### 5. Run the Streamlit Dashboard
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser. Use the sidebar to toggle between users (**Sneha, Hari, Sravani, Pallavi, Srujith**) and explore different scenarios.

---

## 🧪 Testing & Validation

All 80 test cases covering calculations, edge cases, user behaviours, and AI safety checks can be executed via:
```bash
python -m pytest test_nance.py -v
```

### Tested Scenarios:
- **Transaction Filters:** Exclusion of self transfers, credit card payments, salary credits, and refunds from spending totals.
- **Budget Alerts:** Correct threshold identification (`healthy`, `on_track`, `warning`, `exceeded`) and edge cases with zero budgets.
- **Inactivity & Comeback:** Seamless detection of lapsing users and kind return messaging.
- **Quiet Day Classification:** Differentiating between missing data, zero spending, and non-spending transfers.
- **Streak Calculation:** Resilient streak evaluation that does not penalise users for missing past dates.
- **AI Safety:** Rejection of shaming vocabulary and spend-inducing triggers.
- **End-to-End User Verification:** Specific validation for all 5 demo user personas.
