"""
Nance – Data Loading and Validation

Loads CSV data files, validates schemas, and provides clean DataFrames
for use by feature modules.
"""

import pandas as pd
from pathlib import Path
from datetime import date, datetime
from typing import Optional, Dict

from config import DATA_DIR, TODAY, REAL_SPENDING_CATEGORIES, NON_SPENDING_CATEGORIES


class DataLoader:
    """Loads and validates all Nance data from CSV files."""

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or DATA_DIR
        self._users = None
        self._transactions = None
        self._budgets = None
        self._app_activity = None
        self._challenges = None
        self._garden = None

    def _load_csv(self, filename: str) -> pd.DataFrame:
        """Load a CSV file with error handling."""
        path = self.data_dir / filename
        if not path.exists():
            return pd.DataFrame()
        return pd.read_csv(path)

    @property
    def users(self) -> pd.DataFrame:
        if self._users is None:
            df = self._load_csv("users.csv")
            if not df.empty:
                df["joined_on"] = pd.to_datetime(df["joined_on"]).dt.date
            self._users = df
        return self._users

    @property
    def transactions(self) -> pd.DataFrame:
        if self._transactions is None:
            df = self._load_csv("transactions.csv")
            if not df.empty:
                df["txn_date"] = pd.to_datetime(df["txn_date"]).dt.date
                df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
                df["merchant_name"] = df["merchant_name"].fillna("")
                df["person_name"] = df["person_name"].fillna("")
                df["sub_category"] = df["sub_category"].fillna("")
            self._transactions = df
        return self._transactions

    @property
    def budgets(self) -> pd.DataFrame:
        if self._budgets is None:
            df = self._load_csv("budgets.csv")
            if not df.empty:
                df["from_date"] = pd.to_datetime(df["from_date"]).dt.date
                df["to_date"] = pd.to_datetime(df["to_date"]).dt.date
                df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
            self._budgets = df
        return self._budgets

    @property
    def app_activity(self) -> pd.DataFrame:
        if self._app_activity is None:
            df = self._load_csv("app_activity.csv")
            if not df.empty:
                df["date"] = pd.to_datetime(df["date"]).dt.date
            self._app_activity = df
        return self._app_activity

    @property
    def challenges(self) -> pd.DataFrame:
        if self._challenges is None:
            df = self._load_csv("challenges_progress.csv")
            if not df.empty:
                df["progress"] = pd.to_numeric(df["progress"], errors="coerce").fillna(0).astype(int)
                df["target"] = pd.to_numeric(df["target"], errors="coerce").fillna(1).astype(int)
            self._challenges = df
        return self._challenges

    @property
    def garden(self) -> pd.DataFrame:
        if self._garden is None:
            df = self._load_csv("garden_progress.csv")
            if not df.empty:
                for col in ["total_xp", "checkins", "category_reviews", "challenges_completed"]:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
            self._garden = df
        return self._garden

    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get a single user's info as a dict."""
        df = self.users
        if df.empty:
            return None
        row = df[df["user_id"] == user_id]
        if row.empty:
            return None
        return row.iloc[0].to_dict()

    def get_user_transactions(self, user_id: str) -> pd.DataFrame:
        """Get all transactions for a user."""
        df = self.transactions
        if df.empty:
            return df
        return df[df["user_id"] == user_id].copy()

    def get_user_spending(self, user_id: str) -> pd.DataFrame:
        """Get only real spending transactions (excludes money movement, income, etc.)."""
        txns = self.get_user_transactions(user_id)
        if txns.empty:
            return txns
        mask = (
            (txns["transaction_type"] == "debit")
            & (txns["main_category"].isin(REAL_SPENDING_CATEGORIES))
        )
        return txns[mask].copy()

    def get_user_budgets(self, user_id: str, as_of: Optional[date] = None) -> pd.DataFrame:
        """Get budgets for a user, optionally filtered to those active on a date."""
        df = self.budgets
        if df.empty:
            return df
        result = df[df["user_id"] == user_id].copy()
        if as_of and not result.empty:
            result = result[(result["from_date"] <= as_of) & (result["to_date"] >= as_of)]
        return result

    def get_user_app_activity(self, user_id: str) -> pd.DataFrame:
        """Get app activity for a user."""
        df = self.app_activity
        if df.empty:
            return df
        return df[df["user_id"] == user_id].copy()

    def get_user_challenges(self, user_id: str) -> pd.DataFrame:
        """Get challenge progress for a user."""
        df = self.challenges
        if df.empty:
            return df
        return df[df["user_id"] == user_id].copy()

    def get_user_garden(self, user_id: str) -> Optional[Dict]:
        """Get garden progress for a user."""
        df = self.garden
        if df.empty:
            return None
        row = df[df["user_id"] == user_id]
        if row.empty:
            return None
        return row.iloc[0].to_dict()

    def get_all_user_ids(self) -> list:
        """Get list of all user IDs."""
        if self.users.empty:
            return []
        return self.users["user_id"].tolist()

    def get_user_name_map(self) -> Dict[str, str]:
        """Get mapping of user_id -> name."""
        if self.users.empty:
            return {}
        return dict(zip(self.users["user_id"], self.users["name"]))
