#flattened 
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QStackedWidget, QSizePolicy
)

from session import Session

from .dashboard import DashboardPage
from .visualisation_page import VisualisationPage
from .gestion import InfoHubPage
from .investissement import InvestissementHubPage

#from .actifs import ActifsPage
#from .projets import ProjetsPage

from .gestion import EditMetierPage, EditProfilPage, AddScenarioPage
from .gestion.transaction import TransactionPage, TransfertPage, AjouterDepensePage, AjouterRevenuPage
from .gestion.banque import BanquePage
from .gestion.banque.comptes_bancaires import ComptesBancairesPage, CbVisualizerPage, AjouterCompteBancairePage
from .gestion.banque.crédits import CreditsPage, AjouterCreditPage, CréditVisualizerPage, NoCreditPage
from .gestion.logements import LogementsHubPage, MesLocatairesPage, MonDomicilePage, NouvelleLocationPage, NouveauLocatairePage

from .investissement import InfosProjetPage, NouveauProjetPage

from .outils.outils_page import OutilsPage, CalculImpotsPage

from services import AppContext, Page
from services.navigator_service import Page

class ProfilPage(QWidget):
    logout_success = Signal()
    
    
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.appContext = appContext
        self.session = session
        self.navigator = appContext.navigator
        
        # --- Layout principal ---
        layout = QVBoxLayout(self)
        
        sidebar_widget = QWidget()
        sidebar_widget.setObjectName("Sidebar")
        sidebar_layout = QHBoxLayout(sidebar_widget)
        
        self.dashboard_btn = QPushButton("Dashboard")
        self.outils_btn = QPushButton("Outils")
        self.infos_btn = QPushButton("Gestion")
        self.invest_btn = QPushButton("Investissements")
        self.visualisation_btn = QPushButton("Visualisation")

        sidebar_layout.addWidget(self.dashboard_btn)
        sidebar_layout.addWidget(self.outils_btn)
        sidebar_layout.addWidget(self.infos_btn)
        sidebar_layout.addWidget(self.invest_btn)
        sidebar_layout.addWidget(self.visualisation_btn)

        self.dashboard_page = DashboardPage(self.appContext, self.session)
        self.outils_page = OutilsPage(self.appContext, self.session)
        self.infos_page = InfoHubPage(self.appContext, self.session)
        self.invest_page = InvestissementHubPage(self.appContext, self.session)
        self.visualisation_page = VisualisationPage()

        self.add_scenario_page = AddScenarioPage(appContext, session)
        self.edit_metier_page = EditMetierPage(appContext, session)
        self.edit_profil_page = EditProfilPage(appContext,session)
        self.banque_hub_page = BanquePage(appContext,session)
        self.transactions_page = TransactionPage(appContext,session)
        self.logements_page = LogementsHubPage(appContext, session)
        
        self.comptes_bancaires_page = ComptesBancairesPage(appContext,session)
        self.ajouter_cb_page = AjouterCompteBancairePage(appContext,session)
        self.cb_visualizer_page = CbVisualizerPage(appContext,session)
       
        self.credits_page = CreditsPage(appContext,session)
        self.credit_visualizer_page = CréditVisualizerPage(appContext,session)
        self.ajouter_credit_page = AjouterCreditPage(appContext,session)
        self.no_credit_page = NoCreditPage(appContext, session)
        
        self.depenses_page = AjouterDepensePage(appContext,session)
        self.revenus_page = AjouterRevenuPage(appContext,session)
        self.transferts_page = TransfertPage(appContext,session)
        
        self.mon_domicile_page = MonDomicilePage(appContext, session)
        self.mes_locataires_page = MesLocatairesPage(appContext,session)
        self.nouvelle_location_page = NouvelleLocationPage(appContext, session)
        self.nouveau_locataire_page = NouveauLocatairePage(appContext, session)
        
        self.nouveau_projet_page = NouveauProjetPage(appContext,session)
        self.infos_projet_page = InfosProjetPage(appContext,session)
        
        self.calcul_impot_page = CalculImpotsPage(appContext,session)
        
        
        #Gestion de la pile de pages
        self.stack = QStackedWidget()
        self.stack.addWidget(self.dashboard_page) #index 0
        self.stack.addWidget(self.outils_page) #index 1
        self.stack.addWidget(self.infos_page) #index 2
        self.stack.addWidget(self.invest_page) #index 3
        self.stack.addWidget(self.visualisation_page) #index 4
        
        #stacking flat
        self.stack.addWidget(self.add_scenario_page)
        self.stack.addWidget(self.edit_metier_page)
        self.stack.addWidget(self.edit_profil_page)
        self.stack.addWidget(self.banque_hub_page)
        self.stack.addWidget(self.transactions_page)
        self.stack.addWidget(self.logements_page)
        self.stack.addWidget(self.comptes_bancaires_page)
        self.stack.addWidget(self.ajouter_cb_page)
        self.stack.addWidget(self.cb_visualizer_page)
        self.stack.addWidget(self.credits_page)
        self.stack.addWidget(self.no_credit_page)
        self.stack.addWidget(self.credit_visualizer_page)
        self.stack.addWidget(self.ajouter_credit_page)
        self.stack.addWidget(self.depenses_page)
        self.stack.addWidget(self.revenus_page)
        self.stack.addWidget(self.transferts_page)
        self.stack.addWidget(self.mon_domicile_page)
        self.stack.addWidget(self.mes_locataires_page)
        self.stack.addWidget(self.nouvelle_location_page)
        self.stack.addWidget(self.nouveau_locataire_page)
        self.stack.addWidget(self.nouveau_projet_page)
        self.stack.addWidget(self.infos_projet_page)
        self.stack.addWidget(self.calcul_impot_page )
        
        
        self.my_pages = {
            #GROUND 1 | SIDEBAR -- DIRECT CHILDREN
            Page.DASHBOARD : self.dashboard_page,
            Page.OUTILS : self.outils_page,
            Page.INFOS_HUB : self.infos_page,
            Page.INVESTISSEMENT_HUB : self.invest_page,
            Page.VISUALISATION : self.visualisation_page,
            
            #INFO / GESTION CHILDREN
            Page.ADD_SCENARIO : self.add_scenario_page,
            Page.EDIT_METIER : self.edit_metier_page,
            Page.EDIT_PROFIL : self.edit_profil_page,
            Page.BANQUE_HUB : self.banque_hub_page,
            Page.TRANSACTIONS : self.transactions_page,
            Page.LOGEMENTS : self.logements_page,
            
            #GESTION/BANQUE/COMPTES BANCAIRES
            Page.COMPTES_BANCAIRES : self.comptes_bancaires_page,
            Page.AJOUTER_COMPTE_BANCAIRE :self.ajouter_cb_page,
            Page.CB_VISUALIZER :self.cb_visualizer_page,
            
            #GESTION/BANQUE/CREDITS
            Page.CREDITS : self.credits_page,
            Page.CREDIT_VISUALIZER : self.credit_visualizer_page,
            Page.AJOUTER_CREDIT : self.ajouter_credit_page,
            Page.NO_CREDIT : self.no_credit_page,
            
            #GESTION/TRANSACTIONS
            Page.DEPENSE :self.depenses_page,
            Page.REVENU : self.revenus_page,
            Page.TRANSFERT : self.transferts_page,
            
            #GESTION / LOGEMENTS
            Page.MON_DOMICILE : self.mon_domicile_page,
            Page.MES_LOCATAIRES : self.mes_locataires_page,
            Page.NOUVELLE_LOCATION : self.nouvelle_location_page,
            Page.NOUVEAU_LOCATAIRE : self.nouveau_locataire_page,
            #INVESTISSEMENTS
            Page.NOUVEAU_PROJET : self.nouveau_projet_page,
            Page.INFOS_PROJET : self.infos_projet_page,

            #OUTIL
            Page.CALCUL_IMPOT : self.calcul_impot_page
        }

        layout.addWidget(sidebar_widget, 1)
        layout.addWidget(self.stack, 7)
        
        #Actions boutons
        self.dashboard_btn.clicked.connect(lambda : self.navigator.go_to(Page.DASHBOARD))
        self.outils_btn.clicked.connect(lambda : self.navigator.go_to(Page.OUTILS))
        self.infos_btn.clicked.connect(lambda : self.navigator.go_to(Page.INFOS_HUB))
        self.invest_btn.clicked.connect(lambda : self.navigator.go_to(Page.INVESTISSEMENT_HUB))
        self.visualisation_btn.clicked.connect(lambda : self.navigator.go_to(Page.VISUALISATION))
        
        self.appContext.navigator.navigation_requested.connect(self.handle_navigation)
        
    def handle_navigation(self, page_key, context):
        if page_key not in self.my_pages:
            return
        page = self.my_pages[page_key]
        self.stack.setCurrentWidget(page)
        if context and hasattr(page, "set_context"):
            page.set_context(context)
        if hasattr(page, "load"):
            page.load()    
                    
            

        

