from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional
import pandas as pd
from pathlib import Path

from domain.profil_pro import Profil_pro, Salarié
class MetierRepository:
    def __init__(self, xlsx_path: str | Path, sheet_name: str = "Metiers"):
        self.xlsx_path = Path(xlsx_path)
        self.sheet_name = sheet_name
        self._df_cache: Optional[pd.DataFrame] = None  # cache optionnel

    # --------- I/O ---------
    def _load_df(self, force_reload: bool = False) -> pd.DataFrame:
        if self._df_cache is None or force_reload:
            if not self.xlsx_path.exists():
                # créer une "table" vide si fichier absent
                self._df_cache = pd.DataFrame(columns=[
                    "ID METIER", "ID SCENARIO","ID USER", "ID COMPTE", "INTITULE", "ANCIENNETE (ANNEE)", "ANNUEL BRUT (€/AN)", "ANNUEL NET (€/AN)", 
                    "PRIMES (€/AN) ", "BONUS (%/AN)", "AUGMENTATION  (%/AN)", "FREQUENCE 1 (ANNEE)", "AUGMENT. (%/F1)", "PRIVE"
                ])
            else:
                self._df_cache = pd.read_excel(self.xlsx_path, sheet_name=self.sheet_name)
                # normalisation basique
                if "ID METIER" in self._df_cache.columns:
                    self._df_cache["ID METIER"] = pd.to_numeric(self._df_cache["ID METIER"], errors="coerce").astype("Int64")
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
         
    def _row_to_profils_pros(self, rows: pd.DataFrame) -> list[Salarié]:
        def s(x):
            return "" if pd.isna(x) else str(x)
        # normalisation
        if isinstance(rows, pd.Series):
            rows = rows.to_frame().T

        profils_pros = []

        for _, row in rows.iterrows():
            profil_pro = Salarié(
            id_metier=int(row["ID METIER"]),
            intitule_métier= s(row["INTITULE"]),
            id_compte= int(row["ID COMPTE"]),
            id_recette= int(row["ID SALAIRE"]), #
            annuel_brut= float(row["ANNUEL BRUT (€/AN)"]),
            privé= s(row["PRIVE"]),
            date_in= row["DATE IN"],
            date_out= row["DATE OUT"], 
            annuel_net= row["ANNUEL NET (€/AN)"], #
            prélèvement_source_pct= float(row["PAS (%)"]) #
            )        

            profils_pros.append(profil_pro)

        return profils_pros

    # --------- getters ---------
    def get_by_ID(self, metier_ID: int) -> Salarié:
        df = self._load_df()
        row = df[df["ID METIER"] == metier_ID]
        if row.empty:
            return None
        return self._row_to_profils_pros(row.iloc[0])[0]
    
    def get_by_(self, dict_str_int : dict[str, int]) -> list[Salarié]:
        df = self._load_df()
        for by_str, by_id in dict_str_int.items():
            df = df[df[by_str] == by_id]
            if df.empty:
                return None
        row = df
        return self._row_to_profils_pros(row.iloc[::])
    

    def get_by_userID(self, userID: str) -> list[Salarié]:
        df = self._load_df()
        row = df[df["ID USER"] == userID]
        if row.empty:
            return []
        return self._row_to_profils_pros(row.iloc[::])

    # --------- writes ---------
    def create(self, metier: dict[str, Any]) -> dict[str, Any]:
        """
        user doit contenir au minimum: username, password_hash
        ID METIER sera généré si absent.
        """
        df = self._load_df()

        if "ID METIER" not in metier or metier["ID METIER"] is None:
            next_ID = int(df["ID METIER"].max()) + 1 if (len(df) and df["ID METIER"].notna().any()) else 1
            metier["ID METIER"] = next_ID
        metier = pd.DataFrame([metier])
        df = pd.concat([df, metier], ignore_index=True)
        self._save_df(df)
        return self._row_to_profils_pros(metier)[0]

    def update(self, metier_ID: int, patch: dict[str, Any]) -> dict[str, Any]:
        df = self._load_df()

        IDx = df.index[df["ID METIER"] == metier_ID]
        if len(IDx) == 0:
            raise ValueError("Utilisateur introuvable")

        i = IDx[0]
        for k, v in patch.items():
            if k == "ID METIER":
                continue
            print("UPDATE", k, "=>", v, "type:", type(v))
            df.at[i, k] = v

        self._save_df(df)
        return self._row_to_profils_pros(df.iloc[i])[0]

    def delete(self, metier_ID: int) -> None:
        df = self._load_df()
        df2 = df[df["ID METIER"] != metier_ID].copy()
        self._save_df(df2)
