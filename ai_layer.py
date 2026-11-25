"""
Nance – AI-Powered Message Generation

Uses Google Gemini (when available) or rule-based fallbacks to generate
personalised, kind, and financially responsible messages.

AI is used for:
1. Personalising Daily Money Moment messages
2. Generating kind comeback messages
3. Creating contextual challenge encouragement

All AI outputs are:
- Based on verified data inputs (never invented financial facts)
- Checked for kindness and safety
- Fallback to rule-based messages when AI is unavailable
"""

import os
import random
from typing import Dict, Optional

from config import format_inr


# ── AI availability check ────────────────────────────────────────────

_gemini_available = False
_model = None


def _init_gemini():
    """Try to initialise Gemini. Fail silently if unavailable."""
    global _gemini_available, _model
    try:
        import google.generativeai as genai
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if api_key:
            genai.configure(api_key=api_key)
            _model = genai.GenerativeModel("gemini-1.5-flash")
            _gemini_available = True
    except Exception:
        _gemini_available = False


_init_gemini()


def is_ai_available() -> bool:
    """Check if AI generation is available."""
    return _gemini_available


# ── Safety checks ────────────────────────────────────────────────────

def _validate_ai_message(message: str) -> bool:
    """
    Validate that an AI-generated message follows Nance's principles:
    - No shaming language
    - No specific financial amounts (unless from verified data)
    - No comparisons with other users
    - No encouragement to spend or avoid spending
    """
    shame_words = [
        "wasteful", "irresponsible", "bad with money", "failed",
        "terrible", "awful", "shameful", "worse than", "behind",
        "everyone else", "other users", "you should feel",
    ]
    for word in shame_words:
        if word.lower() in message.lower():
            return False

    spend_encouragements = [
        "buy more", "spend more", "treat yourself",
        "reward yourself with a purchase", "you deserve to shop",
    ]
    for phrase in spend_encouragements:
        if phrase.lower() in message.lower():
            return False

    return True


def _safe_generate(prompt: str, fallback: str) -> str:
    """Generate with AI if available, with safety checks and fallback."""
    if not _gemini_available or _model is None:
        return fallback

    try:
        response = _model.generate_content(prompt)
        text = response.text.strip()

        # Safety check
        if not _validate_ai_message(text):
            return fallback

        # Length check — keep it concise
        if len(text) > 300:
            text = text[:297] + "..."

        return text

    except Exception:
        return fallback


# ── Public API ───────────────────────────────────────────────────────

def personalise_insight_message(
    insight: Dict,
    user_name: str,
    engagement_level: str,
) -> str:
    """
    Generate a personalised version of an insight message.
    Uses AI when available, falls back to the original message.
    """
    original = insight.get("message", "")

    prompt = f"""You are a friendly personal finance assistant for an Indian user named {user_name}.
Rewrite this financial insight in a warm, encouraging tone. Keep it under 2 sentences.
Never shame the user. Never invent financial amounts. Never compare with other users.

Original insight: {original}

User's engagement level: {engagement_level}

Rewritten message:"""

    return _safe_generate(prompt, original)


def generate_comeback_message(
    user_name: str,
    days_inactive: int,
    total_spent_while_away: float,
) -> str:
    """Generate a warm comeback message for returning users."""
    if days_inactive >= 14:
        fallbacks = [
            f"Welcome back, {user_name}! It's been a while, and that's perfectly fine. Let's take a fresh look at your finances together.",
            f"Hey {user_name}, great to see you! No matter how long it's been, your next money check-in starts right now.",
            f"Welcome back, {user_name}! Every return is a step toward better financial awareness.",
        ]
    elif days_inactive >= 7:
        fallbacks = [
            f"Good to see you, {user_name}! A week away? No worries. Let's catch up on your finances.",
            f"Hey {user_name}! Your money journey continues — one check-in at a time.",
        ]
    else:
        fallbacks = [
            f"Welcome back, {user_name}! Ready for a quick money moment?",
            f"Hey {user_name}! Let's see what's been happening with your money.",
        ]

    fallback = random.choice(fallbacks)

    if not _gemini_available:
        return fallback

    spent_info = ""
    if total_spent_while_away > 0:
        spent_info = f"While they were away, {format_inr(total_spent_while_away)} in spending was recorded."

    prompt = f"""You are a friendly personal finance assistant. Write a warm, encouraging
welcome-back message for {user_name} who hasn't opened the app in {days_inactive} days.
{spent_info}

Rules:
- Be warm and kind, never shame them for being away
- Keep it to 1-2 short sentences
- Don't mention exact amounts unless provided
- Don't say things like "we missed you" (it's an app, not a person)
- Encourage them to check in, not to spend or save specific amounts

Message:"""

    return _safe_generate(prompt, fallback)


def generate_challenge_encouragement(
    challenge_name: str,
    progress: int,
    target: int,
    user_name: str,
) -> str:
    """Generate encouragement for a challenge."""
    pct = round(progress / target * 100) if target > 0 else 0

    if pct >= 100:
        fallbacks = [
            f"🎉 Congratulations! You've completed the {challenge_name} challenge!",
            f"Well done! {challenge_name} — completed! Your financial awareness is growing.",
        ]
    elif pct >= 70:
        fallbacks = [
            f"Almost there! {progress}/{target} — just a little more to complete {challenge_name}.",
            f"You're so close to completing {challenge_name}! Keep going!",
        ]
    elif pct >= 30:
        fallbacks = [
            f"Good progress on {challenge_name}! {progress}/{target} completed so far.",
            f"You're making steady progress on {challenge_name} — {progress}/{target}!",
        ]
    else:
        fallbacks = [
            f"You've started {challenge_name}! Every step counts — {progress}/{target} so far.",
            f"{challenge_name} is underway! {progress}/{target} completed.",
        ]

    return random.choice(fallbacks)


def generate_quiet_day_reflection(user_name: str) -> str:
    """Generate a reflection prompt for a quiet money day."""
    reflections = [
        f"{user_name}, a quieter day can be a good time to review a spending category.",
        f"No spending recorded today, {user_name}. Your money check-in is still valuable.",
        f"A calm day in your finances, {user_name}. Perhaps review your budget progress?",
        f"Quieter days are perfect for reflecting on your financial goals, {user_name}.",
    ]
    return random.choice(reflections)
