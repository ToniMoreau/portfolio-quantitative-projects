from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional
import pandas as pd
from pathlib import Path

from domain.banque import Banque



class BanqueRepository:
    def __init__(self, xlsx_path: str | Path, sheet_name: str = "Banques"):
        self.xlsx_path = Path(xlsx_path)
        self.sheet_name = sheet_name
        self._df_cache: Optional[pd.DataFrame] = None  # cache optionnel
    
    def _load_df(self, force_reload: bool = False) -> pd.DataFrame:
        if self._df_cache is None or force_reload:
            if not self.xlsx_path.exists():
                # créer une "table" vide si fichier absent
                self._df_cache = pd.DataFrame(columns=[
                    "ID BANQUE", "INTITULE", "TAUX CREDIT (%)"
                ])
            else:
                self._df_cache = pd.read_excel(self.xlsx_path, sheet_name=self.sheet_name)
                # normalisation basique
                if "ID BANQUE" in self._df_cache.columns:
                    self._df_cache["ID BANQUE"] = pd.to_numeric(self._df_cache["ID BANQUE"], errors="coerce").astype("Int64")
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
        
    def _row_to_banques(self, rows: pd.DataFrame) -> list[Banque]: 
        def s(x):
            return "" if pd.isna(x) else str(x)
        # normalisation
        if isinstance(rows, pd.Series):
            rows = rows.to_frame().T

        banques = []

        for _, row in rows.iterrows():
            banque = Banque(
                id=int(row["ID BANQUE"]),
                nom = s(row.get("INTITULE", "")),
                taux_credit_pct= float(row["TAUX CREDIT (%)"])
                )                    
            banques.append(banque)
        return banques
    
    # --------- getters ---------
    def get_all_names(self):
        df = self._load_df()
        return df["INTITULE"]
    
    def get_all_banques(self):
        df = self._load_df()
        return self._row_to_banques(df.iloc[::])
    
    def get_by_ID(self, banque_id: int) -> Banque:
        df = self._load_df()
        row = df[df["ID BANQUE"] == banque_id]
        if row.empty:
            return []
        return self._row_to_banques(row.iloc[0])[0]

    def get_by_name(self, banque_intitule: str) -> Banque:
        df = self._load_df()
        row = df[df["INTITULE"] == banque_intitule]
        if row.empty:
            return None
        
        return self._row_to_banques(row.iloc[0])[0]
    
    def exists_name(self, banque_name: str) -> bool:
        print("gbn :", self.get_by_name(banque_name))
        return self.get_by_name(banque_name) is not None
    # --------- writes ---------
    def create(self, banque: dict[str, Any]) -> dict[str, Any]:
        """
        banque doit contenir au minimum: ID BANQUE, INTITULE
        ID sera généré si absent.
        """
        df = self._load_df()

        if self.exists_name(banque["INTITULE"]):
            raise ValueError("Banque déjà existante")

        if "ID BANQUE" not in banque or banque["ID BANQUE"] is None:
            next_ID = int(df["ID BANQUE"].max()) + 1 if (len(df) and df["ID BANQUE"].notna().any()) else 1
            banque["ID BANQUE"] = next_ID
        banque = pd.DataFrame([banque])
        df = pd.concat([df, banque], ignore_index=True)
        self._save_df(df)
        return self._row_to_banques(banque)[0]

    def update(self, banque_ID: int, patch: dict[str, Any]) -> dict[str, Any]:
        df = self._load_df()

        IDx = df.index[df["ID BANQUE"] == banque_ID]
        if len(IDx) == 0:
            raise ValueError("Banque introuvable")

        i = IDx[0]
        for k, v in patch.items():
            if k == "ID BANQUE":
                continue
            print("UPDATE", k, "=>", v, "type:", type(v))
            df.at[i, k] = v

        self._save_df(df)
        return self._row_to_banques(df.iloc[i])[0]

    def delete(self, banque_ID: int) -> None:
        df = self._load_df()
        df2 = df[df["ID BANQUE"] != banque_ID].copy()
        self._save_df(df2)


