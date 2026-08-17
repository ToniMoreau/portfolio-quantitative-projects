#flattened

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel
from PySide6.QtCore import Signal

from services import AppContext, Page
from session import Session

from .comptes_bancaires import ComptesBancairesPage
from .crédits import CreditsPage

class BanquePage(QWidget):
    back_signal = Signal()
    def __init__(self, appContext : AppContext,session : Session):
        super().__init__()
        
        self.appContext = appContext
        self.session = session
        
        layout = QVBoxLayout(self)
        
        self.banque_hub = self.banque_hub_page()
        
        layout.addWidget(self.banque_hub)
        
    def banque_hub_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        title = QLabel("Fiche Banque")
        
        comptes_btn = QPushButton("Comptes Bancaires")
        credits_btn = QPushButton("Crédits")
        retour_btn = QPushButton("Retour <-")
        
        layout.addWidget(comptes_btn)
        layout.addWidget(credits_btn)
        layout.addStretch()
        
        layout.addWidget(retour_btn)
        
        comptes_btn.clicked.connect(self.comptes_clicked)
        credits_btn.clicked.connect(self.credits_clicked)
        
        retour_btn.clicked.connect(lambda : self.appContext.navigator.go_to(Page.INFOS_HUB))
        
        return page
    
    def comptes_clicked(self):
        self.appContext.cb_service.set_cb_actif(None)
        self.appContext.navigator.go_to(Page.COMPTES_BANCAIRES)   
    
    def credits_clicked(self):
        self.appContext.credit_service.set_credit_actif(None)
        self.appContext.invest_service.set_invest_actif(None)
        self.appContext.navigator.go_to(Page.CREDITS)