"""
Nance – Challenge and Progress Logic

Manages awareness challenges, XP calculation, and Money Garden progress.
"""

from datetime import date
from typing import Dict, List, Optional
import pandas as pd

from config import CHALLENGES, GARDEN_STAGES, format_inr


def get_challenge_status(challenges_df: pd.DataFrame) -> List[Dict]:
    """
    Get the status of all challenges for a user.
    Returns list of challenge dicts with progress info.
    """
    if challenges_df.empty:
        # Return default challenges with zero progress
        return [
            {
                "id": c["id"],
                "name": c["name"],
                "description": c["description"],
                "icon": c["icon"],
                "progress": 0,
                "target": c["target"],
                "unit": c["unit"],
                "percentage": 0,
                "is_complete": False,
                "status": "not_started",
            }
            for c in CHALLENGES
        ]

    statuses = []
    for c in CHALLENGES:
        row = challenges_df[challenges_df["challenge_id"] == c["id"]]
        if row.empty:
            progress = 0
            completed_on = ""
        else:
            progress = int(row.iloc[0]["progress"])
            completed_on = row.iloc[0].get("completed_on", "")

        target = c["target"]
        percentage = min(100, round(progress / target * 100)) if target > 0 else 0
        is_complete = progress >= target

        if is_complete:
            status = "completed"
        elif progress > 0:
            status = "in_progress"
        else:
            status = "not_started"

        statuses.append({
            "id": c["id"],
            "name": c["name"],
            "description": c["description"],
            "icon": c["icon"],
            "progress": progress,
            "target": target,
            "unit": c["unit"],
            "percentage": percentage,
            "is_complete": is_complete,
            "status": status,
            "completed_on": completed_on if is_complete else None,
        })

    return statuses


def get_challenges_summary(challenges_df: pd.DataFrame) -> Dict:
    """Get a high-level summary of challenge progress."""
    statuses = get_challenge_status(challenges_df)

    total = len(statuses)
    completed = sum(1 for s in statuses if s["is_complete"])
    in_progress = sum(1 for s in statuses if s["status"] == "in_progress")
    not_started = sum(1 for s in statuses if s["status"] == "not_started")

    return {
        "total": total,
        "completed": completed,
        "in_progress": in_progress,
        "not_started": not_started,
        "completion_rate": round(completed / total * 100) if total > 0 else 0,
    }


def get_garden_stage(total_xp: int) -> Dict:
    """Determine the current Money Garden stage based on XP."""
    current_stage = GARDEN_STAGES[0]
    next_stage = None

    for i, stage in enumerate(GARDEN_STAGES):
        if total_xp >= stage["min_xp"]:
            current_stage = stage
            if i + 1 < len(GARDEN_STAGES):
                next_stage = GARDEN_STAGES[i + 1]
            else:
                next_stage = None

    # Progress to next stage
    if next_stage:
        range_xp = next_stage["min_xp"] - current_stage["min_xp"]
        progress_xp = total_xp - current_stage["min_xp"]
        progress_pct = round(progress_xp / range_xp * 100) if range_xp > 0 else 100
    else:
        progress_pct = 100  # Max stage reached

    return {
        "stage_name": current_stage["name"],
        "stage_emoji": current_stage["emoji"],
        "total_xp": total_xp,
        "progress_to_next": progress_pct,
        "next_stage": next_stage["name"] if next_stage else None,
        "next_stage_emoji": next_stage["emoji"] if next_stage else None,
        "xp_to_next": (next_stage["min_xp"] - total_xp) if next_stage else 0,
    }


def get_garden_status(garden_data: Optional[Dict]) -> Dict:
    """Get complete Money Garden status for display."""
    if not garden_data:
        return {
            "stage": get_garden_stage(0),
            "total_xp": 0,
            "checkins": 0,
            "category_reviews": 0,
            "challenges_completed": 0,
            "activities": [],
        }

    xp = garden_data.get("total_xp", 0)
    stage = get_garden_stage(xp)

    activities = []
    checkins = garden_data.get("checkins", 0)
    reviews = garden_data.get("category_reviews", 0)
    challenges = garden_data.get("challenges_completed", 0)

    if checkins > 0:
        activities.append({
            "name": "Daily check-ins",
            "count": checkins,
            "icon": "☀️",
        })
    if reviews > 0:
        activities.append({
            "name": "Categories reviewed",
            "count": reviews,
            "icon": "📊",
        })
    if challenges > 0:
        activities.append({
            "name": "Challenges completed",
            "count": challenges,
            "icon": "🏆",
        })

    return {
        "stage": stage,
        "total_xp": xp,
        "checkins": checkins,
        "category_reviews": reviews,
        "challenges_completed": challenges,
        "activities": activities,
    }


def get_next_recommended_challenge(challenges_df: pd.DataFrame) -> Optional[Dict]:
    """Recommend the next challenge for the user to try."""
    statuses = get_challenge_status(challenges_df)

    # First recommend in-progress challenges
    in_progress = [s for s in statuses if s["status"] == "in_progress"]
    if in_progress:
        # Pick the one closest to completion
        in_progress.sort(key=lambda x: x["percentage"], reverse=True)
        return in_progress[0]

    # Then recommend not-started ones
    not_started = [s for s in statuses if s["status"] == "not_started"]
    if not_started:
        return not_started[0]

    return None  # All completed
