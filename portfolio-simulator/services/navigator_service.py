from enum import Enum


from enum import Enum
from PySide6.QtCore import QObject, Signal

class NavigatorService(QObject):
    navigation_requested = Signal(object, object)  # (page_key, context)

    def go_to(self, page_key: str, context=None):
        self.navigation_requested.emit(page_key, context)

class Page(Enum):
    # ─────────────────────────────────────────────
    # Ground 0 — owned by MainWindow (top-level worlds)
    # ─────────────────────────────────────────────
    ACCUEIL = "accueil"
    PARAMETRES = "parametres"
    PROFIL = "profil"
    AUTH = "auth"
    BANQUE_STANDALONE = "banque_standalone"   # the admin-only sous_pages/banque one

    # ─────────────────────────────────────────────
    # Ground 1 — owned by ProfilPage (all functional pages)
    # ─────────────────────────────────────────────
    DASHBOARD = "dashboard"
    OUTILS = "outils"
    INFOS_HUB = "infos_hub"
    INVESTISSEMENT_HUB = "investissement_hub"
    VISUALISATION = "visualisation"

    # Gestion — profil / metier / scenario
    EDIT_PROFIL = "edit_profil"
    EDIT_METIER = "edit_metier"
    ADD_SCENARIO = "add_scenario"
    BANQUE_HUB = "banque_hub"
    LOGEMENTS = "logements"
    
    # Gestion — transactions
    TRANSACTIONS = "transactions"
    REVENU = "revenu"
    DEPENSE = "depense"
    TRANSFERT = "transfert"

    # Gestion — banque / comptes bancaires
    COMPTES_BANCAIRES = "comptes_bancaires"
    AJOUTER_COMPTE_BANCAIRE = "ajouter_compte_bancaire"
    CB_VISUALIZER = "cb_visualizer"

    # Gestion — banque / crédits
    CREDITS = "credits"                       # the annuary / hub
    CREDIT_VISUALIZER = "credit_visualizer"
    AJOUTER_CREDIT = "ajouter_credit"
    NO_CREDIT = "no_credit"    

    #Gestion - Logements 
    MON_DOMICILE = 'mon_domicile'
    MES_LOCATAIRES = "mes_locataires"
    NOUVELLE_LOCATION = "nouvelle_location"
    NOUVEAU_LOCATAIRE = "nouveau_locataire"
    # Investissement
    NOUVEAU_PROJET = "nouveau_projet"
    INFOS_PROJET = "infos_projet"

    # Projets immobiliers
    PROJETS_HUB = "projets_hub"
    IMMO_PROJETS = "immo_projets"
    ADD_IMMO_PROJET = "add_immo_projet"

    # Actifs
    ACTIFS = "actifs"
    ACTIFS_IMMO = "actifs_immo"

    # Outils
    CALCUL_IMPOT = "calcul_impot"    
