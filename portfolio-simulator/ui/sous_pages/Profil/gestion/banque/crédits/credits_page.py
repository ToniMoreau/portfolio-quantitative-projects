#flattened

from PySide6.QtWidgets import QListWidget, QListWidgetItem, QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel
from PySide6.QtCore import Signal

from services import AppContext, Page
from session import Session

from .ajouter_credit import AjouterCreditPage
from .credit_visualizer_page import CréditVisualizerPage

class CreditsPage(QWidget):
    back_to_hub = Signal()
    open_invests = Signal()
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.credit_service = appContext.credit_service
        self.session = session
        self.banque_service = appContext.banque_service
        self.scenario_service = appContext.scenario_service
        self.navigator = appContext.navigator
        
        self.mlayout = QVBoxLayout(self)
        
        self.credit_hub = self.credit_hub_page()
                
        self.mlayout.addWidget(self.credit_hub)
        
    def credit_hub_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        title = QLabel("Crédits")
        self.scenario_label = QLabel("")
        
        layout.addWidget(title)
        layout.addWidget(self.scenario_label)
        
        self.liste_credits = QListWidget()
        layout.addWidget(self.liste_credits)
        self.liste_credits.clicked.connect(self.btn_credit_clicked)
        
        self.btn_finaliser   = QPushButton("Finaliser Projets")
       
        layout.addStretch()
        
        self.visualiser = QPushButton("Visualiser compte")
        self.btn_supprimer = QPushButton("Supprimer ce crédit")
        self.btn_modifier  = QPushButton("Modifier ce crédit")
        
        layout.addWidget(self.btn_finaliser)
        layout.addStretch()
        layout.addWidget(self.visualiser)
        layout.addWidget(self.btn_supprimer)
        layout.addWidget(self.btn_modifier)
        self.visualiser.hide()
        self.btn_supprimer.hide()
        self.btn_modifier.hide()
        
        self.visualiser.clicked.connect(lambda : self.navigator.go_to(Page.CREDIT_VISUALIZER))
        self.btn_finaliser.clicked.connect(lambda : self.navigator.go_to(Page.INVESTISSEMENT_HUB))
        self.btn_modifier.clicked.connect(lambda : self.navigator.go_to(Page.AJOUTER_CREDIT))
        self.btn_supprimer.clicked.connect(self.supprimer_clicked)
        
        btn_retour = QPushButton("Retour")
        layout.addWidget(btn_retour)
        btn_retour.clicked.connect(lambda : self.navigator.go_to(Page.BANQUE_HUB))

        return page
                
    def btn_credit_clicked(self, credit_item : QListWidgetItem):
        self.visualiser.show()
        self.btn_supprimer.show()
        self.btn_modifier.show()
        credit_id = credit_item.data(1)
        credit = self.credit_service.get_credit_by_id(credit_id)
        self.credit_service.set_credit_actif(credit)
        
    def ajouter_clicked(self):
        self.credit_service.set_credit_actif()
        self.navigator.go_to(Page.AJOUTER_CREDIT)    
            
    def supprimer_clicked(self):
        self.credit_service.delete_credit(self.credit_service.credit_actif)
        self.load()
        
    def load(self):
        self.credit_service.set_credit_actif()
        self.scenario_label.setText(f"Scénario : {self.scenario_service.scenario_actif.intitule}")

        self.liste_credits.clear()
        
        if self.session.current_user:
            for credit in (self.credit_service.get_all_credits_from_scenario(self.scenario_service.scenario_actif.id) or []):
                banque = self.banque_service.get_banque_by_id(credit.id_banque)
                widget_item= QListWidgetItem(f"Crédit n°{credit.id}, chez {banque.nom}, de {credit.montant}.00 €")
                widget_item.setData(1, credit.id)
                self.liste_credits.addItem(widget_item)
