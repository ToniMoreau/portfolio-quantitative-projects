from PySide6.QtCore import Signal
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QListWidget, QListWidgetItem, QWidget, QHBoxLayout,QVBoxLayout, QLabel, QPushButton, QLineEdit, QStackedWidget, QSizePolicy
)

from services import AppContext
from session import Session

class ActifsImmoPage(QWidget):
    back_to_hub = Signal()
    
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.profil_service = appContext.profile_Service
        self.session = session
        layout = QVBoxLayout(self)
        
        #Element de la page
        self.title = QLabel("Actifs Immobiliers")
        
        self.date_wgt = QWidget()
        self.date_lyt = QHBoxLayout(self.date_wgt)
        self.date_immo_lbl = QLabel("Date")
        self.month_immo_input = QLineEdit()
        self.month_immo_input.setPlaceholderText("MM")
        self.month_immo_input.setValidator(QIntValidator(1,12))
        self.year_immo_input  = QLineEdit()
        self.year_immo_input.setPlaceholderText("AAAA")
        self.year_immo_input.setValidator(QIntValidator(2020, 2500))
        
        self.date_lyt.addWidget(self.date_immo_lbl)
        self.date_lyt.addWidget(self.month_immo_input)
        self.date_lyt.addWidget(self.year_immo_input)
        
        self.lists_wgt = QWidget()
        self.lists_lyt = QHBoxLayout(self.lists_wgt)
        self.current_immo_list = QListWidget()
        self.past_immo_list = QListWidget()
        self.lists_lyt.addWidget(self.current_immo_list)
        self.lists_lyt.addWidget(self.past_immo_list)
        
        #Ajouter physiquement à la page
        layout.addWidget(self.title)
        layout.addWidget(self.date_wgt)
        layout.addWidget(self.lists_wgt)
        layout.addStretch()

        self.retour_btn = QPushButton("Retour <-")
        layout.addWidget(self.retour_btn)
        self.retour_btn.clicked.connect(self.back_to_hub.emit)
    
    def load(self):
        self.month_immo_input.clear()
        self.year_immo_input.clear()
        
        self.past_immo_list.clear()
        self.current_immo_list.clear()
        