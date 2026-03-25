from PySide6.QtWidgets import QTableWidget, QTableWidgetItem,QListWidgetItem, QListWidget, QComboBox, QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel, QLineEdit
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont, QIntValidator
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
        
        self.date_visu_lbl = QLabel("mois n°:")
        self.date_visu_input = QLineEdit("0")
        self.date_visu_input.setValidator(QIntValidator(0,1200))
        self.date_visu_input.textChanged.connect(self.update_visualisation)
        
        
        cb_choix_layout.addWidget(cb_choix_lbl)
        cb_choix_layout.addWidget(self.cb_choix_list)
        cb_choix_layout.addStretch()
        cb_choix_layout.addWidget(self.date_visu_lbl)
        cb_choix_layout.addWidget(self.date_visu_input)
        cb_choix_layout.addWidget(self.solde_lbl)
        
        donnee_wgt = QWidget()
        donnees_lyt = QHBoxLayout(donnee_wgt)
        
        graphe_wgt = QWidget()
        graphe_lyt = QVBoxLayout(graphe_wgt)
        graphe_lbl = QLabel("Evolution du solde au fil des mois :")
        self.graphe_figure =  GraphWidget()
        graphe_lyt.addWidget(graphe_lbl)
        graphe_lyt.addWidget(self.graphe_figure)
        
        transaction_widget = QWidget()
        transaction_layout = QVBoxLayout(transaction_widget)
        transac_label = QLabel("Transactions : ")
        transaction_layout.addWidget(transac_label)
        
        self.transac_table = QTableWidget()
        transaction_layout.addWidget(self.transac_table)
        self.transac_table.setColumnCount(5)
        sequence = ["Nature", "Fréquence","Intitule","Débit", "Crédit"]
        self.transac_table.setHorizontalHeaderLabels(sequence)

        donnees_lyt.addWidget(graphe_wgt,2)
        donnees_lyt.addWidget(transaction_widget,1)
        
        #Ajout du layout général
        layout.addWidget(self.scenario_label)
        layout.addWidget(cb_choix_widget)
        layout.addStretch()
        layout.addWidget(donnee_wgt)
        
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
        self.selected_item = item
    def on_recette_selected(self, item : QListWidgetItem):       
        self.selected_item = item
        
    def update_visualisation(self):
    
        cb_id = self.cb_choix_list.currentData()
        mois_actif = self.date_visu_input.text().strip()
        
        if cb_id and mois_actif:
            mois_actif = int(mois_actif)
            solde_du_mois_precedent = self.cb_service.solde_from_cb(cb_id, max(mois_actif-1,0)) if mois_actif > 0 else 0
            self.solde_lbl.setText(f"Solde : {euro(self.cb_service.solde_from_cb(cb_id, mois_actif))}")
            depenses = self.depense_service.get_all_depense_from_cb(cb_id, mois_actif)
            recettes = self.recette_service.get_all_recette_from_cb(cb_id, mois_actif)
            
            self.transac_table.clearContents()
            self.transac_table.setRowCount(len(depenses) + len(recettes) +1)
            i=0
            if mois_actif >0:
                self.transac_table.setItem(i,0,QTableWidgetItem("Suivi"))
                self.transac_table.setItem(i,2,QTableWidgetItem(f"Solde mois n°{mois_actif -1}"))
                if solde_du_mois_precedent >=0:
                    col = 4
                else : col = 3
                self.transac_table.setItem(i,col,QTableWidgetItem(str(euro(abs(solde_du_mois_precedent)))))
                i+=1
            
            for depense in depenses:
                natureItem = QTableWidgetItem(str(depense.nature))
                frequenceItem = QTableWidgetItem(str(depense.frequence))
                intituleItem = QTableWidgetItem(str(depense.intitule))
                montantItem = QTableWidgetItem(str(euro(depense.montant)))
                
                self.transac_table.setItem(i,0, natureItem)
                self.transac_table.setItem(i,1, frequenceItem)
                self.transac_table.setItem(i,2, intituleItem)
                self.transac_table.setItem(i,3, montantItem)
                i+=1
                
            for recette in recettes:
                natureItem = QTableWidgetItem(str(recette.nature))
                frequenceItem = QTableWidgetItem(str(recette.frequence))
                intituleItem = QTableWidgetItem(str(recette.intitule))
                montantItem = QTableWidgetItem(str(euro(recette.montant)))
                
                self.transac_table.setItem(i,0, natureItem)
                self.transac_table.setItem(i,1, frequenceItem)
                self.transac_table.setItem(i,2, intituleItem)
                self.transac_table.setItem(i,4, montantItem)
                i+=1
            self.transac_table.resizeColumnsToContents()
            n_mois = []
            montant_mois = []
            for i in range(mois_actif, mois_actif+12):
                n_mois.append(i)
                montant_mois.append(self.cb_service.solde_from_cb(cb_id, date_valide=i))
            
            self.graphe_figure.plot(n_mois, montant_mois)
        
    def load(self):
        scenario = self.scenario_service.scenario_actif
        self.scenario_label.setText(f"Scénario : {scenario.intitule}")
                
        self.date_visu_input.setText("0")
        self.cb_choix_list.clear()
        cbs = self.cb_service.all_userCB_from_scenario(scenario.id)
        for cb in cbs:
            banque = self.banque_service.get_banque_by_id(cb.id_banque)
            self.cb_choix_list.addItem(f"{cb.type}, {banque.nom}", cb.id)
                 


