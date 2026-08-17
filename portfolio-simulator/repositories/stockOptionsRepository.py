from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional
import pandas as pd
from pathlib import Path

from domain.entities import StockOption



class StockOptionsRepository:
    def __init__(self, xlsx_path: str | Path, sheet_name: str = "StockOptions"):
        self.xlsx_path = Path(xlsx_path)
        self.sheet_name = sheet_name
        self._df_cache: Optional[pd.DataFrame] = None  # cache optionnel

    # --------- I/O ---------
    def _load_df(self, force_reload: bool = False) -> pd.DataFrame:
        if self._df_cache is None or force_reload:
            if not self.xlsx_path.exists():
                # créer une "table" vide si fichier absent
                self._df_cache = pd.DataFrame(columns=[
                    "ID STOCKOPTION", "ID DIVIDENDES",  "ID USER", "ID COMPTE", "ID ACHAT", "ID VENTE", "PRIX ACHAT", "DIVIDENDES (%)", "TITRE", "VALORISATION (%/AN)", "DATE ACHAT", "DATE VENTE", "ETAT"
                ])
            else:
                self._df_cache = pd.read_excel(self.xlsx_path, sheet_name=self.sheet_name)
                # normalisation basique
                if "ID STOCKOPTION" in self._df_cache.columns:
                    self._df_cache["ID STOCKOPTION"] = pd.to_numeric(self._df_cache["ID STOCKOPTION"], errors="coerce").astype("Int64")
                if "DATE ACHAT" in self._df_cache.columns:
                    self._df_cache["DATE ACHAT"] = pd.to_datetime(self._df_cache["DATE ACHAT"]).dt.date
                if "DATE VENTE" in self._df_cache.columns:
                    self._df_cache["DATE VENTE"] = pd.to_datetime(self._df_cache["DATE VENTE"]).dt.date
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
  
    def _rows_to_stockoption(self, rows: pd.DataFrame) -> StockOption:
        def s(x):
            return "" if pd.isna(x) else str(x)
        # normalisation
        if isinstance(rows, pd.Series):
            rows = rows.to_frame().T

        stockoptions = []
        
        for _, row in rows.iterrows():
            stockoption = StockOption( 
                    id=int(row["ID STOCKOPTION"]),
                    id_scenario= 0 if pd.isna(row.get("ID SCENARIO")) else int(row["ID SCENARIO"]),
                    id_user= int(row["ID USER"]),
                    id_compte= 0 if pd.isna(row.get("ID COMPTE")) else int(row["ID COMPTE"]),
                    id_achat= None if pd.isna(row.get("ID ACHAT")) else int(row["ID ACHAT"]),
                    id_vente= None if pd.isna(row.get("ID VENTE")) else int(row["ID VENTE"]),
                    id_dividendes=None if pd.isna(row.get("ID DIVIDENDES")) else int(row["ID DIVIDENDES"]),
                    dividendes_pct=None if pd.isna(row.get("DIVIDENDES (%)")) else int(row["DIVIDENDES (%)"]),
                    titre= s(row["TITRE"]),
                    etat= s(row["ETAT"]),
                    prix_achat= 0 if pd.isna(row.get("PRIX ACHAT")) else int(row["PRIX ACHAT"]),
                    date_in= row["DATE ACHAT"],
                    date_out= None if pd.isna(row.get("DATE VENTE")) else row["DATE VENTE"],
                    valorisation_annuelle_pct= 0 if pd.isna(row.get("VALORISATION (%/AN)")) else float(row["VALORISATION (%/AN)"])
                    )
            stockoptions.append(stockoption)
        return stockoptions

    # --------- getters ---------
    def get_by_ID(self, stockoption_ID: int) -> StockOption:
        df = self._load_df()
        row = df[df["ID STOCKOPTION"] == stockoption_ID]
        if row.empty:
            return None
        return self._rows_to_stockoption(row.iloc[0])[0]

    def get_by_userID(self, userID: str) -> StockOption:
        df = self._load_df()
        row = df[df["username"] == userID]
        if row.empty:
            return None
        
        return self._rows_to_stockoption(row.iloc[::])
    
    def get_by_(self, dict_str_int : dict[str, int]) -> list[StockOption]:
        df = self._load_df()
        for by_str, by_id in dict_str_int.items():
            df = df[df[by_str] == by_id]
            if df.empty:
                return []
        row = df
        return self._rows_to_stockoption(row.iloc[::])

    # --------- writes ---------
    def create(self, stockoption: dict[str, Any]) -> dict[str, Any]:
        """
        user doit contenir au minimum: username, password_hash
        ID STOCKOPTION sera généré si absent.
        """
        df = self._load_df()


        if "ID STOCKOPTION" not in stockoption or stockoption["ID STOCKOPTION"] is None:
            next_ID = int(df["ID STOCKOPTION"].max()) + 1 if (len(df) and df["ID STOCKOPTION"].notna().any()) else 1
            stockoption["ID STOCKOPTION"] = next_ID
            
        new_id = stockoption["ID STOCKOPTION"]
        stockoption = pd.DataFrame([stockoption])
        df = pd.concat([df, stockoption], ignore_index=True)
        self._save_df(df)
        saved_row = df[df["ID STOCKOPTION"] == new_id ]
        return self._rows_to_stockoption(saved_row)[0]

    def update(self, stockoption_ID: int, patch: dict[str, Any]) -> dict[str, Any]:
        df = self._load_df()

        IDx = df.index[df["ID STOCKOPTION"] == stockoption_ID]
        if len(IDx) == 0:
            raise ValueError("STOCKOPTION introuvable")

        i = IDx[0]
        for k, v in patch.items():
            if k == "ID STOCKOPTION":
                continue
            print("UPDATE", k, "=>", v, "type:", type(v))
            df.at[i, k] = v

        self._save_df(df)
        return self._rows_to_stockoption(df.iloc[i])[0]

    def delete(self, stockoption_ID: int) -> None:
        df = self._load_df()
        df2 = df[df["ID STOCKOPTION"] != stockoption_ID].copy()
        self._save_df(df2)
