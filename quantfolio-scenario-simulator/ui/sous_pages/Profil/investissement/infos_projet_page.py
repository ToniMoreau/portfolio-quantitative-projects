from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QTableWidget, QTableWidgetItem,
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QLineEdit, QStackedWidget, QSizePolicy
)

from services import AppContext, Page
from session import Session

class InfosProjetPage(QWidget):
    back_to_hub = Signal()
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.session = session
        
        layout = QVBoxLayout(self)
        
        self.title = QLabel("Incomings/Actifs/Old")
        
        
        self.retour_btn = QPushButton("Retour")
        layout.addWidget(self.retour_btn)

        
        self.retour_btn.clicked.connect(lambda : appContext.navigator.go_to(Page.INVESTISSEMENT_HUB))    
                

