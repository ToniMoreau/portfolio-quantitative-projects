from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional
import pandas as pd
from pathlib import Path

from domain.banque import Crédit

class CreditcRepository:
    def __init__(self, xlsx_path: str | Path, sheet_name: str = "Crédits"):
        self.xlsx_path = Path(xlsx_path)
        self.sheet_name = sheet_name
        self._df_cache: Optional[pd.DataFrame] = None  # cache optionnel

    # --------- I/O ---------
    def _load_df(self, force_reload: bool = False) -> pd.DataFrame:
        if self._df_cache is None or force_reload:
            if not self.xlsx_path.exists():
                # créer une "table" vide si fichier absent
                self._df_cache = pd.DataFrame(columns=[
                    "ID CREDIT", "ID BANQUE", "ID USER", "ID COMPTE", "MONTANT", "DUREE DIFF (MOIS)", "DUREE (MOIS)", "MENSUALITE (€)", "TAUX (%)", "TYPE"
                ])
            else:
                self._df_cache = pd.read_excel(self.xlsx_path, sheet_name=self.sheet_name)
                # normalisation basique
                if "ID CREDIT" in self._df_cache.columns:
                    self._df_cache["ID CREDIT"] = pd.to_numeric(self._df_cache["ID CREDIT"], errors="coerce").astype("Int64")
                if "DATE IN" in self._df_cache.columns:
                    self._df_cache["DATE IN"] = pd.to_datetime(self._df_cache["DATE IN"]).dt.date
                if "DATE OUT" in self._df_cache.columns:
                    self._df_cache["DATE OUT"] = pd.to_datetime(self._df_cache["DATE OUT"]).dt.date

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
        
    def _rows_to_credit(self, rows: pd.DataFrame) -> list[Crédit]:
        def s(x):
            return "" if pd.isna(x) else str(x)
        # normalisation
        if isinstance(rows, pd.Series):
            rows = rows.to_frame().T

        credits = []
        for _, row in rows.iterrows():
            credit = Crédit(
                id=int(row["ID CREDIT"]),
                id_banque= int(row["ID BANQUE"]), 
                id_utilisateur= int(row["ID USER"]), 
                id_compte= 0 if pd.isna(row.get("ID COMPTE")) else int(row["ID COMPTE"]),
                id_depense=0 if pd.isna(row.get("ID DEPENSE")) else int(row["ID DEPENSE"]),
                montant= int(row["MONTANT"]),
                duree_diff_mois= int(row["DUREE DIFF (MOIS)"]),
                durée_crédit_mois = None if pd.isna(row["DUREE (MOIS)"]) else int(row["DUREE (MOIS)"]),                
                mensualite_constante= None if pd.isna(row["MENSUALITE (€)"]) else int(row["MENSUALITE (€)"]),               
                taux_crédit_pct= float(row["TAUX (%)"]),
                type = s(row["TYPE"]), #Annuité constante ou Remboursement constant
                debut= row["DATE IN"],
                fin = row["DATE OUT"]
            )
            credits.append(credit)

        return credits

    # --------- getters ---------
    def get_by_ID(self, credit_ID: int) -> Crédit:
        df = self._load_df()
        row = df[df["ID CREDIT"] == credit_ID]
        if row.empty:
            return None
        return self._rows_to_credit(row.iloc[0])[0]

    def get_by_userID(self, userID: str) -> list[Crédit]:
        df = self._load_df()
        row = df[df["ID USER"] == userID]
        if row.empty:
            return None
        
        return self._rows_to_credit(row.iloc[::])

    def get_by_(self, dict_str_int : dict[str, int]) -> list[Crédit]:
        df = self._load_df()
        for by_str, by_id in dict_str_int.items():
            df = df[df[by_str] == by_id]
            if df.empty:
                return None
        row = df
        return self._rows_to_credit(row.iloc[::])

    # --------- writes ---------
    def create(self, credit: dict[str, Any]) -> dict[str, Any]:
        """
        ID CREDIT sera généré si absent.
        """
        df = self._load_df()

        if "ID CREDIT" not in credit or credit["ID CREDIT"] is None:
            next_ID = int(df["ID CREDIT"].max()) + 1 if (len(df) and df["ID CREDIT"].notna().any()) else 1
            credit["ID CREDIT"] = next_ID
        credit = pd.DataFrame([credit])
        df = pd.concat([df, credit ], ignore_index=True)
        self._save_df(df)
        
        return self._rows_to_credit(credit)[0]

    def update(self, credit_ID: int, patch: dict[str, Any]) -> dict[str, Any]:
        df = self._load_df()

        IDx = df.index[df["ID CREDIT"] == credit_ID]
        if len(IDx) == 0:
            raise ValueError("Utilisateur introuvable")

        i = IDx[0]
        for k, v in patch.items():
            if k == "ID CREDIT":
                continue
            print("UPDATE", k, "=>", v, "type:", type(v))
            df.at[i, k] = v

        self._save_df(df)
        return self._rows_to_credit(df.iloc[i])[0]

    def delete(self, credit_ID: int) -> None:
        df = self._load_df()
        df2 = df[df["ID CREDIT"] != credit_ID].copy()
        self._save_df(df2)
