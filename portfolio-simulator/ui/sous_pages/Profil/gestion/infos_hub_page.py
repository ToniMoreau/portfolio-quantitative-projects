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
        
        scenarios_widget = QWidget()
        scenarios_widget.setObjectName("Scenario Widget")
        scenario_layout = QHBoxLayout(scenarios_widget)
        
        self.scenario_choix = QComboBox()
        self.scenario_choix.currentIndexChanged.connect(self.update_scenario)
        self.add_scenario_btn = QPushButton("Ajouter un Scenario")
        self.edit_scenario_btn = QPushButton("Modifier Scénario")
        
        scenario_layout.addWidget(self.scenario_choix)
        scenario_layout.addWidget(self.add_scenario_btn)
        scenario_layout.addWidget(self.edit_scenario_btn)
        
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
        
        layout.addWidget(scenarios_widget)
        
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
        self.add_scenario_btn.clicked.connect(self.add_scenario_clicked)
        self.edit_scenario_btn.clicked.connect(lambda: self.navigator.go_to(Page.ADD_SCENARIO))
        transac_btn.clicked.connect(lambda: self.navigator.go_to(Page.TRANSACTIONS))
        logements_btn.clicked.connect(lambda: self.navigator.go_to(Page.LOGEMENTS))

        return page
    
    def add_scenario_clicked(self):
        self.scenario_service.set_scenario_actif(None)
        self.navigator.go_to(Page.ADD_SCENARIO)

    def update_scenario(self):
        scenario = self.scenario_service.get_scenario_by_id(self.scenario_choix.currentData())
        self.scenario_service.scenario_actif = scenario
        
        
        if scenario:
            cbs = self.cb_service.all_userCB_from_scenario(scenario.id) 
            credits = self.credit_service.get_all_credits_from_scenario(scenario.id) 
            self.edit_scenario_btn.show()
        else : 
            cbs = credits = None
            self.edit_scenario_btn.hide()
        
        self.banque_label.setText(f"Nb compte bancaire : {len(cbs) if cbs else 0}, pour un total de : {euro(self.cb_service.montant_total_cb_from_scenario(scenario, self.scenario_service.scenario_actif.date_in)) if cbs else euro(0)}.\nNombre de crédits : {len(credits) if credits else 0}, pour un total de {euro(self.credit_service.montant_total_credits_from_scenario(scenario.id)) if credits else euro(0)}.")

    def load(self):
        user = self.session.current_user
        data = self.scenario_choix.currentData()
        
        self.scenario_choix.clear()
        self.scenario_choix.addItem("")
        for scenario in self.scenario_service.get_all_scenario_from_user(self.session.current_user.id):
            self.scenario_choix.addItem(scenario.intitule, scenario.id)
        
        index = self.scenario_choix.findData(data)
        if index is not None:
            self.scenario_choix.setCurrentIndex(index)
            
        self.update_scenario()
        
        
        
        
        