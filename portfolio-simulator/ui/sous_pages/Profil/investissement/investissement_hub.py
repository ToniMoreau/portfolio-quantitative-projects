from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QTableWidget, QTableWidgetItem,
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QLineEdit, QStackedWidget, QSizePolicy
)

from services import AppContext
from session import Session

from .nouveau_projet_page import NouveauProjetPage
from .infos_projet_page import InfosProjetPage

class InvestissementHubPage(QWidget):
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.profil_service = appContext.profile_Service
        self.session = session
        
        layout = QVBoxLayout(self)
        
        self.hub_page = self.hub()
        self.nouveau_projet_page = NouveauProjetPage(appContext, self.session)
        self.infos_projet_page = InfosProjetPage(appContext, self.session)
        
        self.stack = QStackedWidget()
        self.stack.addWidget(self.hub_page) #index 0
        self.stack.addWidget(self.nouveau_projet_page) #index 1
        self.stack.addWidget(self.infos_projet_page) #index 2
        
        layout.addWidget(self.stack) 
        
        self.load_index(0)
        
        self.nouveau_projet_page.back_to_hub.connect(lambda : self.load_index(0))
        self.infos_projet_page.back_to_hub.connect(lambda : self.load_index(0))
    def hub(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        self.title = QLabel("Incomings/Actifs/Old")
        
        self.filter_wgt = QWidget()
        self.filter_layout = QHBoxLayout(self.filter_wgt)
        
        self.invest_tab = QTableWidget()
        self.invest_tab.setColumnCount(8)
        self.invest_tab.setHorizontalHeaderLabels([
            "Type", "Nom", "Prix achat", "Valeur marché", "Paiement Comptant", "Crédit Restant", "Duréee Crédit Restante", "Etat"
        ])
        
        btns_wgt = QWidget()
        self.btns_lyt = QHBoxLayout(btns_wgt)
        
        left_btns_wgt = QWidget()
        self.left_btns_lyt = QHBoxLayout(left_btns_wgt)
        self.nouveau_projet_btn = QPushButton("Nouveau Projet")
        
        right_btns_wgt = QWidget()
        self.right_btns_lyt = QHBoxLayout(right_btns_wgt)
        self.infos_btn = QPushButton("+ d'infos")
        self.vendre_btn =QPushButton("Vendre")
        self.supprimer_btn = QPushButton("Supprimer")
        self.conclure_btn = QPushButton("Conclure")
        
        self.btns_lyt.addWidget(left_btns_wgt)
        self.left_btns_lyt.addWidget(self.nouveau_projet_btn)

        self.btns_lyt.addStretch()
        
        self.btns_lyt.addWidget(right_btns_wgt)
        self.right_btns_lyt.addWidget(self.infos_btn)
        self.right_btns_lyt.addWidget(self.vendre_btn)
        self.right_btns_lyt.addWidget(self.supprimer_btn)
        self.right_btns_lyt.addWidget(self.conclure_btn)
        
        layout.addWidget(self.title)
        layout.addWidget(self.filter_wgt)
        layout.addWidget(self.invest_tab)
        layout.addWidget(btns_wgt)
    
        layout.addStretch()

        self.nouveau_projet_btn.clicked.connect(lambda : self.load_index(1))
        self.infos_btn.clicked.connect(lambda : self.load_index(2))
        
        return page
    
    def load_index(self, index):
        self.stack.setCurrentIndex(index)
        page = self.stack.currentWidget()
        if hasattr(page, "load"):
            page.load()
        

