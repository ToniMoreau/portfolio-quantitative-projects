#flattened 

from PySide6.QtWidgets import QMessageBox, QTableWidget, QTableWidgetItem,QListWidgetItem, QListWidget, QComboBox, QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel, QLineEdit
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont, QIntValidator
from services import AppContext, Page, PatrimoineService
from session import Session
from domain.errors import *
from ui.widgets import GraphWidget
from utils.finance_format import euro
from datetime import date
from utils.date import add_months, month_range
from ui.widgets import confirm_and_delete
from domain.entities import Depense, Recette
SOLDE_FONT = QFont()
SOLDE_FONT.setPointSize(40)
SOLDE_FONT.setBold(True)

class CbVisualizerPage(QWidget):
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.patrimoine_service = appContext.patrimoine_service
        self.banque_service = appContext.banque_service
        self.cb_service = appContext.cb_service
        self.scenario_service = appContext.scenario_service
        self.session = session
        self.depense_service = appContext.depense_service
        self.recette_service = appContext.recette_service
        self.transaction_service = appContext.transaction_service
        self.navigator = appContext.navigator
        
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
        
        self.date_visu_lbl = QLabel("date :")
        self.month_visu_input = QLineEdit(f"")
        self.month_visu_input.setValidator(QIntValidator(0,12))
        self.month_visu_input.textChanged.connect(self.update_visualisation)
        self.year_visu_input = QLineEdit(f"")
        self.year_visu_input.setValidator(QIntValidator(1980,2200))
        self.year_visu_input.textChanged.connect(self.update_visualisation)
        
        cb_choix_layout.addWidget(cb_choix_lbl)
        cb_choix_layout.addWidget(self.cb_choix_list)
        cb_choix_layout.addStretch()
        cb_choix_layout.addWidget(self.date_visu_lbl)
        cb_choix_layout.addWidget(self.month_visu_input)
        cb_choix_layout.addWidget(self.year_visu_input)
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
        self.transac_table.cellClicked.connect(self.cell_clicked)
        
        self.suppr_objet = QPushButton("Supprimer x")
        transaction_layout.addWidget(self.suppr_objet)
        self.suppr_objet.clicked.connect(self.on_suppr_clicked)
        self.suppr_objet.hide()

        donnees_lyt.addWidget(graphe_wgt,2)
        donnees_lyt.addWidget(transaction_widget,1)
        
        #Ajout du layout général
        layout.addWidget(self.scenario_label)
        layout.addWidget(cb_choix_widget)
        layout.addStretch()
        layout.addWidget(donnee_wgt)
        
        btn_retour = QPushButton("Retour")
        layout.addWidget(btn_retour)
        btn_retour.clicked.connect(lambda : self.navigator.go_to(Page.COMPTES_BANCAIRES))
        
    def cell_clicked(self, row, col):
        item_ref = self.transac_table.item(row, 0)
        if item_ref is None:
            self.suppr_objet.hide()
            return
        depense_id = item_ref.data(1)
        depense = self.depense_service.get_depense_by_id(depense_id)
        recette = self.recette_service.get_recette_by_id(depense_id)
        if recette is None and depense is None:
            self.suppr_objet.hide()
            return
        if depense is not None:
            if depense.nature in self.depense_service.natures_customs:
                self.suppr_objet.show()
                return
        if recette is not None:
            if recette.nature in self.recette_service.natures_customs:
                self.suppr_objet.show()
                return
        self.suppr_objet.hide()
    
    def _route_deletion(self, entity):
        """Returns one of: 'propagate', 'direct', 'blocked'."""
        if isinstance(entity, Depense):
            if entity.id_transaction is not None:
                return 'propagate'
            if entity.id_source is None:
                return 'direct'
            return 'blocked'

        else:  # Recette
            if entity.id_source is None or entity.nature == "Locataires":
                return 'propagate'
            return 'blocked'    
        
    def on_suppr_clicked(self):
        scenario = self.scenario_service.get_scenario_by_id(self.scenario_service.scenario_actif_id)
        item_row = self.transac_table.currentRow()
        if item_row <0:
            return
        item_ref = self.transac_table.item(item_row, 0)
        if item_ref is None:
            return
        entity_id = item_ref.data(1)
        entity = self.recette_service.get_recette_by_id(entity_id) or self.depense_service.get_depense_by_id(entity_id)

        if entity is None:
            QMessageBox.warning(self, "Erreur", "Aucun élément sélectionné.")
            return

        route = self._route_deletion(entity)

        if route == 'blocked':
            QMessageBox.warning(self, "Suppression impossible",
                                "Cet élément est généré automatiquement et ne peut pas être supprimé directement.")
            return

        try:
            if route == 'propagate':
                if confirm_and_delete(self.patrimoine_service, scenario, entity, self):
                    self.update_visualisation()
            else:  # direct
                self.depense_service.delete_depense(entity.id)
                self.update_visualisation()
        except QuantFolioError as e:
            QMessageBox.critical(self, "Suppression impossible", str(e))
        except (ValueError, AttributeError) as e:
            QMessageBox.critical(self, "Erreur inattendue", str(e))            
                
    def update_visualisation(self):
        scenario = self.scenario_service.get_scenario_by_id(self.scenario_service.scenario_actif_id)
        
        cb_id = self.cb_choix_list.currentData()
        month_actif = self.month_visu_input.text().strip()
        year_actif = self.year_visu_input.text().strip()
        
        
        if cb_id and month_actif and year_actif:
            month_actif = int(month_actif)
            year_actif = int(year_actif)
    
            date_visu = date(year_actif, month_actif, 1)
            previous_date = add_months(date_visu, -1)
            
            if cb_id == "all":
                cb_id = self.cb_service.all_userCB_from_scenario(scenario.id)
                cb_id = [cb.id for cb in cb_id]
            solde_du_mois_precedent = self.cb_service.solde_from_cb(scenario.date_in, cb_id, previous_date)
            solde = self.cb_service.solde_from_cb(scenario.date_in,cb_id, date_visu)
            self.solde_lbl.setText(f"Solde : {euro(solde.solde)}")
            
            depenses = self.depense_service.get_all_depense_from_cb(cb_id, date_visu)
            recettes = self.recette_service.get_all_recette_from_cb(cb_id, date_visu)
            self.transac_table.clearContents()
            self.transac_table.setRowCount(len(depenses) + len(recettes) +3)
            i=0  
            if date_visu > scenario.date_in:
                self.transac_table.setItem(i,0,QTableWidgetItem("Suivi"))
                self.transac_table.setItem(i,2,QTableWidgetItem(f"Solde au {previous_date}"))
                if solde_du_mois_precedent.solde >=0:
                    col = 4
                else : col = 3
                self.transac_table.setItem(i,col,QTableWidgetItem(str(euro(abs(solde_du_mois_precedent.solde)))))
                i+=1
                
                self.transac_table.setItem(i,0,QTableWidgetItem("Suivi"))
                self.transac_table.setItem(i,2,QTableWidgetItem(f"Intérêts du {date_visu}"))
                self.transac_table.setItem(i,4,QTableWidgetItem(str(euro((solde.interets_dernier_mois)))))
                i+=1
            

            for depense in depenses:
                natureDItem = QTableWidgetItem(str(depense.nature))
                natureDItem.setData(1, depense.id)
                
                frequenceItem = QTableWidgetItem(str(depense.frequence))
                intituleItem = QTableWidgetItem(str(depense.intitule))
                montantItem = QTableWidgetItem(str(euro(depense.montant)))
                
                self.transac_table.setItem(i,0, natureDItem)
                self.transac_table.setItem(i,1, frequenceItem)
                self.transac_table.setItem(i,2, intituleItem)
                self.transac_table.setItem(i,3, montantItem)
                i+=1
                
            for recette in recettes:
                natureRItem = QTableWidgetItem(str(recette.nature))
                natureRItem.setData(1, recette.id)
                frequenceItem = QTableWidgetItem(str(recette.frequence))
                intituleItem = QTableWidgetItem(str(recette.intitule))
                montantItem = QTableWidgetItem(str(euro(recette.montant)))
                
                self.transac_table.setItem(i,0, natureRItem)
                self.transac_table.setItem(i,1, frequenceItem)
                self.transac_table.setItem(i,2, intituleItem)
                self.transac_table.setItem(i,4, montantItem)
                i+=1
            self.transac_table.resizeColumnsToContents()
            
            dates = list(month_range(date_visu, add_months(date_visu,12)))
            soldes_avec = []
            soldes_sans = []
            for periode in dates:
                solde = self.cb_service.solde_from_cb(scenario.date_in, cb_id, date_valide=periode)
                soldes_avec.append(solde.solde)
                soldes_sans.append(solde.solde_hors_interets)
                
            self.graphe_figure.plot(dates, [soldes_avec,soldes_sans], ["Avec Intérêts", "Sans Intérêts"])
        
    def load(self):
        scenario = self.scenario_service.get_scenario_by_id(self.scenario_service.scenario_actif_id)
        if scenario:
            date_debut = scenario.date_in

            self.scenario_label.setText(f"Scénario : {scenario.intitule}")
                    
            self.month_visu_input.setText(f"{date_debut.month}")
            self.year_visu_input.setText(f"{date_debut.year}")
            
            self.cb_choix_list.clear()
            cbs = self.cb_service.all_userCB_from_scenario(scenario.id)
            self.cb_choix_list.addItem("Tous les comptes","all")
            for cb in cbs:
                banque = self.banque_service.get_banque_by_id(cb.id_banque)
                self.cb_choix_list.addItem(f"{cb.type}, {banque.nom}", cb.id)
                    
            self.suppr_objet.hide()
        else:
            self.navigator.go_to(Page.NO_SCENARIO)
        self.navigator.hold_page(Page.CB_VISUALIZER)
