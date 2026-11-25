"""
Nance – Daily Money Moment
Habit-Building Features for Personal Finance

A Streamlit dashboard that helps users build consistent financial awareness
through personalised insights, challenges, and progress tracking.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import TODAY, format_inr, CHALLENGES, GARDEN_STAGES
from data_loader import DataLoader
from transaction_processor import (
    get_spending_by_category, get_total_spending, get_budget_status,
    find_recurring_expenses, get_top_spending_categories,
    get_weekend_vs_weekday_spending, detect_unusual_spending,
    get_daily_spending, filter_real_spending, get_payment_mode_breakdown,
)
from user_behaviour import (
    classify_user_engagement, is_quiet_money_day, get_current_streak,
    get_weekly_activity_summary,
)
from insight_generator import (
    generate_daily_money_moment, generate_spending_detective_insights,
)
from challenge_engine import (
    get_challenge_status, get_challenges_summary,
    get_garden_status, get_next_recommended_challenge,
)
from ai_layer import (
    generate_comeback_message, generate_challenge_encouragement,
    generate_quiet_day_reflection, is_ai_available,
)

# ── Page config ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nance – Daily Money Moment",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main theme */
    .main .block-container {
        padding-top: 1.5rem;
        max-width: 1200px;
    }

    /* Header styling */
    .nance-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 1.5rem 2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 1.5rem;
    }
    .nance-header h1 {
        margin: 0;
        font-size: 1.8rem;
        font-weight: 700;
    }
    .nance-header p {
        margin: 0.3rem 0 0 0;
        opacity: 0.85;
        font-size: 0.95rem;
    }

    /* Money Moment card */
    .moment-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    .moment-card.comeback {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    .moment-card.quiet {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    .moment-card.budget-alert {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: #333;
    }
    .moment-card h3 {
        margin: 0 0 0.5rem 0;
        font-size: 1.3rem;
    }
    .moment-card p {
        margin: 0.3rem 0;
        font-size: 1rem;
        line-height: 1.5;
    }
    .moment-card .detail {
        margin-top: 0.8rem;
        font-size: 0.9rem;
        opacity: 0.9;
        font-style: italic;
    }

    /* Metric cards styling compatible with dark and light modes */
    div[data-testid="stMetric"] {
        background-color: var(--secondary-background-color, rgba(255, 255, 255, 0.05));
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    div[data-testid="stMetric"] label {
        color: var(--text-color, #888888) !important;
        opacity: 0.85;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: var(--text-color, #ffffff) !important;
        font-weight: 700;
    }

    /* Section headers with responsive color */
    .section-header {
        font-size: 1.2rem;
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(128, 128, 128, 0.2);
    }

    /* Challenge and insight cards */
    .challenge-card {
        background-color: var(--secondary-background-color, rgba(255, 255, 255, 0.05));
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
    }
    .challenge-card.completed {
        border-left: 4px solid #28a745;
    }
    .challenge-card.in-progress {
        border-left: 4px solid #667eea;
    }

    .insight-card {
        background-color: var(--secondary-background-color, rgba(255, 255, 255, 0.05));
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        border-left: 4px solid #667eea;
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
</style>
""", unsafe_allow_html=True)


# ── Data loading ─────────────────────────────────────────────────────
@st.cache_data
def load_data():
    loader = DataLoader()
    return loader


loader = load_data()

# ── Sidebar ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💰 Nance")
    st.markdown("**Daily Money Moment**")
    st.markdown("---")

    # User selector
    user_map = loader.get_user_name_map()
    user_ids = loader.get_all_user_ids()

    if not user_ids:
        st.error("No data found. Run `python generate_data.py` first.")
        st.stop()

    selected_name = st.selectbox(
        "👤 Select User",
        options=[user_map[uid] for uid in user_ids],
        index=0,
    )
    selected_uid = [uid for uid, name in user_map.items() if name == selected_name][0]

    st.markdown("---")

    # User info
    user_info = loader.get_user(selected_uid)
    if user_info:
        st.markdown(f"**City:** {user_info['city']}")
        st.markdown(f"**Joined:** {user_info['joined_on']}")

    # Navigation
    st.markdown("---")
    st.markdown("### 📍 Navigation")
    page = st.radio(
        "Go to",
        [
            "🏠 Home",
            "📊 Spending Insights",
            "🏆 Challenges",
            "🌱 Money Garden",
        ],
        label_visibility="collapsed",
    )

    # AI status
    st.markdown("---")
    if is_ai_available():
        st.success("🤖 AI: Connected")
    else:
        st.info("🤖 AI: Rule-based mode")
        st.caption("Set GEMINI_API_KEY for AI-powered messages")

    st.markdown("---")
    st.caption(f"Demo date: {TODAY.strftime('%d %b %Y')}")


