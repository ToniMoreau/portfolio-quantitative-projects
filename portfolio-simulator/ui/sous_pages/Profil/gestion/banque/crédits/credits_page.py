from PySide6.QtWidgets import QListWidget, QListWidgetItem, QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel
from PySide6.QtCore import Signal

from services import AppContext
from session import Session
from .credits_immo_page import CreditsImmoPage


class CreditsPage(QWidget):
    back_to_hub = Signal()
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.credit_service = appContext.credit_service
        self.session = session
        self.banque_service = appContext.banque_service
        self.scenario_service = appContext.scenario_service
        
        self.mlayout = QVBoxLayout(self)
        
        self.credit_hub = self.credit_hub_page()
        print("crédits immo")
        self.credit_immo = CreditsImmoPage(appContext, self.session)
        print("creditys immos 2")
        self.credit_conso = CreditsImmoPage(appContext, self.session)
        
        self.stack = QStackedWidget()
        self.stack.addWidget(self.credit_hub) #index 0
        self.stack.addWidget(self.credit_immo) #index 1
        self.stack.addWidget(self.credit_conso) #index 2
        
        self.mlayout.addWidget(self.stack)
        
        self.stack.setCurrentIndex(0)
        self.credit_immo.back_to_hub.connect(lambda :self.stack.setCurrentIndex(0))
        self.credit_conso.back_to_hub.connect(lambda :self.stack.setCurrentIndex(0))

    def credit_hub_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        self.scenario_label = QLabel("")

        self.credit_immo_btn = QPushButton("Crédits Immo")
        self.credit_conso_btn = QPushButton("Crédits Conso")
        
        layout.addWidget(self.scenario_label)        

        layout.addWidget(self.credit_immo_btn)
        layout.addWidget(self.credit_conso_btn)
        
        self.credit_immo_btn.clicked.connect(lambda : self.load_index(1))
        
        btn_retour = QPushButton("Retour")
        layout.addWidget(btn_retour)
        btn_retour.clicked.connect(self.back_to_hub.emit)

        return page
    
    def load_index(self, index):
        self.stack.setCurrentIndex(index)
        page = self.stack.currentWidget()
        if hasattr(page, "load"):
            page.load()
        