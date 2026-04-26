from PySide6.QtWidgets import QListWidget, QListWidgetItem, QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel
from PySide6.QtCore import Signal

from utils.finance_format import euro
from services import AppContext
from session import Session
from .ajouter_compte_bancaire import AjouterCompteBancairePage
from .cb_visualizer_page import CbVisualizerPage

class ComptesBancairesPage(QWidget):
    back_to_hub = Signal()
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.cb_service = appContext.cb_service
        self.recette_service = appContext.recette_service
        self.depense_service = appContext.depense_service
        self.credit_service = appContext.credit_service
        self.metier_service = appContext.metier_service
        self.session = session
        self.banque_service = appContext.banque_service
        self.scenario_service = appContext.scenario_service        
        
        self.mlayout = QVBoxLayout(self)
        
        self.cb_visualizer_page = CbVisualizerPage(appContext, self.session)
        self.ajouter_cb_page = AjouterCompteBancairePage(appContext, self.session)
        self.cb_hub = self.cb_hub_page()
        
        self.stack = QStackedWidget()
        self.stack.addWidget(self.cb_hub) #index 0
        self.stack.addWidget(self.cb_visualizer_page) #index 1
        self.stack.addWidget(self.ajouter_cb_page) # index 2
        
        self.mlayout.addWidget(self.stack)
        
        self.stack.setCurrentIndex(0)
        self.ajouter_cb_page.back_to_hub.connect(self.load)
        self.cb_visualizer_page.back_to_hub.connect(self.load)
        
    def cb_hub_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        title = QLabel("Comptes Bancaires")
        self.scenario_label = QLabel()
        layout.addWidget(title)
        layout.addWidget(self.scenario_label)
        
        self.btn_ajouter   = QPushButton("Ajouter un compte")
        layout.addWidget(self.btn_ajouter)
        
        self.liste_comptes = QListWidget()
        self.liste_comptes.clicked.connect(self.btn_cb_clicked)

        if self.session.current_user:
            cbs = self.cb_service.all_userCB_from_scenario(self.scenario_service.scenario_actif.id)
            for cb in cbs:
                banque = self.banque_service.get_banque_by_id(cb.id_banque)
                date_solde = self.scenario_service.scenario_actif.date_in
                cb_item = QListWidgetItem(f"compte {cb.type} n°{cb.id}, chez {banque.nom} | {euro(self.cb_service.solde_from_cb(self.scenario_service.scenario_actif.date_in, cb.id,date_solde ).solde)}")
                cb_item.setData(1, cb.id)
                self.liste_comptes.addItem(cb_item)
                
        layout.addWidget(self.liste_comptes)
        layout.addStretch()
        
        self.visualiser = QPushButton("Visualiser compte")
        self.btn_supprimer = QPushButton("Supprimer ce compte")
        self.btn_modifier  = QPushButton("Modifier ce compte")
        
        self.information_msg = QLabel("")
        self.information_msg.hide()
        
        layout.addWidget(self.visualiser)
        layout.addWidget(self.btn_supprimer)
        layout.addWidget(self.btn_modifier)
        self.visualiser.hide()
        self.btn_supprimer.hide()
        self.btn_modifier.hide()
        layout.addWidget(self.information_msg)
        
        self.btn_ajouter.clicked.connect(self.ajouter_clicked)
        self.visualiser.clicked.connect(lambda : self.load_index(1))
        self.btn_modifier.clicked.connect(lambda : self.load_index(2))
        self.btn_supprimer.clicked.connect(self.supprimer_clicked)
        
        btn_retour = QPushButton("Retour")
        layout.addWidget(btn_retour)
        btn_retour.clicked.connect(self.back_to_hub.emit)

        return page
    
    def btn_cb_clicked(self, cb_item : QListWidgetItem):
        self.visualiser.show()
        self.btn_supprimer.show()
        self.btn_modifier.show()
        
        cb_id = cb_item.data(1)
        cb = self.cb_service.get_cb_by_id(cb_id)
        self.cb_service.set_cb_actif(cb)
    
    
    def ajouter_clicked(self):
        self.cb_service.set_cb_actif()
        self.stack.setCurrentIndex(2)
        
    def supprimer_clicked(self):
        cb_id = self.liste_comptes.currentItem().data(1)
        credit = self.credit_service.get_by_({"ID COMPTE" : cb_id})
        metier = self.metier_service.get_by_({"ID COMPTE" : cb_id})
        if credit is not None:
            self.information_msg.setText("Suppression Impossible, un crédit est encore associé.")
            return
        if metier is not None:
            self.information_msg.setText("Suppression Impossible, un métier est encore associé.")
            return
        print("la")
        self.information_msg.setText("")
        recettes = self.recette_service.get_all_recette_from_cb(cb_id)
        depenses = self.depense_service.get_all_depense_from_cb(cb_id)

        for recette in recettes:
            self.recette_service.delete_recette(recette)
        for depense in depenses:
            self.depense_service.delete_depense(depense)
            
        self.cb_service.delete_cb(self.cb_service.get_cb_by_id(cb_id))
        self.load()
        
    def load(self):
        self.mlayout.removeWidget(self.stack)
    
        self.cb_hub = self.cb_hub_page()
        self.stack = QStackedWidget()
        
        self.stack.addWidget(self.cb_hub)
        self.stack.addWidget(self.cb_visualizer_page)
        self.stack.addWidget(self.ajouter_cb_page)
        
        self.mlayout.addWidget(self.stack)
        self.stack.setCurrentIndex(0)
        
        self.cb_service.set_cb_actif()
        self.scenario_label.setText(f"Scénario : {self.scenario_service.scenario_actif.intitule}")

        self.information_msg.setText("")
        
    def load_index(self, index):
        self.stack.setCurrentIndex(index)
        page = self.stack.currentWidget()
        if hasattr(page, "load"):
            page.load()
