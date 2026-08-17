#flattened

from PySide6.QtWidgets import QMessageBox,QListWidget, QListWidgetItem, QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel
from PySide6.QtCore import Signal

from services import AppContext, Page, PatrimoineService
from session import Session
from domain.errors import *
from .ajouter_credit import AjouterCreditPage
from .credit_visualizer_page import CréditVisualizerPage

from ui.widgets import confirm_and_delete

class CreditsPage(QWidget):
    back_to_hub = Signal()
    open_invests = Signal()
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.patrimoine_service = appContext.patrimoine_service
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
        #layout.addWidget(self.btn_modifier)
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
        #self.btn_modifier.show()
        credit_id = credit_item.data(1)
        self.credit_service.set_credit_actif(credit_id)
        
    def ajouter_clicked(self):
        self.credit_service.set_credit_actif()
        self.navigator.go_to(Page.AJOUTER_CREDIT)    
            
    def supprimer_clicked(self):
        scenario = self.scenario_service.get_scenario_by_id(self.scenario_service.scenario_actif_id)
        credit = self.credit_service.get_credit_by_id(self.credit_service.credit_actif_id)

        if credit is None:
            QMessageBox.warning(self, "Erreur", "Aucun crédit sélectionné.")
            return

        try:
            if confirm_and_delete(self.patrimoine_service, scenario, credit, self):
                self.load()
        except QuantFolioError as e:
            QMessageBox.critical(self, "Suppression impossible", str(e))   
                 
    def load(self):
        scenario = self.scenario_service.get_scenario_by_id(self.scenario_service.scenario_actif_id)   
        if scenario:
            self.credit_service.set_credit_actif()
            self.scenario_label.setText(f"Scénario : {scenario.intitule}")

            self.liste_credits.clear()
            
            if self.session.current_user:
                for credit in (self.credit_service.get_all_credits_from_scenario(self.scenario_service.scenario_actif_id) or []):
                    banque = self.banque_service.get_banque_by_id(credit.id_banque)
                    widget_item= QListWidgetItem(f"Crédit n°{credit.id}, chez {banque.nom}, de {credit.montant}.00 €")
                    widget_item.setData(1, credit.id)
                    self.liste_credits.addItem(widget_item)
        else:
            self.navigator.go_to(Page.NO_SCENARIO)
        self.navigator.hold_page(Page.CREDITS)
            