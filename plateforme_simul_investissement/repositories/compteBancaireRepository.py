from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional
import pandas as pd
from pathlib import Path

from domain.banque import CompteBancaire


class CompteBancaireRepository:
    def __init__(self, xlsx_path: str | Path, sheet_name: str = "Comptes"):
        self.xlsx_path = Path(xlsx_path)
        self.sheet_name = sheet_name
        self._df_cache: Optional[pd.DataFrame] = None  # cache optionnel

    # --------- I/O ---------
    def _load_df(self, force_reload: bool = False) -> pd.DataFrame:
        if self._df_cache is None or force_reload:
            if not self.xlsx_path.exists():
                # créer une "table" vide si fichier absent
                self._df_cache = pd.DataFrame(columns=[
                    "ID COMPTE", "ID USER", "TYPE", "MONTANT", "TAUX", "MIN","MAX"
                ])
            else:
                self._df_cache = pd.read_excel(self.xlsx_path, sheet_name=self.sheet_name)
                # normalisation basique
                if "ID COMPTE" in self._df_cache.columns:
                    self._df_cache["ID COMPTE"] = pd.to_numeric(self._df_cache["ID COMPTE"], errors="coerce").astype("Int64")
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
        
    def _rows_to_compteBancaire(self, rows: pd.DataFrame) -> list[CompteBancaire]:
        def s(x):
            return "" if pd.isna(x) else str(x)
        # normalisation
        if isinstance(rows, pd.Series):
            rows = rows.to_frame().T

        cbs = []

        for _, row in rows.iterrows():
            cb = CompteBancaire(
                id=int(row["ID COMPTE"]),
                id_banque=int(row["ID BANQUE"]),
                id_utilisateur=int(row["ID USER"]),
                montant=float(row["MONTANT"]),
                type=s(row.get("TYPE"))
            )
            cbs.append(cb)

        return cbs
    # --------- getters ---------
    def get_by_ID(self, compte_ID: int) -> CompteBancaire:
        df = self._load_df()
        row = df[df["ID COMPTE"] == compte_ID]
        if row.empty:
            return None
        return self._rows_to_compteBancaire(row.iloc[0])[0]

    def get_by_userID(self, userID: str) -> list[CompteBancaire]:
        df = self._load_df()
        row = df[df["ID USER"] == userID]
        if row.empty:
            return None
        return self._rows_to_compteBancaire(row.iloc[::])
    
    def get_by_banqueID(self, banqueID: str) -> list[CompteBancaire]:
        df = self._load_df()
        row = df[df["ID BANQUE"] == banqueID]
        if row.empty:
            return None
        
        return self._rows_to_compteBancaire(row.iloc[::])
    
    def get_by_(self, dict_str_int : dict[str, int]) -> CompteBancaire:
        df = self._load_df()
        for by_str, by_id in dict_str_int.items():
            df = df[df[by_str] == by_id]
            if df.empty:
                return []
        row = df
        return self._rows_to_compteBancaire(row.iloc[::])


    # --------- writes ---------
    def create(self, compteBancaire: dict[str, Any]) -> dict[str, Any]:
        """
        user doit contenir au minimum: username, password_hash
        ID COMPTE sera généré si absent.
        """
        df = self._load_df()

        if "ID COMPTE" not in compteBancaire or compteBancaire["ID COMPTE"] is None:
            next_ID = int(df["ID COMPTE"].max()) + 1 if (len(df) and df["ID COMPTE"].notna().any()) else 1
            compteBancaire["ID COMPTE"] = next_ID

        compteBancaire = pd.DataFrame([compteBancaire])
        df = pd.concat([df,compteBancaire], ignore_index=True)
        self._save_df(df)
        return self._rows_to_compteBancaire(compteBancaire)[0]

    def update(self, compte_ID: int, patch: dict[str, Any]) -> dict[str, Any]:
        df = self._load_df()

        IDx = df.index[df["ID COMPTE"] == compte_ID]
        if len(IDx) == 0:
            raise ValueError("compte introuvable")

        i = IDx[0]
        for k, v in patch.items():
            if k == "ID COMPTE":
                continue
            print("UPDATE", k, "=>", v, "type:", type(v))
            df.at[i, k] = v

        self._save_df(df)
        print("df", df.iloc[i] )
        return self._rows_to_compteBancaire(df.iloc[i])[0]

    def delete(self, compte_ID: int) -> None:
        df = self._load_df()
        df2 = df[df["ID COMPTE"] != compte_ID].copy()
        self._save_df(df2)

