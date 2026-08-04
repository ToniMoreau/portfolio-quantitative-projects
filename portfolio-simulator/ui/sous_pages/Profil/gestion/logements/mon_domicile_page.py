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

class MonDomicilePage(QWidget):
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.scenario_service = appContext.scenario_service
        self.depense_service = appContext.depense_service
        self.session = session
        self.navigator = appContext.navigator
        
        layout = QVBoxLayout(self)
        
        self.hub_page = self.hub()        
        layout.addWidget(self.hub_page) 
        
    def hub(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        self.title = QLabel("Locations")
        
        self.filter_wgt = QWidget()
        self.filter_layout = QHBoxLayout(self.filter_wgt)
        
        self.date_lbl = QLabel("Logements fréquentés antérieur au ")
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
                
        self.loyer_tab = QTableWidget()
        self.loyer_tab.setColumnCount(4)
        self.loyer_tab.setHorizontalHeaderLabels([
            "Titre", "Entrée", "Sortie", "Loyer"
        ])
        self.loyer_tab.cellClicked.connect(self.loyer_clicked)
        
        btns_wgt = QWidget()
        self.btns_lyt = QHBoxLayout(btns_wgt)
        
        left_btns_wgt = QWidget()
        self.left_btns_lyt = QHBoxLayout(left_btns_wgt)
        self.nouvelle_location_btn = QPushButton("Nouvelle Location")
        
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
        layout.addWidget(self.loyer_tab)
        layout.addWidget(btns_wgt)
    
        layout.addStretch()
        layout.addWidget(self.retour_btn)
        
        self.supprimer_btn.clicked.connect(self.suppr_clicked)
        self.nouvelle_location_btn.clicked.connect(lambda: self.navigator.go_to(Page.NOUVELLE_LOCATION))
        self.retour_btn.clicked.connect(lambda : self.navigator.go_to(Page.LOGEMENTS))
        self.infos_btn.hide()
        
        return page
    
    def loyer_clicked(self, row, col):
        self.supprimer_btn.show()
        
    def suppr_clicked(self):
        print("suppr clicked")
        item_row = self.loyer_tab.currentRow()
        print("ir", item_row)
        
        if item_row <0:
            return
        item_ref = self.loyer_tab.item(item_row, 0)
        print(item_ref)
        if item_ref is None:
            return
        print(item_ref.data(1))
        loyer = self.depense_service.get_depense_by_id(item_ref.data(1))
        print(loyer)
        if loyer is not None:
            self.depense_service.delete_depense(loyer)
        self.load()

    def load(self):
        scenario = self.scenario_service.scenario_actif
        
        loyers = self.depense_service.get_loyers_from_scenario(scenario.id) or []
        
        month = self.month_input.text().strip()
        year = self.year_input.text().strip()
        if month and year:
            date_seuil = date(int(year), int(month), 1)
        else:
            self.month_input.setText(str(scenario.date_in.month))
            self.year_input.setText(str(scenario.date_in.year))
            
            date_seuil = scenario.date_in
            
        self.loyer_tab.setRowCount(len(loyers))
        
        for i,loyer in enumerate(loyers):
            if loyer.date_in <= date_seuil:
                intitule = QTableWidgetItem(str(loyer.intitule))
                intitule.setData(1,loyer.id)
                
                self.loyer_tab.setItem(i,0, intitule)
                self.loyer_tab.setItem(i,1, QTableWidgetItem(str(loyer.date_in)))
                self.loyer_tab.setItem(i,2, QTableWidgetItem(str(loyer.date_out)))
                self.loyer_tab.setItem(i,3, QTableWidgetItem(str(euro(loyer.montant))))

        self.infos_btn.hide()
        self.supprimer_btn.hide()
                
