#flattened

from PySide6.QtWidgets import QListWidget, QListWidgetItem, QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel
from PySide6.QtCore import Signal

from utils.finance_format import euro
from services import AppContext, Page
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
        self.navigator = appContext.navigator 
        
        self.mlayout = QVBoxLayout(self)
        
        self.cb_hub = self.cb_hub_page()
        
        self.mlayout.addWidget(self.cb_hub)    
                    
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
        self.visualiser.clicked.connect(lambda : self.navigator.go_to(Page.CB_VISUALIZER))
        self.btn_modifier.clicked.connect(lambda : self.navigator.go_to(Page.AJOUTER_COMPTE_BANCAIRE))
        self.btn_supprimer.clicked.connect(self.supprimer_clicked)
        
        btn_retour = QPushButton("Retour")
        layout.addWidget(btn_retour)
        btn_retour.clicked.connect(lambda : self.navigator.go_to(Page.BANQUE_HUB))

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
        self.navigator.go_to(Page.AJOUTER_COMPTE_BANCAIRE)
        
    def supprimer_clicked(self):
        cb_id = self.liste_comptes.currentItem().data(1)
        credit = self.credit_service.get_by_criterias({"ID COMPTE" : cb_id})
        metier = self.metier_service.get_by_criterias({"ID COMPTE" : cb_id})
        if credit is not None:
            self.information_msg.setText("Suppression Impossible, un crédit est encore associé.")
            return
        if metier is not None:
            self.information_msg.setText("Suppression Impossible, un métier est encore associé.")
            return
        self.information_msg.setText("")
        recettes = self.recette_service.get_all_recette_from_cb(cb_id)
        depenses = self.depense_service.get_all_depense_from_cb(cb_id)

        for recette in recettes:
            self.recette_service.delete_recette(recette.id)
        for depense in depenses:
            self.depense_service.delete_depense(depense.id)
            
        self.cb_service.delete_cb(cb_id)
        self.load()
        
    def load(self):  
        scenario = self.scenario_service.get_scenario_by_id(self.scenario_service.scenario_actif_id)   
        if scenario:
            self.cb_service.set_cb_actif()
            self.scenario_label.setText(f"Scénario : {scenario.intitule}")

            self.liste_comptes.clear()
            if self.session.current_user:
                cbs = self.cb_service.all_userCB_from_scenario(scenario.id)
                for cb in cbs:
                    banque = self.banque_service.get_banque_by_id(cb.id_banque)
                    date_solde = scenario.date_in
                    cb_item = QListWidgetItem(f"compte {cb.type} n°{cb.id}, chez {banque.nom} | {euro(self.cb_service.solde_from_cb(scenario.date_in, cb.id,date_solde ).solde)}")
                    cb_item.setData(1, cb.id)
                    self.liste_comptes.addItem(cb_item)


            self.information_msg.setText("")
        else:
            self.navigator.go_to(Page.NO_SCENARIO)
        self.navigator.hold_page(Page.NO_SCENARIO)
