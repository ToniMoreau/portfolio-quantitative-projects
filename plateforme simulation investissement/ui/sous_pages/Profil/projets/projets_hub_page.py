from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QStackedWidget, QSizePolicy
)

from .immo_projets_page import ProjetsImmoPage
from services import AppContext
from session import Session

class ProjetsPage(QWidget):
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.profil_service = appContext.profile_Service
        self.session = session
        
        layout = QVBoxLayout(self)
        
        self.hub_page = self.hub()
        self.projets_immo_page = ProjetsImmoPage(appContext, session)
        
        self.stack = QStackedWidget()
        self.stack.addWidget(self.hub_page) #index 0
        self.stack.addWidget(self.projets_immo_page)#index 1
        
        layout.addWidget(self.stack) 
        
        self.projets_immo_page.back_to_hub.connect(lambda :self.load_index(0))
        
        self.load_index(0)
        
    def hub(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        self.title = QLabel("Projets")
        
        self.immo_btn = QPushButton("Projets Immobiliers")
        
        layout.addWidget(self.title)
        layout.addWidget(self.immo_btn)
        layout.addStretch()
        
        self.immo_btn.clicked.connect(lambda : self.load_index(1))

        return page
    
    def load_index(self, index):
        self.stack.setCurrentIndex(index)
        page = self.stack.currentWidget()
        if hasattr(page, "load"):
            page.load()
        

