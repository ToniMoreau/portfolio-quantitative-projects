#flattened

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel
from PySide6.QtCore import Signal

from services import AppContext, Page
from session import Session

class LogementsHubPage(QWidget):
    def __init__(self, appContext : AppContext,session : Session):
        super().__init__()
        
        self.appContext = appContext
        self.session = session
        
        layout = QVBoxLayout(self)        
        title = QLabel("Logements Hub")
        
        mon_domicile_btn = QPushButton("Mon Domicile")
        mes_locataires_btn = QPushButton("Mes locataires")
        retour_btn = QPushButton("Retour <-")
        
        layout.addWidget(mon_domicile_btn)
        layout.addWidget(mes_locataires_btn)
        layout.addStretch()
        
        layout.addWidget(retour_btn)
        
        mon_domicile_btn.clicked.connect(self.mon_dom_clicked)
        mes_locataires_btn.clicked.connect(self.mes_locs_clicked)

        
        retour_btn.clicked.connect(lambda : self.appContext.navigator.go_to(Page.INFOS_HUB))
    
    def mon_dom_clicked(self):
        self.appContext.cb_service.set_cb_actif(None)
        self.appContext.navigator.go_to(Page.MON_DOMICILE)   
    
    def mes_locs_clicked(self):
        self.appContext.credit_service.set_credit_actif(None)
        self.appContext.invest_service.set_invest_actif(None)
        self.appContext.navigator.go_to(Page.MES_LOCATAIRES)