from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel
from PySide6.QtCore import Signal

from services import AppContext
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
        self.stack = QStackedWidget()
        
        self.banque_hub = self.banque_hub_page()
        self.cb_page = ComptesBancairesPage(self.appContext, self.session)
        self.credits_page = CreditsPage(self.appContext, self.session)
        
        self.stack.addWidget(self.banque_hub)#index 0
        self.stack.addWidget(self.cb_page) #index 1
        self.stack.addWidget(self.credits_page) #index 2
        
        layout.addWidget(self.stack)
        self.stack.setCurrentIndex(0)
        
        self.cb_page.back_to_hub.connect(lambda : self.stack.setCurrentIndex(0))
        self.credits_page.back_to_hub.connect(lambda : self.stack.setCurrentIndex(0))
        
        
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
        
        comptes_btn.clicked.connect(lambda : self.load_index(1))
        credits_btn.clicked.connect(lambda : self.load_index(2))
        
        retour_btn.clicked.connect(self.back_signal.emit)
        
        
        return page
    
    def load_index(self, index):
        self.stack.setCurrentIndex(index)
        
        page = self.stack.currentWidget()
        if hasattr(page, "load"):
            page.load()
