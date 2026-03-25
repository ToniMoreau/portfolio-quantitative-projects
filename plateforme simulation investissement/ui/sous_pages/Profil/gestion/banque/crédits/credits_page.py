from PySide6.QtWidgets import QListWidget, QListWidgetItem, QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel
from PySide6.QtCore import Signal

from services import AppContext
from session import Session

from .ajouter_credit import AjouterCreditPage
from .credit_visualizer_page import CréditVisualizerPage

class CreditsPage(QWidget):
    back_to_hub = Signal()
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.credit_service = appContext.credit_service
        self.session = session
        self.banque_service = appContext.banque_service
        self.scenario_service = appContext.scenario_service
        
        self.mlayout = QVBoxLayout(self)
        
        self.credit_visualizer = CréditVisualizerPage(appContext, self.session)
        self.ajouter_credit_page = AjouterCreditPage(appContext, self.session)
        self.credit_hub = self.credit_hub_page()
        
        self.stack = QStackedWidget()
        self.stack.addWidget(self.credit_hub) #index0
        self.stack.addWidget(self.credit_visualizer) #index1
        self.stack.addWidget(self.ajouter_credit_page) #index2
        
        self.mlayout.addWidget(self.stack)
        
        self.stack.setCurrentIndex(0)
        self.ajouter_credit_page.back_to_hub.connect(self.load)
        self.credit_visualizer.back_to_hub.connect(self.load)

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
        
        if self.session.current_user:
            print(self.session.current_user)
            for credit in self.credit_service.get_all_credits_from_scenario(self.scenario_service.scenario_actif.id):
                banque = self.banque_service.get_banque_by_id(credit.id_banque)
                widget_item= QListWidgetItem(f"Crédit n°{credit.id}, chez {banque.nom}, de {credit.montant}.00 €")
                widget_item.setData(1, credit.id)
                self.liste_credits.addItem(widget_item)
                
        layout.addStretch()
        self.visualiser = QPushButton("Visualiser compte")
        self.btn_ajouter   = QPushButton("Ajouter un crédit")
        self.btn_supprimer = QPushButton("Supprimer ce crédit")
        self.btn_modifier  = QPushButton("Modifier ce crédit")
        
        layout.addWidget(self.visualiser)
        layout.addWidget(self.btn_ajouter)
        layout.addWidget(self.btn_supprimer)
        layout.addWidget(self.btn_modifier)
        self.visualiser.hide()
        self.btn_supprimer.hide()
        self.btn_modifier.hide()
        
        self.visualiser.clicked.connect(lambda : self.load_index(1))
        self.btn_ajouter.clicked.connect(self.ajouter_clicked)
        self.btn_modifier.clicked.connect(lambda : self.load_index(2))
        self.btn_supprimer.clicked.connect(self.supprimer_clicked)
        
        btn_retour = QPushButton("Retour")
        layout.addWidget(btn_retour)
        btn_retour.clicked.connect(self.back_to_hub.emit)

        return page
    
    def load_index(self, index):
        self.stack.setCurrentIndex(index)
        page = self.stack.currentWidget()
        if hasattr(page, "load"):
            page.load()
            
    def btn_credit_clicked(self, credit_item : QListWidgetItem):
        self.visualiser.show()
        self.btn_supprimer.show()
        self.btn_modifier.show()
        credit_id = credit_item.data(1)
        credit = self.credit_service.get_credit_by_id(credit_id)
        self.credit_service.set_credit_actif(credit)
        
    def ajouter_clicked(self):
        self.credit_service.set_credit_actif()
        self.load_index(2)
        
    def supprimer_clicked(self):
        self.credit_service.delete_credit(self.credit_service.credit_actif)
        self.load()
        
    def load(self):
        self.mlayout.removeWidget(self.stack)
    
        self.credit_hub = self.credit_hub_page()
        self.stack = QStackedWidget()
        self.stack.addWidget(self.credit_hub)
        self.stack.addWidget(self.credit_visualizer)
        self.stack.addWidget(self.ajouter_credit_page)
        
        self.mlayout.addWidget(self.stack)
        self.stack.setCurrentIndex(0)
        
        self.credit_service.set_credit_actif()
        self.scenario_label.setText(f"Scénario : {self.scenario_service.scenario_actif.intitule}")

        