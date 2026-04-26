from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QStackedWidget, QSizePolicy
)

from .actifs_immo_page import ActifsImmoPage
from services import AppContext
from session import Session

class ActifsPage(QWidget):
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.profil_service = appContext.profile_Service
        self.session = session
        
        layout = QVBoxLayout(self)
        
        self.hub_page = self.hub()
        self.immo_page = ActifsImmoPage(appContext, session)
        
        self.stack = QStackedWidget()
        self.stack.addWidget(self.hub_page) #index 0
        self.stack.addWidget(self.immo_page)#index 1
        
        layout.addWidget(self.stack) 
        
        self.immo_page.back_to_hub.connect(lambda :self.load_index(0))
        
        self.load_index(0)
        
    def hub(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        self.title = QLabel("Actifs")
        
        self.immo_btn = QPushButton("Actifs Immobiliers")
        
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
        

