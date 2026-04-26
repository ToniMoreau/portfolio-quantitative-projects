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
  
    def _rows_to_invest(self, rows: pd.DataFrame) -> Investissement:
        def s(x):
            return "" if pd.isna(x) else str(x)
        # normalisation
        if isinstance(rows, pd.Series):
            rows = rows.to_frame().T

        invests = []
        
        for _, row in rows.iterrows():
            invest = Investissement( 
                    id=int(row["ID INVESTISSEMENT"]),
                    id_user=int(row["ID COMPTE"]),
                    id_scenario= 0 if pd.isna(row.get("ID SCENARIO")) else int(row["ID SCENARIO"]),
                    id_compte= 0 if pd.isna(row.get("ID COMPTE")) else int(row["ID COMPTE"]),
                    id_credit= None if pd.isna(row.get("ID CREDIT")) else int(row["ID CREDIT"]),
                    id_achat= None if pd.isna(row.get("ID ACHAT")) else int(row["ID ACHAT"]),
                    id_vente= None if pd.isna(row.get("ID VENTE")) else int(row["ID VENTE"]),
                    nature= s(row["NATURE"]),
                    etat= s(row["ETAT"]),
                    prix_achat= 0 if pd.isna(row.get("PRIX ACHAT")) else int(row["PRIX ACHAT"]),
                    comptant_pct=0 if pd.isna(row.get("COMPTANT (%)")) else int(row["COMPTANT (%)"]),
                    date_in= row["DATE ACHAT"],
                    date_out= None if pd.isna(row.get("DATE VENTE")) else int(row["DATE VENTE"]),
                    valorisation_annuelle_pct= 0 if pd.isna(row.get("VALORISATION (%/AN)")) else int(row["VALORISATION (%/AN)"])
                    )
            invests.append(invest)
        return invests

    # --------- getters ---------
    def get_by_ID(self, invest_ID: int) -> Investissement:
        df = self._load_df()
        row = df[df["ID INVESTISSEMENT"] == invest_ID]
        if row.empty:
            return None
        return self._rows_to_invest(row.iloc[0])[0]

    def get_by_userID(self, userID: str) -> Investissement:
        df = self._load_df()
        row = df[df["username"] == userID]
        if row.empty:
            return None
        
        return self._rows_to_invest(row.iloc[::])
    
    def get_by_(self, dict_str_int : dict[str, int]) -> list[Investissement]:
        df = self._load_df()
        for by_str, by_id in dict_str_int.items():
            df = df[df[by_str] == by_id]
            if df.empty:
                return []
        row = df
        return self._rows_to_invest(row.iloc[::])

    # --------- writes ---------
    def create(self, invest: dict[str, Any]) -> dict[str, Any]:
        """
        user doit contenir au minimum: username, password_hash
        ID INVESTISSEMENT sera généré si absent.
        """
        df = self._load_df()


        if "ID INVESTISSEMENT" not in invest or invest["ID INVESTISSEMENT"] is None:
            next_ID = int(df["ID INVESTISSEMENT"].max()) + 1 if (len(df) and df["ID INVESTISSEMENT"].notna().any()) else 1
            invest["ID INVESTISSEMENT"] = next_ID
        invest = pd.DataFrame([invest])
        df = pd.concat([df, invest], ignore_index=True)
        self._save_df(df)
        return self._rows_to_invest(invest)[0]

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
        return self._rows_to_invest(df.iloc[i])[0]

    def delete(self, invest_ID: int) -> None:
        df = self._load_df()
        df2 = df[df["ID INVESTISSEMENT"] != invest_ID].copy()
        self._save_df(df2)
