from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional
import pandas as pd
from pathlib import Path

from domain.entities import Immobilier



class ImmobilierRepository:
    def __init__(self, xlsx_path: str | Path, sheet_name: str = "Immobilier"):
        self.xlsx_path = Path(xlsx_path)
        self.sheet_name = sheet_name
        self._df_cache: Optional[pd.DataFrame] = None  # cache optionnel

    # --------- I/O ---------
    def _load_df(self, force_reload: bool = False) -> pd.DataFrame:
        if self._df_cache is None or force_reload:
            if not self.xlsx_path.exists():
                # créer une "table" vide si fichier absent
                self._df_cache = pd.DataFrame(columns=[
                    "ID IMMOBILIER", "ID SCENARIO", "ID USER", "ID COMPTE", "ID CREDIT", "ID ACHAT", "ID VENTE", "PRIX ACHAT", "TITRE", "LOCALISATION", "SURFACE", "TYPE", "COMPTANT (%)", "VALORISATION (%/AN)", "DATE ACHAT", "DATE VENTE", "ETAT"
                ])
            else:
                self._df_cache = pd.read_excel(self.xlsx_path, sheet_name=self.sheet_name)
                # normalisation basique
                if "ID IMMOBILIER" in self._df_cache.columns:
                    self._df_cache["ID IMMOBILIER"] = pd.to_numeric(self._df_cache["ID IMMOBILIER"], errors="coerce").astype("Int64")
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
  
    def _rows_to_immo(self, rows: pd.DataFrame) -> Immobilier:
        def s(x):
            return "" if pd.isna(x) else str(x)
        # normalisation
        if isinstance(rows, pd.Series):
            rows = rows.to_frame().T

        immos = []
        
        for _, row in rows.iterrows():
            immo = Immobilier( 
                    id=int(row["ID IMMOBILIER"]),
                    id_scenario= 0 if pd.isna(row.get("ID SCENARIO")) else int(row["ID SCENARIO"]),
                    id_user= int(row["ID USER"]),
                    id_compte= 0 if pd.isna(row.get("ID COMPTE")) else int(row["ID COMPTE"]),
                    id_credit= None if pd.isna(row.get("ID CREDIT")) else int(row["ID CREDIT"]),
                    id_achat= None if pd.isna(row.get("ID ACHAT")) else int(row["ID ACHAT"]),
                    id_vente= None if pd.isna(row.get("ID VENTE")) else int(row["ID VENTE"]),
                    titre= s(row["TITRE"]),
                    localisation= s(row["LOCALISATION"]),
                    surface= int(row["SURFACE"]),
                    type= s(row["TYPE"]),
                    etat= s(row["ETAT"]),
                    prix_achat= 0 if pd.isna(row.get("PRIX ACHAT")) else int(row["PRIX ACHAT"]),
                    comptant_pct=0 if pd.isna(row.get("COMPTANT (%)")) else float(row["COMPTANT (%)"]),
                    date_in= row["DATE ACHAT"],
                    date_out= None if pd.isna(row.get("DATE VENTE")) else row["DATE VENTE"],
                    valorisation_annuelle_pct= 0 if pd.isna(row.get("VALORISATION (%/AN)")) else float(row["VALORISATION (%/AN)"])
                    )
            immos.append(immo)
        return immos

    # --------- getters ---------
    def get_by_ID(self, immo_ID: int) -> Immobilier:
        df = self._load_df()
        row = df[df["ID IMMOBILIER"] == immo_ID]
        if row.empty:
            return None
        return self._rows_to_immo(row.iloc[0])[0]

    def get_by_userID(self, userID: str) -> Immobilier:
        df = self._load_df()
        row = df[df["username"] == userID]
        if row.empty:
            return None
        
        return self._rows_to_immo(row.iloc[::])
    
    def get_by_(self, dict_str_int : dict[str, int]) -> list[Immobilier]:
        df = self._load_df()
        for by_str, by_id in dict_str_int.items():
            df = df[df[by_str] == by_id]
            if df.empty:
                return []
        row = df
        return self._rows_to_immo(row.iloc[::])

    # --------- writes ---------
    def create(self, immo: dict[str, Any]) -> dict[str, Any]:
        df = self._load_df()
        if "ID IMMOBILIER" not in immo or immo["ID IMMOBILIER"] is None:
            next_ID = int(df["ID IMMOBILIER"].max()) + 1 if (len(df) and df["ID IMMOBILIER"].notna().any()) else 1
            immo["ID IMMOBILIER"] = next_ID

        new_id =immo["ID IMMOBILIER"]
        immo_df = pd.DataFrame([immo])
        df = pd.concat([df, immo_df], ignore_index=True)
        self._save_df(df)

        saved_row = df[df["ID IMMOBILIER"] == new_id]
        return self._rows_to_immo(saved_row)[0]
    
    def update(self, immo_ID: int, patch: dict[str, Any]) -> dict[str, Any]:
        df = self._load_df()

        IDx = df.index[df["ID IMMOBILIER"] == immo_ID]
        if len(IDx) == 0:
            raise ValueError("Immobilier introuvable")

        i = IDx[0]
        for k, v in patch.items():
            if k == "ID IMMOBILIER":
                continue
            print("UPDATE", k, "=>", v, "type:", type(v))
            df.at[i, k] = v

        self._save_df(df)
        return self._rows_to_immo(df.loc[i])[0]

    def delete(self, immo_ID: int) -> None:
        df = self._load_df()
        df2 = df[df["ID IMMOBILIER"] != immo_ID].copy()
        self._save_df(df2)
