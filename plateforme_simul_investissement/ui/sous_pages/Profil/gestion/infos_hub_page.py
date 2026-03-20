from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox, QWidget, QVBoxLayout,QHBoxLayout,  QLabel, QPushButton, QLineEdit, QStackedWidget, QSizePolicy
)

from services import AppContext
from session import Session

from .add_scenario_page import AddScenarioPage
from .edit_profil_page import EditProfilPage
from .edit_metier_page import EditMetierPage
from .banque import BanquePage
from .transaction import TransactionPage

from utils.finance_format import euro, percent, age
class InfoHubPage(QWidget):
    back_to_infos_sgn = Signal()
    
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.profil_service = appContext.profile_Service
        self.metier_service = appContext.metier_service
        self.scenario_service = appContext.scenario_service
        self.cb_service = appContext.cb_service
        self.credit_service = appContext.credit_service
        
        self.session = session
        
        layout = QHBoxLayout(self)
        
        hub_page = self.host_widget()
        profil_page = EditProfilPage(self.profil_service, self.session)
        metier_page = EditMetierPage(appContext, self.session)
        self.banque_page = BanquePage(appContext, self.session)
        self.add_scenario_page = AddScenarioPage(appContext, self.session)
        self.transaction_page = TransactionPage(appContext, self.session)
        
        self.stack = QStackedWidget()
        self.stack.addWidget(hub_page) #index 0
        self.stack.addWidget(profil_page) #index 1
        self.stack.addWidget(metier_page) #index 2
        self.stack.addWidget(self.banque_page) #index 3
        self.stack.addWidget(self.add_scenario_page) #index 4
        self.stack.addWidget(self.transaction_page)
        
        layout.addWidget(self.stack)
        
        self.stack.setCurrentIndex(0)
        
        metier_page.back_to_hub.connect(lambda : self.load_index(0))
        profil_page.back_to_hub.connect(lambda : self.load_index(0))
        self.banque_page.back_signal.connect(lambda : self.load_index(0))
        self.add_scenario_page.back_to_hub.connect(lambda: self.load_index(0))
        self.transaction_page.back_to_hub.connect(lambda : self.load_index(0))
        
    def load_index(self, index):
        if self.scenario_service.scenario_actif is None:
            self.msg_lbl.setText("Veuillez selectionner un scenario avant.")
        else:
            self.stack.setCurrentIndex(index)
            
            page = self.stack.currentWidget()
            if hasattr(page, "load"):
                page.load()
            if index == 0:
                self.load()
        
        
    def host_widget(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        scenarios_widget = QWidget()
        scenarios_widget.setObjectName("Scenario Widget")
        scenario_layout = QHBoxLayout(scenarios_widget)
        
        self.scenario_choix = QComboBox()
        self.scenario_choix.currentIndexChanged.connect(self.update_scenario)
        self.add_scenario_btn = QPushButton("Ajouter un Scenario")
        
        
        scenario_layout.addWidget(self.scenario_choix)
        scenario_layout.addWidget(self.add_scenario_btn)
        
        self.profil_label = QLabel("")
        self.metier_label = QLabel("")
        self.banque_label = QLabel("")
        
        title = QLabel("Selectionner l'espace à visualiser")
        
        profil_btn = QPushButton("Profil")
        metier_btn = QPushButton("Metier")
        cb_btn = QPushButton("Banque")
        transac_btn = QPushButton("Transactions")
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
        layout.addWidget(self.msg_lbl)
        
        
        profil_btn.clicked.connect(lambda : self.load_index(1))
        metier_btn.clicked.connect(lambda : self.load_index(2)) 
        cb_btn.clicked.connect(lambda : self.load_index(3))
        self.add_scenario_btn.clicked.connect(lambda : self.load_index(4))
        transac_btn.clicked.connect(lambda: self.load_index(5))

        return page
    
    def update_scenario(self):
        scenario = self.scenario_service.get_scenario_by_id(self.scenario_choix.currentData())
        self.scenario_service.scenario_actif = scenario
        
        if scenario:
            cbs = self.cb_service.all_userCB_from_scenario(scenario.id) 
            credits = self.credit_service.get_all_credits_from_scenario(scenario.id) 
        else : cbs = credits = None
        
        self.banque_label.setText(f"Nb compte bancaire : {len(cbs) if cbs else 0}, pour un total de : {euro(self.cb_service.montant_total_cb_from_scenario(scenario.id)) if cbs else euro(0)}.\nNombre de crédits : {len(credits) if credits else 0}, pour un total de {euro(self.credit_service.montant_total_cb_from_scenario(scenario.id)) if credits else euro(0)}.")

    def load(self):
        user = self.session.current_user
        data = self.scenario_choix.currentData()
        
        self.scenario_choix.clear()
        for scenario in self.scenario_service.get_all_scenario_from_user(self.session.current_user.id):
            self.scenario_choix.addItem(scenario.intitule, scenario.id)
        
        index = self.scenario_choix.findData(data)
        if index is not None:
            self.scenario_choix.setCurrentIndex(index)
        
        scenario = self.scenario_service.get_scenario_by_id(self.scenario_choix.currentData())
        self.scenario_service.scenario_actif = scenario
        if scenario:
            cbs = self.cb_service.all_userCB_from_scenario(scenario.id) 
            credits = self.credit_service.get_all_credits_from_scenario(scenario.id) 
        else : cbs = credits = None
        
        self.profil_label.setText(f"{user.username} : {user.firstname} {user.lastname}, {age(user.age) if user.age else ""}.")
        self.banque_label.setText(f"Nb compte bancaire : {len(cbs) if cbs else 0}, pour un total de : {euro(self.cb_service.montant_total_cb_from_scenario(scenario.id)) if cbs else euro(0)}.\nNombre de crédits : {len(credits) if credits else 0}, pour un total de {euro(self.credit_service.montant_total_cb_from_scenario(scenario.id)) if credits else euro(0)}.")
        
        
        
        
        
        