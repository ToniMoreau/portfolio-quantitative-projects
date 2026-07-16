from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QTableWidget, QTableWidgetItem,
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QLineEdit, QStackedWidget, QSizePolicy
)

from services import AppContext
from session import Session

class InfosProjetPage(QWidget):
    back_to_hub = Signal()
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.profil_service = appContext.profile_Service
        self.session = session
        
        layout = QVBoxLayout(self)
        
        self.title = QLabel("Incomings/Actifs/Old")
        
        
        self.retour_btn = QPushButton("Retour")
        layout.addWidget(self.retour_btn)

        
        self.retour_btn.clicked.connect(self.back_to_hub.emit)    
                

