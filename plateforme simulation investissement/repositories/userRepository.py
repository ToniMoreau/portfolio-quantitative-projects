from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional
import pandas as pd
from pathlib import Path

from domain.user import User


class UserRepository:
    def __init__(self, xlsx_path: str | Path, sheet_name: str = "Profils"):
        self.xlsx_path = Path(xlsx_path)
        self.sheet_name = sheet_name
        self._df_cache: Optional[pd.DataFrame] = None  # cache optionnel

    # --------- I/O ---------
    def _load_df(self, force_reload: bool = False) -> pd.DataFrame:
        if self._df_cache is None or force_reload:
            if not self.xlsx_path.exists():
                # créer une "table" vide si fichier absent
                self._df_cache = pd.DataFrame(columns=[
                    "ID", "username", "password_hash", "name", "email"
                ])
            else:
                self._df_cache = pd.read_excel(self.xlsx_path, sheet_name=self.sheet_name)
                # normalisation basique
                if "ID" in self._df_cache.columns:
                    self._df_cache["ID"] = pd.to_numeric(self._df_cache["ID"], errors="coerce").astype("Int64")
        return self._df_cache

    def _save_df(self, df: pd.DataFrame) -> None:
        # écriture complète de la feuille (simple + fiable)
        with pd.ExcelWriter(
            self.xlsx_path,
            engine="openpyxl",
            mode="a",
            if_sheet_exists="replace"   # remplace seulement la feuille Metiers
        ) as writer:
            df.to_excel(writer, sheet_name=self.sheet_name, index=False)
        self._df_cache = df    
        
    def _row_to_user(self, row: pd.Series) -> User:
        # robustesse NaN
        def s(x): 
            return "" if pd.isna(x) else str(x)
        return User(
            id=int(row["ID"]),
            username=s(row.get("username", "")),
            firstname=s(row.get("firstname", "")),
            lastname=s(row.get("lastname", "")),
            email=s(row.get("email", "")),
            password = s(row["password"]),
            age = None if pd.isna(row.get("age")) else int(row["age"])
        )        

    # --------- getters ---------
    def get_by_ID(self, user_ID: int) -> User:
        df = self._load_df()
        row = df[df["ID"] == user_ID]
        if row.empty:
            return None
        return self._row_to_user(row.iloc[0])

    def get_by_username(self, username: str) -> User:
        df = self._load_df()
        row = df[df["username"] == username]
        if row.empty:
            return None
        return self._row_to_user(row.iloc[0])

    def exists_username(self, username: str) -> bool:
        return self.get_by_username(username) is not None

    # --------- writes ---------
    def create(self, user: dict[str, Any]) -> dict[str, Any]:
        """
        user doit contenir au minimum: username, password_hash
        ID sera généré si absent.
        """
        df = self._load_df()

        if self.exists_username(user["username"]):
            raise ValueError("Username déjà utilisé")

        if "ID" not in user or user["ID"] is None:
            next_ID = int(df["ID"].max()) + 1 if (len(df) and df["ID"].notna().any()) else 1
            user["ID"] = next_ID

        df = pd.concat([df, pd.DataFrame([user])], ignore_index=True)
        self._save_df(df)
        return self._row_to_user(user)

    def update(self, user_ID: int, patch: dict[str, Any]) -> dict[str, Any]:
        df = self._load_df()

        IDx = df.index[df["ID"] == user_ID]
        if len(IDx) == 0:
            raise ValueError("Utilisateur introuvable")

        i = IDx[0]
        for k, v in patch.items():
            if k == "ID":
                continue
            print("UPDATE", k, "=>", v, "type:", type(v))
            df.at[i, k] = v

        self._save_df(df)
        return self._row_to_user(df.iloc[i])

    def delete(self, user_ID: int) -> None:
        df = self._load_df()
        df2 = df[df["ID"] != user_ID].copy()
        self._save_df(df2)


    
