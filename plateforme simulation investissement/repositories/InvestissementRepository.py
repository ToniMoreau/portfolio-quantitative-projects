from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional
import pandas as pd
from pathlib import Path

from domain.investissement import Investissement



class InvestissementRepository:
    def __init__(self, xlsx_path: str | Path, sheet_name: str = "Investissements"):
        self.xlsx_path = Path(xlsx_path)
        self.sheet_name = sheet_name
        self._df_cache: Optional[pd.DataFrame] = None  # cache optionnel

    # --------- I/O ---------
    def _load_df(self, force_reload: bool = False) -> pd.DataFrame:
        if self._df_cache is None or force_reload:
            if not self.xlsx_path.exists():
                # créer une "table" vide si fichier absent
                self._df_cache = pd.DataFrame(columns=[
                    "ID INVESTISSEMENT", "ID USER", "VALEUR (€)", "DATE CREATION", "DATE FIN", "AUGMENTATION (€/AN)"
                ])
            else:
                self._df_cache = pd.read_excel(self.xlsx_path, sheet_name=self.sheet_name)
                # normalisation basique
                if "ID INVESTISSEMENT" in self._df_cache.columns:
                    self._df_cache["ID INVESTISSEMENT"] = pd.to_numeric(self._df_cache["ID INVESTISSEMENT"], errors="coerce").astype("Int64")
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
        
    def _row_to_invest(self, row: pd.Series) -> Investissement:
        # robustesse NaN
        def s(x): 
            return "" if pd.isna(x) else str(x)
        return Investissement(
            id=int(row["ID INVESTISSEMENT"]),

        )        

    # --------- getters ---------
    def get_by_ID(self, invest_ID: int) -> Investissement:
        df = self._load_df()
        row = df[df["ID INVESTISSEMENT"] == invest_ID]
        if row.empty:
            return None
        return self._row_to_invest(row.iloc[0])

    def get_by_userID(self, userID: str) -> Investissement:
        df = self._load_df()
        row = df[df["username"] == userID]
        if row.empty:
            return None
        
        return self._row_to_invest(row.iloc[0])

    # --------- writes ---------
    def create(self, user: dict[str, Any]) -> dict[str, Any]:
        """
        user doit contenir au minimum: username, password_hash
        ID INVESTISSEMENT sera généré si absent.
        """
        df = self._load_df()


        if "ID INVESTISSEMENT" not in user or user["ID INVESTISSEMENT"] is None:
            next_ID = int(df["ID"].max()) + 1 if (len(df) and df["ID"].notna().any()) else 1
            user["ID INVESTISSEMENT"] = next_ID

        df = pd.concat([df, pd.DataFrame([user])], ignore_index=True)
        self._save_df(df)
        return self._row_to_invest(user)

    def update(self, invest_ID: int, patch: dict[str, Any]) -> dict[str, Any]:
        df = self._load_df()

        IDx = df.index[df["ID INVESTISSEMENT"] == invest_ID]
        if len(IDx) == 0:
            raise ValueError("Investissement introuvable")

        i = IDx[0]
        for k, v in patch.items():
            if k == "ID INVESTISSEMENT":
                continue
            print("UPDATE", k, "=>", v, "type:", type(v))
            df.at[i, k] = v

        self._save_df(df)
        return self._row_to_invest(df.iloc[i])

    def delete(self, invest_ID: int) -> None:
        df = self._load_df()
        df2 = df[df["ID INVESTISSEMENT"] != invest_ID].copy()
        self._save_df(df2)
