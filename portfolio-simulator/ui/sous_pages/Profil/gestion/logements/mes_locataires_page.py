#flattened

from PySide6.QtCore import Signal
from PySide6.QtGui import QIntValidator, QDoubleValidator
from PySide6.QtWidgets import (
    QTableWidget, QTableWidgetItem,
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QLineEdit, QStackedWidget, QSizePolicy
)

from services import AppContext, Page
from session import Session

from utils.finance_format import euro
from utils.date import month_count
from datetime import date

class MesLocatairesPage(QWidget):
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.scenario_service = appContext.scenario_service
        self.invest_service = appContext.invest_service
        self.recette_service = appContext.recette_service
        self.session = session
        self.navigator = appContext.navigator
        
        layout = QVBoxLayout(self)
        
        self.hub_page = self.hub()        
        layout.addWidget(self.hub_page) 
        
    def hub(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        self.title = QLabel("Gestion Locatives")
        
        self.filter_wgt = QWidget()
        self.filter_layout = QHBoxLayout(self.filter_wgt)
        
        self.date_lbl = QLabel("Locataires antérieurs au ")
        self.month_input = QLineEdit("")
        self.month_input.setValidator(QIntValidator(0,12))
        self.month_input.setPlaceholderText("MM")
        
        self.year_input = QLineEdit("")
        self.year_input.setPlaceholderText("AAAA")
        self.year_input.setValidator(QIntValidator(1980, 2200))
        
        self.actualiser_date_btn = QPushButton("Actualiser")
        self.actualiser_date_btn.clicked.connect(self.load)
        
        self.effacer_filtre_btn = QPushButton("Effacer filtre")
        
        self.filter_layout.addWidget(self.date_lbl,1)
        self.filter_layout.addWidget(self.month_input,1)
        self.filter_layout.addWidget(self.year_input, 2)
        self.filter_layout.addWidget(self.actualiser_date_btn, 3)
        self.filter_layout.addWidget(self.effacer_filtre_btn,2)
                
        self.locataires_tab = QTableWidget()
        self.locataires_tab.setColumnCount(7)
        self.locataires_tab.setHorizontalHeaderLabels([
            "Titre", "Entrée", "Sortie", "Type","Ville","Surface","locataire"
        ])
        self.locataires_tab.cellClicked.connect(self.locataire_clicked)
        
        btns_wgt = QWidget()
        self.btns_lyt = QHBoxLayout(btns_wgt)
        
        left_btns_wgt = QWidget()
        self.left_btns_lyt = QHBoxLayout(left_btns_wgt)
        self.nouvelle_location_btn = QPushButton("Nouveau Locataire")
        
        right_btns_wgt = QWidget()
        self.right_btns_lyt = QHBoxLayout(right_btns_wgt)
        self.infos_btn = QPushButton("+ d'infos")
        self.retour_btn = QPushButton("Retour <-")
        self.supprimer_btn = QPushButton("Supprimer")
        
        self.btns_lyt.addWidget(left_btns_wgt)
        self.left_btns_lyt.addWidget(self.nouvelle_location_btn)

        self.btns_lyt.addStretch()
        
        self.btns_lyt.addWidget(right_btns_wgt)
        self.right_btns_lyt.addWidget(self.infos_btn)
        self.right_btns_lyt.addWidget(self.supprimer_btn)
        
        layout.addWidget(self.title)
        layout.addWidget(self.filter_wgt)
        layout.addWidget(self.locataires_tab)
        layout.addWidget(btns_wgt)
    
        layout.addStretch()
        layout.addWidget(self.retour_btn)
        
        self.supprimer_btn.clicked.connect(self.suppr_clicked)
        self.nouvelle_location_btn.clicked.connect(lambda: self.navigator.go_to(Page.NOUVEAU_LOCATAIRE))
        self.retour_btn.clicked.connect(lambda : self.navigator.go_to(Page.LOGEMENTS))
        self.infos_btn.hide()
        
        return page
    
    def locataire_clicked(self, row, col):
        self.supprimer_btn.show()
        
    def suppr_clicked(self):
        item_row = self.locataires_tab.currentRow()
        
        if item_row <0:
            return
        item_ref = self.locataires_tab.item(item_row, 0)
        if item_ref is None:
            return
        locataire = self.recette_service.get_recette_by_id(item_ref.data(1))
        bien_occupé = self.invest_service.get_by_id(locataire.id_investissement)
        if locataire is not None:
            self.recette_service.delete_recette(locataire)
        self.load()

    def load(self):
        scenario = self.scenario_service.scenario_actif
        
        locataires = self.recette_service.get_locataires_from_scenario(scenario.id) or []
        print(locataires)
        month = self.month_input.text().strip()
        year = self.year_input.text().strip()
        if month and year:
            date_seuil = date(int(year), int(month), 1)
        else:
            self.month_input.setText(str(scenario.date_in.month))
            self.year_input.setText(str(scenario.date_in.year))
            
            date_seuil = scenario.date_in
            
        self.locataires_tab.setRowCount(len(locataires))
        
        for i,locataire in enumerate(locataires):
            if locataire.date_in <= date_seuil:
                bien_loué = self.invest_service.get_by_id(locataire.id_investissement)
                print(bien_loué)
                try:
                    intitule = QTableWidgetItem(str(locataire.intitule))
                    intitule.setData(1,locataire.id)
                
                    self.locataires_tab.setItem(i,0, intitule)
                    self.locataires_tab.setItem(i,1, QTableWidgetItem(str(locataire.date_in)))
                    self.locataires_tab.setItem(i,2, QTableWidgetItem(str(locataire.date_out)))
                    self.locataires_tab.setItem(i,3,QTableWidgetItem(str(bien_loué.type)))
                    self.locataires_tab.setItem(i,4, QTableWidgetItem(str(bien_loué.localisation)))
                    self.locataires_tab.setItem(i,5, QTableWidgetItem(str(bien_loué.surface) + "m²"))
                    self.locataires_tab.setItem(i,6, QTableWidgetItem(str(euro(locataire.montant))))
                except Exception as e:
                    raise ValueError(str(e))

        self.infos_btn.hide()
        self.supprimer_btn.hide()
                
