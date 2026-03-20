from PySide6.QtWidgets import QListWidgetItem, QListWidget, QComboBox, QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel, QLineEdit
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from services import AppContext
from session import Session
from ui.widgets import GraphWidget
from utils.finance_format import euro

SOLDE_FONT = QFont()
SOLDE_FONT.setPointSize(40)
SOLDE_FONT.setBold(True)

class CbVisualizerPage(QWidget):
    back_to_hub = Signal()
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.banque_service = appContext.banque_service
        self.cb_service = appContext.cb_service
        self.scenario_service = appContext.scenario_service
        self.session = session
        self.depense_service = appContext.depense_service
        self.recette_service = appContext.recette_service
        
        self.selected_item : QListWidgetItem | None =  None
        
        layout = QVBoxLayout(self)
        
        self.scenario_label = QLabel("Scénario:")
        
        #Zone choix compte bancaire + solde
        cb_choix_widget = QWidget()
        cb_choix_layout = QHBoxLayout(cb_choix_widget)
        
        cb_choix_lbl = QLabel("Selectionner compte : ")
        self.cb_choix_list = QComboBox()
        self.cb_choix_list.setFixedSize(250,36)
        self.cb_choix_list.currentIndexChanged.connect(self.update_visualisation)
        self.solde_lbl = QLabel("Solde : ")
        self.solde_lbl.setFont(SOLDE_FONT)
        
        
        cb_choix_layout.addWidget(cb_choix_lbl)
        cb_choix_layout.addWidget(self.cb_choix_list)
        cb_choix_layout.addStretch()
        
        cb_choix_layout.addWidget(self.solde_lbl)
        
        graphe_wgt = QWidget()
        graphe_lyt = QVBoxLayout(graphe_wgt)
        graphe_lbl = QLabel("Evolution du solde au fil des mois :")
        graphe_figure =  GraphWidget()
        graphe_lyt.addWidget(graphe_lbl)
        graphe_lyt.addWidget(graphe_figure)
        
        transaction_widget = QWidget()
        transaction_layout = QVBoxLayout(transaction_widget)
        transac_label = QLabel("Transactions : ")
        transaction_layout.addWidget(transac_label)
        
        liste_widget = QWidget()
        liste_layout = QHBoxLayout(liste_widget)
        transaction_layout.addWidget(liste_widget)

        
        recette_layout = QVBoxLayout()
        depense_layout = QVBoxLayout()
        liste_layout.addLayout(recette_layout)
        liste_layout.addLayout(depense_layout)
        
        self.liste_recette = QListWidget()
        self.liste_depense = QListWidget()
        self.liste_recette.clicked.connect(self.on_recette_selected)
        self.liste_depense.clicked.connect(self.on_depense_selected)
        
        self.btn_suppr_recette = QPushButton("Supprimer recette")
        self.btn_suppr_depense = QPushButton("Supprimer dépense")
        self.btn_suppr_recette.clicked.connect(self.on_suppr_clicked)
        self.btn_suppr_depense.clicked.connect(self.on_suppr_clicked)
        self.btn_suppr_recette.hide()
        self.btn_suppr_depense.hide()
        
        recette_layout.addWidget(self.liste_recette)
        recette_layout.addWidget(self.btn_suppr_recette)
            
        depense_layout.addWidget(self.liste_depense)
        depense_layout.addWidget(self.btn_suppr_depense)

        #Ajout du layout général
        layout.addWidget(self.scenario_label)
        layout.addWidget(cb_choix_widget)
        layout.addStretch()
        layout.addWidget(graphe_wgt)
        layout.addWidget(transaction_widget)
        
        btn_retour = QPushButton("Retour")
        layout.addWidget(btn_retour)
        btn_retour.clicked.connect(self.back_to_hub.emit)
    
    def on_suppr_clicked(self):
        item_id = self.selected_item.data(1)
        item = self.depense_service.get_depense_by_id(item_id)
        if item:
            self.depense_service.delete_depense(item)
        item = self.recette_service.get_recette_by_id(item_id) 
        if item:       
            self.recette_service.delete_recette(item)
        self.update_visualisation()
        
        
        
    def on_depense_selected(self, item : QListWidgetItem):
        self.btn_suppr_depense.show()
        self.btn_suppr_recette.hide()
        
        self.selected_item = item
    def on_recette_selected(self, item : QListWidgetItem):
        self.btn_suppr_depense.hide()
        self.btn_suppr_recette.show()
        
        self.selected_item = item
        
    def update_visualisation(self):
        self.liste_depense.clear()
        self.liste_recette.clear()
        
        cb_id = self.cb_choix_list.currentData()
        self.solde_lbl.setText(f"Solde : {euro(self.cb_service.solde_from_cb(cb_id))}")
        depenses = self.depense_service.get_all_depense_from_cb(cb_id)
        recettes = self.recette_service.get_all_recette_from_cb(cb_id)
        
        for depense in depenses:
            depenseItem = QListWidgetItem(f"[{depense.nature}] {depense.intitule}, {depense.montant} €, {depense.frequence}")
            depenseItem.setData(1,depense.id)
            self.liste_depense.addItem(depenseItem)
            
        for recette in recettes:
            recetteItem = QListWidgetItem(f"[{recette.nature}] {recette.intitule}, {recette.montant} €, {recette.frequence}")
            recetteItem.setData(1,recette.id)
            self.liste_recette.addItem(recetteItem)
        
    def load(self):
        scenario = self.scenario_service.scenario_actif
        self.scenario_label.setText(f"Scénario : {scenario.intitule}")
        
        self.liste_depense.clear()
        self.liste_recette.clear()
        
        self.cb_choix_list.clear()
        cbs = self.cb_service.all_userCB_from_scenario(scenario.id)
        for cb in cbs:
            banque = self.banque_service.get_banque_by_id(cb.id_banque)
            self.cb_choix_list.addItem(f"{cb.type}, {banque.nom}", cb.id)
     
        self.btn_suppr_recette.hide()
        self.btn_suppr_depense.hide()
            


