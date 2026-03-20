from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QListWidgetItem, QListWidget, QComboBox, QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel, QLineEdit
from PySide6.QtCore import Signal
from utils.finance_format import euro, percent
from services import AppContext,CreditPdfExporter
from session import Session


class CréditVisualizerPage(QWidget):
    back_to_hub = Signal()
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.banque_service = appContext.banque_service
        self.credit_service = appContext.credit_service
        self.scenario_service = appContext.scenario_service
        self.session = session
        self.depense_service = appContext.depense_service
        self.recette_service = appContext.recette_service
        
        self.exporter = CreditPdfExporter()
        
        self.selected_item : QListWidgetItem | None =  None
        
        layout = QVBoxLayout(self)
        
        self.scenario_label = QLabel("Scénario:")
        choix_credit = QLabel("Selectionner crédit : ")
        self.choix_credit = QComboBox()
        self.choix_credit.currentIndexChanged.connect(self.update_visualisation)
        
        self.montant = QLabel("A rembourser : ")
        
        transac_label = QLabel("Amortissement")
        
        liste_layout = QHBoxLayout()
        amorti_layout = QVBoxLayout()
          

        
        self.amorti_table = QTableWidget()
        
        amorti_layout.addWidget(self.amorti_table) 
        liste_layout.addLayout(amorti_layout)
                
        layout.addWidget(self.scenario_label)
        layout.addWidget(choix_credit) 
        layout.addWidget(self.choix_credit) 
        layout.addWidget(self.montant)
        layout.addStretch()
        layout.addWidget(transac_label)
        
        layout.addLayout(liste_layout)
        
        btn_export = QPushButton("Exporter PDF")
        btn_retour = QPushButton("Retour")
        layout.addWidget(btn_export)
        layout.addWidget(btn_retour)
        btn_export.clicked.connect(self.export_clicked)
        btn_retour.clicked.connect(self.back_to_hub.emit)        
    
    def export_clicked(self): 
        credit_id = self.choix_credit.currentData()
        if credit_id is None:
            return
        
        amortissement = self.credit_service.tableau_amortissement(credit_id)
        credit = self.credit_service.get_credit_by_id(credit_id)
        
        self.exporter.export_amortissement(credit, amortissement, "amortissement.pdf")


    def update_visualisation(self):
        self.amorti_table.clear()
          
        credit_id = self.choix_credit.currentData()
        if credit_id is None:
            return
        
        credit = self.credit_service.get_credit_by_id(credit_id)
        self.montant.setText(f"Emprunt : {credit.montant:.2f} €")
        amortissement = self.credit_service.tableau_amortissement(credit_id)
        colonnes = list(amortissement.keys())
        nb_lignes = len(amortissement[colonnes[0]]) if colonnes else 0
        
        self.amorti_table.setColumnCount(len(colonnes))
        self.amorti_table.setRowCount(nb_lignes)
        self.amorti_table.setHorizontalHeaderLabels(colonnes)
            
        for i in range(nb_lignes):
            for j, categorie in enumerate(colonnes):
                if categorie == "ANNEE":
                    self.amorti_table.setItem(i,j, QTableWidgetItem(str(amortissement[categorie][i])))
                elif categorie == "TAUX INTERET (PCT)":
                    self.amorti_table.setItem(i,j, QTableWidgetItem(percent(amortissement[categorie][i])))
                else:
                    self.amorti_table.setItem(i,j, QTableWidgetItem(euro(amortissement[categorie][i])))
        self.amorti_table.resizeColumnsToContents()
        

        
    def load(self):
        scenario = self.scenario_service.scenario_actif
        self.scenario_label.setText(f"Scénario : {scenario.intitule}")
        
        self.amorti_table.clear()   
        self.choix_credit.clear()
        
        credits = self.credit_service.get_all_credits_from_scenario(scenario.id)
        
        for cred in credits:
            banque = self.banque_service.get_banque_by_id(cred.id_banque)
            self.choix_credit.addItem(f"{cred.montant}, {banque.nom}", cred.id)
                


