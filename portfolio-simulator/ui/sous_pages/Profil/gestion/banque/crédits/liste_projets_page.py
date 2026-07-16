from PySide6.QtWidgets import QListWidget, QListWidgetItem, QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel
from PySide6.QtCore import Signal

from services import AppContext
from session import Session


class ListeProjetsPage(QWidget):
    back_to_hub = Signal()
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.credit_service = appContext.credit_service
        self.session = session
        self.banque_service = appContext.banque_service
        self.invest_service = appContext.invest_service
        self.scenario_service = appContext.scenario_service
        
        layout = QHBoxLayout(self)
        
        self.finaliser_hub_page = self.liste_projets_hub()
        self.stack = QStackedWidget()
        self.stack.addWidget(self.finaliser_hub_page) #index 0
        
        layout.addWidget(self.stack)
        self.stack.setCurrentIndex(0)
        
        #self.ttt.back_to_hub.connect(lambda : self.stack.setCurrentIndex(0))
    
    def liste_projets_hub(self):
        page = QWidget()
        layout = QVBoxLayout(page)
                
        self.scenario_label = QLabel("")

        self.liste_wgt = QWidget()
        self.liste_layout = QHBoxLayout(self.liste_wgt)
        self.liste_projets = QListWidget()
        self.liste_projets.itemClicked.connect(self.item_clicked)
        
        self.liste_layout.addWidget(self.liste_projets)
        
        layout.addWidget(self.liste_wgt)

        self.finaliser_btn = QPushButton("Finaliser Projet")
        self.finaliser_btn.hide()

        self.btn_retour = QPushButton("Retour")
        
        layout.addWidget(self.finaliser_btn)
        layout.addWidget(self.btn_retour)
        
        self.btn_retour.clicked.connect(self.back_to_hub.emit)
        self.finaliser_btn.clicked.connect(self.finaliser_btn_clicked)
        return page
    
    def item_clicked(self, item : QListWidgetItem):
        invest = None
        if item:
            invest_id = item.data(1)
            if invest_id is not None:
                invest = self.invest_service.get_by_id(invest_id)
                self.invest_service.set_invest_actif(invest)
        if invest is not None:
            self.finaliser_btn.show()
            
    def finaliser_btn_clicked(self):
        self.load_index(1)
    
    def load_index(self, index):
        self.stack.setCurrentIndex(index)
        page = self.stack.currentWidget()
        if hasattr(page, "load"):
            page.load()
      