# ── Load user data ───────────────────────────────────────────────────
user_txns = loader.get_user_transactions(selected_uid)
user_spending = loader.get_user_spending(selected_uid)
user_budgets = loader.get_user_budgets(selected_uid, TODAY)
user_activity = loader.get_user_app_activity(selected_uid)
user_challenges = loader.get_user_challenges(selected_uid)
user_garden_data = loader.get_user_garden(selected_uid)

engagement = classify_user_engagement(user_activity, TODAY)


# ══════════════════════════════════════════════════════════════════════
# HOME PAGE
# ══════════════════════════════════════════════════════════════════════
if page == "🏠 Home":

    # ── Header ───────────────────────────────────────────────────────
    greeting = "Good afternoon" if 12 <= 14 < 17 else "Hello"
    st.markdown(f"""
    <div class="nance-header">
        <h1>💰 {greeting}, {selected_name}!</h1>
        <p>Your Daily Money Moment — {TODAY.strftime('%A, %d %B %Y')}</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Daily Money Moment ───────────────────────────────────────────
    moment = generate_daily_money_moment(user_txns, user_budgets, user_activity, TODAY)

    moment_class = "moment-card"
    if moment["type"] == "comeback":
        moment_class += " comeback"
    elif moment["type"] == "quiet_day":
        moment_class += " quiet"
    elif moment["type"] == "budget_alert":
        moment_class += " budget-alert"

    detail_html = ""
    if moment.get("detail"):
        detail_html = f'<p class="detail">{moment["detail"]}</p>'

    reflection_html = ""
    if moment.get("reflection"):
        reflection_html = f'<p class="detail">💭 {moment["reflection"]}</p>'

    st.markdown(f"""
    <div class="{moment_class}">
        <h3>{moment.get("icon", "💡")} {moment["title"]}</h3>
        <p>{moment["message"]}</p>
        {detail_html}
        {reflection_html}
    </div>
    """, unsafe_allow_html=True)

    # ── Key metrics ──────────────────────────────────────────────────
    st.markdown('<div class="section-header">📋 Financial Overview</div>', unsafe_allow_html=True)

    month_start = TODAY.replace(day=1)
    month_spending = get_total_spending(user_txns, month_start, TODAY)
    week_spending = get_total_spending(user_txns, TODAY - timedelta(days=6), TODAY)
    today_spending = get_total_spending(user_txns, TODAY, TODAY)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("This Month", format_inr(month_spending))
    with col2:
        st.metric("This Week", format_inr(week_spending))
    with col3:
        st.metric("Today", format_inr(today_spending))
    with col4:
        streak = engagement["current_streak"]
        st.metric("Check-in Streak", f"{streak} day{'s' if streak != 1 else ''}")

    # ── Budget Status ────────────────────────────────────────────────
    budget_statuses = get_budget_status(user_txns, user_budgets, TODAY)
    if budget_statuses:
        st.markdown('<div class="section-header">💳 Budget Progress</div>', unsafe_allow_html=True)

        for bs in budget_statuses:
            cat_label = "Overall" if bs["category"] == "ALL" else bs["category"]
            status_colors = {
                "healthy": "#28a745", "on_track": "#17a2b8",
                "warning": "#ffc107", "exceeded": "#dc3545",
            }
            color = status_colors.get(bs["status"], "#6c757d")
            status_emojis = {
                "healthy": "✅", "on_track": "📊",
                "warning": "⚠️", "exceeded": "🔴",
            }
            emoji = status_emojis.get(bs["status"], "")

            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.markdown(f"**{emoji} {cat_label}**")
                pct = min(bs["utilisation_pct"], 100)
                st.progress(pct / 100)
                st.caption(
                    f"{format_inr(bs['spent'])} / {format_inr(bs['limit'])} "
                    f"({bs['utilisation_pct']}%) · {bs['days_remaining']} days left"
                )
            with col_b:
                remaining = bs['remaining']
                if bs["status"] == "exceeded":
                    st.markdown(f"<span style='color:{color};font-weight:bold;'>Over by {format_inr(bs['spent'] - bs['limit'])}</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<span style='color:{color};font-weight:bold;'>{format_inr(remaining)} left</span>", unsafe_allow_html=True)
    else:
        st.info("No budgets set up yet. Budgets help you track spending against your goals.")

    # ── Recent Transactions ──────────────────────────────────────────
    st.markdown('<div class="section-header">📝 Recent Transactions</div>', unsafe_allow_html=True)

    if not user_txns.empty:
        recent = user_txns.sort_values("txn_date", ascending=False).head(10)
        for _, txn in recent.iterrows():
            type_icon = "🔴" if txn["transaction_type"] == "debit" else "🟢"
            merchant = txn["merchant_name"] if txn["merchant_name"] else txn["main_category"]
            amount_display = format_inr(txn["amount"])

            col_l, col_r = st.columns([4, 1])
            with col_l:
                st.markdown(
                    f"{type_icon} **{merchant}** · {txn['main_category']} · "
                    f"*{txn['txn_date']}*"
                )
            with col_r:
                color = "#dc3545" if txn["transaction_type"] == "debit" else "#28a745"
                prefix = "-" if txn["transaction_type"] == "debit" else "+"
                st.markdown(
                    f"<span style='color:{color};font-weight:600;'>{prefix}{amount_display}</span>",
                    unsafe_allow_html=True,
                )
    else:
        st.info("No transactions recorded yet. Transactions will appear here once available.")

    # ── Engagement snapshot ──────────────────────────────────────────
    st.markdown('<div class="section-header">📈 Your Engagement</div>', unsafe_allow_html=True)

    col_e1, col_e2, col_e3 = st.columns(3)
    with col_e1:
        st.metric("Total Check-ins", engagement["total_active_days"])
    with col_e2:
        st.metric("Longest Streak", f"{engagement['longest_streak']} days")
    with col_e3:
        st.metric("Recent Activity", f"{engagement['recent_activity_rate']}%")

    # Weekly activity heatmap
    weekly = get_weekly_activity_summary(user_activity, TODAY)
    if weekly:
        week_labels = [f"Week of {w['week_start'].strftime('%d %b')}" for w in weekly]
        week_values = [w["days_active"] for w in weekly]

        fig = go.Figure(go.Bar(
            x=week_labels[::-1],
            y=week_values[::-1],
            marker_color=["#667eea" if v >= 5 else "#a0aec0" for v in week_values[::-1]],
            text=[f"{v}/7" for v in week_values[::-1]],
            textposition="auto",
        ))
        fig.update_layout(
            title="Weekly App Activity",
            xaxis_title="", yaxis_title="Days Active",
            yaxis=dict(range=[0, 7]),
            height=250,
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, width="stretch")


# ══════════════════════════════════════════════════════════════════════
# SPENDING INSIGHTS PAGE
# ══════════════════════════════════════════════════════════════════════
elif page == "📊 Spending Insights":
    st.markdown(f"""
    <div class="nance-header">
        <h1>🔍 Spending Pattern Detective</h1>
        <p>Understand your spending patterns — {selected_name}</p>
    </div>
    """, unsafe_allow_html=True)

    if user_spending.empty:
        st.info("Not enough spending data to generate insights yet. Keep using Nance!")
    else:
        # ── Top categories this month ────────────────────────────────
        month_start = TODAY.replace(day=1)
        top_cats = get_top_spending_categories(user_txns, month_start, TODAY, top_n=8)

        if top_cats:
            st.markdown('<div class="section-header">📊 Top Spending Categories (This Month)</div>', unsafe_allow_html=True)

            cat_names = [c["category"] for c in top_cats]
            cat_amounts = [c["amount"] for c in top_cats]
            cat_pcts = [c["percentage"] for c in top_cats]

            col_chart, col_detail = st.columns([3, 2])

            with col_chart:
                fig = px.pie(
                    names=cat_names,
                    values=cat_amounts,
                    color_discrete_sequence=px.colors.qualitative.Set2,
                    hole=0.4,
                )
                fig.update_layout(
                    height=350,
                    margin=dict(l=20, r=20, t=20, b=20),
                    legend=dict(orientation="v", yanchor="middle", y=0.5),
                )
                fig.update_traces(textinfo="percent+label", textposition="outside")
                st.plotly_chart(fig, width="stretch")

            with col_detail:
                for c in top_cats:
                    st.markdown(
                        f"**{c['category']}** — {format_inr(c['amount'])} "
                        f"({c['percentage']}%)"
                    )

        # ── Weekend vs Weekday ───────────────────────────────────────
        st.markdown('<div class="section-header">📅 Weekend vs Weekday Spending</div>', unsafe_allow_html=True)

        wk_data = get_weekend_vs_weekday_spending(user_txns, month_start, TODAY)
        col_wk1, col_wk2, col_wk3 = st.columns(3)
        with col_wk1:
            st.metric("Weekday Average", format_inr(wk_data["weekday_avg"]), help="Average daily spending on weekdays")
        with col_wk2:
            st.metric("Weekend Average", format_inr(wk_data["weekend_avg"]), help="Average daily spending on weekends")
        with col_wk3:
            ratio = wk_data["ratio"]
            if ratio > 1.3:
                st.metric("Weekend / Weekday", f"{ratio}x", "Higher on weekends")
            elif ratio < 0.7:
                st.metric("Weekend / Weekday", f"{ratio}x", "Lower on weekends")
            else:
                st.metric("Weekend / Weekday", f"{ratio}x", "Similar pattern")

        # ── Daily spending trend ─────────────────────────────────────
        st.markdown('<div class="section-header">📈 Daily Spending Trend</div>', unsafe_allow_html=True)

        last_30 = TODAY - timedelta(days=29)
        daily = get_daily_spending(user_txns, last_30, TODAY)

        if daily:
            dates = []
            amounts = []
            d = last_30
            while d <= TODAY:
                dates.append(d)
                amounts.append(daily.get(d, 0))
                d += timedelta(days=1)

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates, y=amounts,
                mode="lines+markers",
                line=dict(color="#667eea", width=2),
                marker=dict(size=4),
                fill="tozeroy",
                fillcolor="rgba(102,126,234,0.1)",
            ))
            fig.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=20, b=20),
                xaxis_title="", yaxis_title="Spending (₹)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig, width="stretch")

        # ── Recurring expenses ───────────────────────────────────────
        recurring = find_recurring_expenses(user_txns)
        if recurring:
            st.markdown('<div class="section-header">🔄 Recurring Expenses</div>', unsafe_allow_html=True)

            for r in recurring[:6]:
                sub_icon = "🔁" if r["is_subscription"] else "🔄"
                consistency_badge = "🟢" if r["consistency"] == "high" else "🟡"
                st.markdown(
                    f"{sub_icon} **{r['merchant']}** · {r['category']} · "
                    f"~{format_inr(r['avg_amount'])} · "
                    f"{r['occurrences']} times · {consistency_badge} {r['consistency']} consistency"
                )

        # ── Unusual patterns ─────────────────────────────────────────
        unusual = detect_unusual_spending(user_txns, as_of=TODAY)
        if unusual:
            st.markdown('<div class="section-header">🔍 Unusual Patterns (vs your average)</div>', unsafe_allow_html=True)

            for u in unusual[:4]:
                direction_icon = "📈" if u["direction"] == "higher" else "📉"
                st.markdown(
                    f"{direction_icon} **{u['category']}** — "
                    f"Recent: {format_inr(u['recent_daily'])}/day vs "
                    f"Average: {format_inr(u['historical_daily'])}/day "
                    f"({u['change_pct']:+.0f}%)"
                )
                st.caption("This is based on your last 7 days vs previous 30 days.")

        # ── Payment mode breakdown ───────────────────────────────────
        pm_data = get_payment_mode_breakdown(user_txns)
        if pm_data:
            st.markdown('<div class="section-header">💳 Payment Mode Breakdown</div>', unsafe_allow_html=True)

            fig = px.bar(
                x=list(pm_data.keys()),
                y=list(pm_data.values()),
                color=list(pm_data.keys()),
                color_discrete_sequence=px.colors.qualitative.Pastel,
                labels={"x": "Payment Mode", "y": "Total (₹)"},
            )
            fig.update_layout(
                height=280,
                margin=dict(l=20, r=20, t=20, b=20),
                showlegend=False,
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig, width="stretch")


# ══════════════════════════════════════════════════════════════════════
# CHALLENGES PAGE
# ══════════════════════════════════════════════════════════════════════
elif page == "🏆 Challenges":
    st.markdown(f"""
    <div class="nance-header">
        <h1>🏆 Awareness Challenges</h1>
        <p>Build financial awareness one challenge at a time — {selected_name}</p>
    </div>
    """, unsafe_allow_html=True)

    # Challenge summary
    summary = get_challenges_summary(user_challenges)

    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.metric("Total", summary["total"])
    with col_s2:
        st.metric("Completed ✅", summary["completed"])
    with col_s3:
        st.metric("In Progress 🔄", summary["in_progress"])
    with col_s4:
        st.metric("Completion Rate", f"{summary['completion_rate']}%")

    # Next recommended challenge
    recommended = get_next_recommended_challenge(user_challenges)
    if recommended:
        encouragement = generate_challenge_encouragement(
            recommended["name"], recommended["progress"],
            recommended["target"], selected_name,
        )
        st.markdown(f"""
        <div class="moment-card">
            <h3>💡 Recommended Next</h3>
            <p>{encouragement}</p>
        </div>
        """, unsafe_allow_html=True)

    # All challenges
    st.markdown('<div class="section-header">📋 Your Challenges</div>', unsafe_allow_html=True)

    statuses = get_challenge_status(user_challenges)
    for ch in statuses:
        status_class = ""
        if ch["is_complete"]:
            status_class = "completed"
        elif ch["status"] == "in_progress":
            status_class = "in-progress"

        col_ch1, col_ch2 = st.columns([4, 1])
        with col_ch1:
            status_icon = "✅" if ch["is_complete"] else ("🔄" if ch["status"] == "in_progress" else "⬜")
            st.markdown(f"### {ch['icon']} {ch['name']} {status_icon}")
            st.markdown(f"*{ch['description']}*")
            st.progress(ch["percentage"] / 100)
            st.caption(f"{ch['progress']}/{ch['target']} {ch['unit']}")
            if ch["is_complete"] and ch.get("completed_on"):
                st.caption(f"Completed on {ch['completed_on']}")
        with col_ch2:
            st.markdown(f"### {ch['percentage']}%")

        st.markdown("---")


# ══════════════════════════════════════════════════════════════════════
# MONEY GARDEN PAGE
# ══════════════════════════════════════════════════════════════════════
elif page == "🌱 Money Garden":
    st.markdown(f"""
    <div class="nance-header">
        <h1>🌱 Money Garden</h1>
        <p>Watch your financial awareness grow — {selected_name}</p>
    </div>
    """, unsafe_allow_html=True)

    garden = get_garden_status(user_garden_data)
    stage = garden["stage"]

    # Garden visualization
    st.markdown(f"""
    <div class="garden-container">
        <div class="garden-emoji">{stage['stage_emoji']}</div>
        <div class="garden-stage">{stage['stage_name']}</div>
        <p style="color:#4a7c59;margin-top:0.5rem;">{stage['total_xp']} XP earned</p>
    </div>
    """, unsafe_allow_html=True)

    # Progress to next stage
    if stage["next_stage"]:
        st.markdown(f"**Next stage:** {stage['next_stage_emoji']} {stage['next_stage']} — "
                    f"{stage['xp_to_next']} XP to go")
        st.progress(stage["progress_to_next"] / 100)
    else:
        st.success("🎉 You've reached the highest stage! Your garden is fully grown!")

    # Activity breakdown
    st.markdown('<div class="section-header">📊 How You Earned Your XP</div>', unsafe_allow_html=True)

    activities = garden["activities"]
    if activities:
        for a in activities:
            st.markdown(f"{a['icon']} **{a['name']}:** {a['count']}")
    else:
        st.info("Start checking in daily and reviewing your spending to earn XP!")

    # Garden stages reference
    st.markdown('<div class="section-header">🗺️ Garden Stages</div>', unsafe_allow_html=True)

    for gs in GARDEN_STAGES:
        is_current = gs["name"] == stage["stage_name"]
        marker = " ← You are here" if is_current else ""
        style = "font-weight:bold;" if is_current else "opacity:0.7;"
        st.markdown(
            f"<span style='{style}'>{gs['emoji']} {gs['name']} "
            f"({gs['min_xp']}+ XP){marker}</span>",
            unsafe_allow_html=True,
        )

    # How to earn XP
    st.markdown('<div class="section-header">💡 How to Grow Your Garden</div>', unsafe_allow_html=True)
    st.markdown("""
    Your Money Garden grows through **financial awareness activities**, not spending:

    | Activity | XP |
    |---|---|
    | ☀️ Daily check-in | +2 XP |
    | 📊 Review a spending category | +1 XP |
    | 🔍 Review a subscription | +2 XP |
    | 🏆 Complete a challenge | +5 XP |
    | 🗓️ Weekend spending review | +3 XP |

    > **Note:** XP is earned through awareness and engagement, never through spending or saving specific amounts.
    """)
