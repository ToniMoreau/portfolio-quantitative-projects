
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox, QWidget, QVBoxLayout, QHBoxLayout,  QLabel, QPushButton, QLineEdit, QStackedWidget, QSizePolicy
)
from services import AppContext
from services.domain_services.metierService import MetierService
from session import Session

from datetime import date

class AddScenarioPage(QWidget):
    back_to_hub = Signal()
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.scenario_service = appContext.scenario_service
        self.session = session
        
        layout = QVBoxLayout(self)
        
        #Formulaire
        self.title =QLabel("Ajouter un scénario : ")
        
        intitule = QLabel("Intitule")
        self.intitule = QLineEdit()
        self.intitule.setPlaceholderText("Entrer le nom du scénario")
        
        date_wgt = QWidget()
        date_lyt=  QHBoxLayout(date_wgt)
        date_lbl = QLabel("Date de début du scénario : ")
        self.month_input = QLineEdit()
        self.month_input.setPlaceholderText("Mois")
        self.year_input = QLineEdit()
        self.year_input.setPlaceholderText("Année")
        
        date_lyt.addWidget(date_lbl)
        date_lyt.addWidget(self.month_input)
        date_lyt.addWidget(self.year_input)

        layout.addWidget(self.title)
        layout.addWidget(intitule)
        layout.addWidget(self.intitule)
        layout.addWidget(date_wgt)
                
        #Boutons
        self.annuler_btn = QPushButton("Annuler x")
        self.enregistrer_btn = QPushButton("Enregister")
        
        layout.addWidget(self.enregistrer_btn)
        layout.addWidget(self.annuler_btn)
        
        #actions boutons
        self.annuler_btn.clicked.connect(self.back_to_hub.emit)
        self.enregistrer_btn.clicked.connect(self.enregistrer_clicked)
        
    def enregistrer_clicked(self):    
        scenario = self.scenario_service.scenario_actif
        
        intitule = self.intitule.text().strip()
        month_in = self.month_input.text().strip()
        year_in  = self.year_input.text().strip()
        
        if scenario:
            id = scenario.id
            date_in = scenario.date_in
            
            intitule = scenario.intitule if not(intitule) else intitule
            month_in = date_in.month if not(month_in) else int(month_in)
            year_in = date_in.year if not(year_in) else int(year_in)

            date_in = date(year_in, month_in,1)
        else:
            id = None
            
            intitule = None if not(intitule) else intitule
            month_in = None if not(month_in) else int(month_in)
            year_in = None if not(year_in) else int(year_in)

            date_in = None if not(year_in and month_in) else date(year_in, month_in,1)
            
        if (intitule is None 
            or date_in is None):           
            raise ValueError("Veuillez tout renseigner.")
        else: 
            data = {
                "ID USER" : self.session.current_user.id, 
                "INTITULE" : intitule,
                "DATE IN"  : date_in
            }
            print(type(date_in))
            scenario = self.scenario_service.update_scenario(id, data)
            self.scenario_service.set_scenario_actif(scenario)
            
            self.back_to_hub.emit()
    
    def load(self):
        self.month_input.clear()
        self.year_input.clear()
        self.intitule.clear()
        scenario = self.scenario_service.scenario_actif
        if scenario:
            self.title.setText(f"Modifier le scénario {scenario.intitule}, début à {""}")
        else:
            self.title.setText("Ajouter un scénario")