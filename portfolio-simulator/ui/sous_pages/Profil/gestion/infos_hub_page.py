#flattened 

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox, QWidget, QVBoxLayout,QHBoxLayout,  QLabel, QPushButton, QLineEdit, QStackedWidget, QSizePolicy
)

from services import AppContext, Page
from session import Session

from .add_scenario_page import AddScenarioPage
from .edit_profil_page import EditProfilPage
from .edit_metier_page import EditMetierPage
from .banque import BanquePage
from .transaction import TransactionPage

from utils.finance_format import euro, percent, age

from services.navigator_service import Page
class InfoHubPage(QWidget):
    back_to_infos_sgn = Signal()
    
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.navigator = appContext.navigator
        self.scenario_service = appContext.scenario_service
        self.cb_service = appContext.cb_service
        self.credit_service = appContext.credit_service
        
        self.session = session
        
        layout = QHBoxLayout(self)
        hub_page = self.host_widget()   
        layout.addWidget(hub_page)             
        
    def host_widget(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        
        self.profil_label = QLabel("")
        self.metier_label = QLabel("")
        self.banque_label = QLabel("")
        
        title = QLabel("Selectionner l'espace à visualiser")
        
        profil_btn = QPushButton("Profil")
        metier_btn = QPushButton("Metier")
        cb_btn = QPushButton("Banque")
        transac_btn = QPushButton("Transactions")
        logements_btn = QPushButton("Logements")
        self.msg_lbl = QLabel()
                
        layout.addWidget(self.profil_label)
        layout.addWidget(self.metier_label)
        layout.addWidget(self.banque_label)
        layout.addStretch()
        
        layout.addWidget(title)
        layout.addWidget(profil_btn)
        layout.addWidget(metier_btn)
        layout.addWidget(cb_btn)
        layout.addWidget(transac_btn)
        layout.addWidget(logements_btn)
        layout.addWidget(self.msg_lbl)
        
        
        profil_btn.clicked.connect(lambda : self.navigator.go_to(Page.EDIT_PROFIL))
        metier_btn.clicked.connect(lambda : self.navigator.go_to(Page.EDIT_METIER)) 
        cb_btn.clicked.connect(lambda : self.navigator.go_to(Page.BANQUE_HUB))
        transac_btn.clicked.connect(lambda: self.navigator.go_to(Page.TRANSACTIONS))
        logements_btn.clicked.connect(lambda: self.navigator.go_to(Page.LOGEMENTS))

        return page
    
    def load(self):
        scenario = self.scenario_service.get_scenario_by_id(self.scenario_service.scenario_actif_id)
        if scenario:
            cbs = self.cb_service.all_userCB_from_scenario(scenario.id)
            credits = self.credit_service.get_all_credits_from_scenario(scenario.id) 
            
            self.banque_label.setText(f"Nb compte bancaire : {len(cbs) if cbs else 0}, pour un total de : {euro(self.cb_service.montant_total_cb_from_scenario(scenario, scenario.date_in)) if cbs else euro(0)}.\nNombre de crédits : {len(credits) if credits else 0}, pour un total de {euro(self.credit_service.montant_total_credits_from_scenario(scenario.id)) if credits else euro(0)}.")
        else:
            self.navigator.go_to(Page.NO_SCENARIO)
        self.navigator.hold_page(Page.INFOS_HUB)
    
        
        
        
        
        