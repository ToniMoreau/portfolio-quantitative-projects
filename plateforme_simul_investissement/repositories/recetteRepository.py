from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional
import pandas as pd
from pathlib import Path

from domain import Recette

class RecetteRepository:
    def __init__(self, xlsx_path: str | Path, sheet_name: str = "Recettes"):
        self.xlsx_path = Path(xlsx_path)
        self.sheet_name = sheet_name
        self._df_cache: Optional[pd.DataFrame] = None  # cache optionnel

    # --------- I/O ---------
    def _load_df(self, force_reload: bool = False) -> pd.DataFrame:
        if self._df_cache is None or force_reload:
            if not self.xlsx_path.exists():
                # créer une "table" vide si fichier absent
                self._df_cache = pd.DataFrame(columns=[
                    "ID RECETTE", "ID SCENARIO", "ID USER", "ID COMPTE", "INTITULE", "MONTANT", "FREQUENCE", "NATURE"
                ])
            else:
                self._df_cache = pd.read_excel(self.xlsx_path, sheet_name=self.sheet_name)
                # normalisation basique
                if "ID RECETTE" in self._df_cache.columns:
                    self._df_cache["ID RECETTE"] = pd.to_numeric(self._df_cache["ID RECETTE"], errors="coerce").astype("Int64")
        return self._df_cache

    def _save_df(self, df: pd.DataFrame) -> None:
        # écriture complète de la feuille (simple + fiable)
        with pd.ExcelWriter(
            self.xlsx_path,
            engine="openpyxl",
            mode="a",
            if_sheet_exists="replace"   # remplace seulement la feuille Scénarios
        ) as writer:
            df.to_excel(writer, sheet_name=self.sheet_name, index=False)
        self._df_cache = df    
        
    def _rows_to_recette(self, rows: pd.DataFrame) -> list[Recette]:
        def s(x):
            return "" if pd.isna(x) else str(x)
        # normalisation
        if isinstance(rows, pd.Series):
            rows = rows.to_frame().T

        recettes = []

        for _, row in rows.iterrows():
            recette = Recette(
                id= int(row["ID RECETTE"]),
                id_user= int(row["ID USER"]),
                intitule= s(row["INTITULE"]),
                id_compte= int(row["ID COMPTE"]),
                id_scenario= int(row["ID SCENARIO"]),
                frequence= s(row["FREQUENCE"]),
                nature= s(row["NATURE"]),
                montant= float(row["MONTANT"])
            )
            recettes.append(recette)

        return recettes

    # --------- getters ---------
    def get_by_ID(self, recette_ID: int) -> Recette:
        df = self._load_df()
        row = df[df["ID RECETTE"] == recette_ID]
        if row.empty:
            return None
        return self._rows_to_recette(row.iloc[0])[0]

    def get_by_userID(self, userID: str) -> list[Recette]:
        df = self._load_df()
        row = df[df["ID USER"] == userID]
        if row.empty:
            return None
        
        return self._rows_to_recette(row.iloc[::])
    
    def get_by_(self, dict_str_int : dict[str, int]) -> list[Recette]:
        df = self._load_df()
        for by_str, by_id in dict_str_int.items():
            df = df[df[by_str] == by_id]
            if df.empty:
                return []
        row = df
        return self._rows_to_recette(row.iloc[::])

    # --------- writes ---------
    def create(self, recette: dict[str, Any]) -> dict[str, Any]:
        """
        ID RECETTE sera généré si absent.
        """
        df = self._load_df()

        if "ID RECETTE" not in recette or recette["ID RECETTE"] is None:
            next_ID = int(df["ID RECETTE"].max()) + 1 if (len(df) and df["ID RECETTE"].notna().any()) else 1
            recette["ID RECETTE"] = next_ID
        recette = pd.DataFrame([recette])
        df = pd.concat([df, recette ], ignore_index=True)
        self._save_df(df)
        
        return self._rows_to_recette(recette)[0]

    def update(self, recette_ID: int, patch: dict[str, Any]) -> dict[str, Any]:
        df = self._load_df()

        IDx = df.index[df["ID RECETTE"] == recette_ID]
        if len(IDx) == 0:
            raise ValueError("recette introuvable")

        i = IDx[0]
        for k, v in patch.items():
            if k == "ID RECETTE":
                continue
            print("UPDATE", k, "=>", v, "type:", type(v))
            df.at[i, k] = v

        self._save_df(df)
        return self._rows_to_recette(df.iloc[i])[0]

    def delete(self, recette_ID: int) -> None:
        df = self._load_df()
        df2 = df[df["ID RECETTE"] != recette_ID].copy()
        self._save_df(df2)
