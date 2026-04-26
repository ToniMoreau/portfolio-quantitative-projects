
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox, QWidget, QVBoxLayout, QHBoxLayout,  QLabel, QPushButton, QLineEdit, QStackedWidget, QSizePolicy
)
from services import AppContext
from services.domain_services.metierService import MetierService
from session import Session
from .revenu_page import AjouterRevenuPage
from .depense_page import AjouterDepensePage
from .transfert_page import TransfertPage

class TransactionPage(QWidget):
    back_to_hub = Signal()
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.metier_service = appContext.metier_service
        self.cb_service = appContext.cb_service
        self.banque_service = appContext.banque_service
        self.scenario_service = appContext.scenario_service
        self.session = session
        
        layout = QVBoxLayout(self)
        self.hub_page = self.transac_hub_page()
        self.depense_page = AjouterDepensePage(appContext, self.session)
        self.revenu_page = AjouterRevenuPage(appContext, self.session)
        self.transfert_page = TransfertPage(appContext, session)

        self.stack = QStackedWidget()
        self.stack.addWidget(self.hub_page) #index 0
        self.stack.addWidget(self.depense_page)#index 1
        self.stack.addWidget(self.revenu_page)#index 2
        self.stack.addWidget(self.transfert_page)#index 3
        
        layout.addWidget(self.stack)
        
        self.depense_page.back_to_hub.connect(lambda : self.load_index(0))
        self.revenu_page.back_to_hub.connect(lambda : self.load_index(0))
        self.transfert_page.back_to_hub.connect(lambda : self.load_index(0))

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
        layout.addWidget(add_transfert_btn
                         )
        add_depense_btn.clicked.connect(lambda : self.load_index(1))
        add_revenu_btn.clicked.connect(lambda : self.load_index(2))
        add_transfert_btn.clicked.connect(lambda : self. load_index(3))

        self.retour_btn = QPushButton("Retour <-")
        layout.addWidget(self.retour_btn)
        self.retour_btn.clicked.connect(self.back_to_hub.emit)
        return page
        
    def load_index(self, index):
        self.stack.setCurrentIndex(index)
        
        page = self.stack.currentWidget()
        if hasattr(page, "load"):
            print("j'ai load")
            page.load()
        if index == 0:
            self.load()
        
    def load(self):
        pass