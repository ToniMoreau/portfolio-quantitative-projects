from PySide6.QtCore import Signal
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QListWidget, QListWidgetItem, QWidget, QHBoxLayout,QVBoxLayout, QLabel, QPushButton, QLineEdit, QStackedWidget, QSizePolicy
)

from services import AppContext
from session import Session

from .add_immo_projet_page import AddImmoProjetPage

class ProjetsImmoPage(QWidget):
    back_to_hub = Signal()
    
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.profil_service = appContext.profile_Service
        self.invest_service = appContext.invest_service
        self.session = session
        layout = QVBoxLayout(self)
        
        self.projet_hub = self.hub_page()
        self.add_projet_page = AddImmoProjetPage(appContext, session)
        
        self.stack = QStackedWidget()
        self.stack.addWidget(self.projet_hub) #index 0
        self.stack.addWidget(self.add_projet_page) #index 1
        
        layout.addWidget(self.stack)
        
        self.load_by_index(0)
        
        self.retour_btn.clicked.connect(self.back_to_hub.emit)
        self.ajouter_btn.clicked.connect(lambda : self.load_by_index(1))
        self.add_projet_page.back_to_hub.connect(lambda : self.load_by_index(0))
        
    def load_by_index(self, index):
        try:
            self.stack.setCurrentIndex(index)
            page = self.stack.currentWidget()
            if hasattr(page, "load"):
                print("yes loaded page")
                page.load()
                print(page)
            if index == 0:
                self.load()
        except Exception as e:
            self.page_msg.setText(str(e))
            raise ValueError(e)
            
    def hub_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        #Element de la page
        self.title = QLabel("Projets Immobiliers")
        
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
        self.projets_immo_list = QListWidget()
        self.lists_lyt.addWidget(self.projets_immo_list)
        
        #Ajouter physiquement à la page
        layout.addWidget(self.title)
        layout.addWidget(self.date_wgt)
        layout.addWidget(self.lists_wgt)
        layout.addStretch()

        self.ajouter_btn = QPushButton("Ajouter Projet")
        self.retour_btn = QPushButton("Retour <-")
        self.page_msg = QLabel("")
        layout.addWidget(self.retour_btn)
        layout.addWidget(self.ajouter_btn)
        layout.addWidget(self.page_msg)
        return page
    
    def load(self):
        self.month_immo_input.clear()
        self.year_immo_input.clear()
        
        self.projets_immo_list.clear()        
        
        self.page_msg.clear()
        
        