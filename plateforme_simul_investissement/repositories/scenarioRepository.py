from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional
import pandas as pd
from pathlib import Path

from domain import Scenario

class ScenarioRepository:
    def __init__(self, xlsx_path: str | Path, sheet_name: str = "Scénarios"):
        self.xlsx_path = Path(xlsx_path)
        self.sheet_name = sheet_name
        self._df_cache: Optional[pd.DataFrame] = None  # cache optionnel

    # --------- I/O ---------
    def _load_df(self, force_reload: bool = False) -> pd.DataFrame:
        if self._df_cache is None or force_reload:
            if not self.xlsx_path.exists():
                # créer une "table" vide si fichier absent
                self._df_cache = pd.DataFrame(columns=[
                    "ID SCENARIO", "ID USER", "INTITULE"
                ])
            else:
                self._df_cache = pd.read_excel(self.xlsx_path, sheet_name=self.sheet_name)
                # normalisation basique
                if "ID SCENARIO" in self._df_cache.columns:
                    self._df_cache["ID SCENARIO"] = pd.to_numeric(self._df_cache["ID SCENARIO"], errors="coerce").astype("Int64")
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
        
    def _rows_to_scenario(self, rows: pd.DataFrame) -> list[Scenario]:
        def s(x):
            return "" if pd.isna(x) else str(x)
        # normalisation
        if isinstance(rows, pd.Series):
            rows = rows.to_frame().T

        scenarios = []

        for _, row in rows.iterrows():
            scenario = Scenario(
                id= int(row["ID SCENARIO"]),
                id_user= int(row["ID USER"]),
                intitule= s(row["INTITULE"])
            )
            scenarios.append(scenario)

        return scenarios

    # --------- getters ---------
    def get_by_ID(self, scenario_ID: int) -> Scenario:
        df = self._load_df()
        row = df[df["ID SCENARIO"] == scenario_ID]
        if row.empty:
            return None
        return self._rows_to_scenario(row.iloc[0])[0]

    def get_by_userID(self, userID: str) -> list[Scenario]:
        df = self._load_df()
        row = df[df["ID USER"] == userID]
        if row.empty:
            return None
        
        return self._rows_to_scenario(row.iloc[::])

    # --------- writes ---------
    def create(self, scenario: dict[str, Any]) -> dict[str, Any]:
        """
        ID SCENARIO sera généré si absent.
        """
        df = self._load_df()

        if "ID SCENARIO" not in scenario or scenario["ID SCENARIO"] is None:
            next_ID = int(df["ID SCENARIO"].max()) + 1 if (len(df) and df["ID SCENARIO"].notna().any()) else 1
            scenario["ID SCENARIO"] = next_ID
        scenario = pd.DataFrame([scenario])
        df = pd.concat([df, scenario ], ignore_index=True)
        self._save_df(df)
        
        return self._rows_to_scenario(scenario)[0]

    def update(self, scenario_ID: int, patch: dict[str, Any]) -> dict[str, Any]:
        df = self._load_df()

        IDx = df.index[df["ID SCENARIO"] == scenario_ID]
        if len(IDx) == 0:
            raise ValueError("Scenario introuvable")

        i = IDx[0]
        for k, v in patch.items():
            if k == "ID SCENARIO":
                continue
            print("UPDATE", k, "=>", v, "type:", type(v))
            df.at[i, k] = v

        self._save_df(df)
        return self._rows_to_scenario(df.iloc[i])[0]

    def delete(self, scenario_ID: int) -> None:
        df = self._load_df()
        df2 = df[df["ID SCENARIO"] != scenario_ID].copy()
        self._save_df(df2)
