from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional
import pandas as pd
from pathlib import Path

from domain.entities import Depense

class DepenseRepository:
    def __init__(self, xlsx_path: str | Path, sheet_name: str = "Dépenses"):
        self.xlsx_path = Path(xlsx_path)
        self.sheet_name = sheet_name
        self._df_cache: Optional[pd.DataFrame] = None  # cache optionnel

    # --------- I/O ---------
    def _load_df(self, force_reload: bool = False) -> pd.DataFrame:
        if self._df_cache is None or force_reload:
            if not self.xlsx_path.exists():
                # créer une "table" vide si fichier absent
                self._df_cache = pd.DataFrame(columns=[
                    "ID DEPENSE", "ID TRANSACTION", "ID SCENARIO", "ID USER", "ID COMPTE", "ID SOURCE", "DATE IN", "DATE OUT", "INTITULE", "NATURE", "MONTANT", "FREQUENCE", "INDEXATION"
                ])
            else:
                self._df_cache = pd.read_excel(self.xlsx_path, sheet_name=self.sheet_name)
                # normalisation basique
                if "ID DEPENSE" in self._df_cache.columns:
                    self._df_cache["ID DEPENSE"] = pd.to_numeric(self._df_cache["ID DEPENSE"], errors="coerce").astype("Int64")
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
            if_sheet_exists="replace"   # remplace seulement la feuille Scénarios
        ) as writer:
            df.to_excel(writer, sheet_name=self.sheet_name, index=False)
        self._df_cache = df    
        
    def _rows_to_depense(self, rows: pd.DataFrame) -> list[Depense]:
        def s(x):
            return "" if pd.isna(x) else str(x)
        # normalisation
        if isinstance(rows, pd.Series):
            rows = rows.to_frame().T

        depenses = []

        for _, row in rows.iterrows():
            depense = Depense(
                id= int(row["ID DEPENSE"]),
                id_user= int(row["ID USER"]),
                id_transaction= None if pd.isna(row.get("ID TRANSACTION")) else int(row["ID TRANSACTION"]),
                intitule= s(row["INTITULE"]),
                id_compte= int(row["ID COMPTE"]),
                id_scenario= int(row["ID SCENARIO"]),
                id_source= None if pd.isna(row.get("ID SOURCE")) else int(row["ID SOURCE"]),
                frequence= s(row["FREQUENCE"]),
                nature= s(row["NATURE"]),
                montant= float(row["MONTANT"]),
                date_in= row["DATE IN"],
                date_out= row["DATE OUT"],
                indexation= 0 if pd.isna(row.get("INDEXATION")) else float(row["INDEXATION"])
            )
            depenses.append(depense)

        return depenses

    # --------- getters ---------
    def get_by_ID(self, depense_ID: int) -> Depense:
        df = self._load_df()
        row = df[df["ID DEPENSE"] == depense_ID]
        if row.empty:
            return None
        return self._rows_to_depense(row.iloc[0])[0]

    def get_by_userID(self, userID: str) -> list[Depense]:
        df = self._load_df()
        row = df[df["ID USER"] == userID]
        if row.empty:
            return None
        
        return self._rows_to_depense(row.iloc[::])
    
    def get_by_(self, dict_str_int : dict[str, int]) -> list[Depense]:
        df = self._load_df()
        for by_str, by_id in dict_str_int.items():
            df = df[df[by_str] == by_id]
            if df.empty:
                return None
        row = df
        return self._rows_to_depense(row.iloc[::])


    # --------- writes ---------
    def create(self, depense: dict[str, Any], is_transaction : bool | None = None) -> dict[str, Any]:
        """
        ID DEPENSE sera généré si absent.
        """
        df = self._load_df()

        if "ID DEPENSE" not in depense or depense["ID DEPENSE"] is None:
            next_ID = int(df["ID DEPENSE"].max()) + 1 if (len(df) and df["ID DEPENSE"].notna().any()) else 1
            depense["ID DEPENSE"] = next_ID
        
        if is_transaction:
            next_ID = int(df["ID TRANSACTION"].max()) + 1 if (len(df) and df["ID TRANSACTION"].notna().any()) else 1
            depense["ID TRANSACTION"] = next_ID
        new_id =depense["ID DEPENSE"]
        depense = pd.DataFrame([depense])
        df = pd.concat([df, depense ], ignore_index=True)
        self._save_df(df)
        
        saved_row = df[df["ID DEPENSE"] == new_id]
        return self._rows_to_depense(saved_row)[0]

    def update(self, depense_ID: int, patch: dict[str, Any]) -> dict[str, Any]:
        df = self._load_df()

        IDx = df.index[df["ID DEPENSE"] == depense_ID]
        if len(IDx) == 0:
            raise ValueError("depense introuvable")

        i = IDx[0]
        for k, v in patch.items():
            if k == "ID DEPENSE":
                continue
            print("UPDATE", k, "=>", v, "type:", type(v))
            df.at[i, k] = v

        self._save_df(df)
        return self._rows_to_depense(df.iloc[i])[0]

    def delete(self, depense_ID: int) -> None:
        df = self._load_df()
        df2 = df[df["ID DEPENSE"] != depense_ID].copy()
        self._save_df(df2)
