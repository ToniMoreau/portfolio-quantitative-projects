#flattered
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox, QWidget, QVBoxLayout, QHBoxLayout,  QLabel, QPushButton, QLineEdit, QStackedWidget, QSizePolicy
)
from services import AppContext, Page
from services.domain_services.metierService import MetierService
from session import Session
from .revenu_page import AjouterRevenuPage
from .depense_page import AjouterDepensePage
from .transfert_page import TransfertPage

class TransactionPage(QWidget):
    back_to_hub = Signal()
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.scenario_service = appContext.scenario_service
        self.session = session
        
        self.navigator = appContext.navigator
        
        layout = QVBoxLayout(self)
        self.hub_page = self.transac_hub_page()        
        layout.addWidget(self.hub_page)
        
    def transac_hub_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        title = QLabel("Choisissez un type de transaction : ")
        
        add_depense_btn = QPushButton("Ajouter une dépense")
        add_revenu_btn = QPushButton("Ajouter un revenu")
        add_transfert_btn = QPushButton("Ajouter un transfert")
        
        layout.addWidget(title)
        layout.addWidget(add_depense_btn)
        layout.addWidget(add_revenu_btn)
        layout.addWidget(add_transfert_btn)
        
        add_depense_btn.clicked.connect(lambda : self.navigator.go_to(Page.DEPENSE))
        add_revenu_btn.clicked.connect(lambda : self.navigator.go_to(Page.REVENU))
        add_transfert_btn.clicked.connect(lambda : self.navigator.go_to(Page.TRANSFERT))

        self.retour_btn = QPushButton("Retour <-")
        layout.addWidget(self.retour_btn)
        self.retour_btn.clicked.connect(lambda : self.navigator.go_to(Page.INFOS_HUB))
        return page
                
    def load(self):
        pass