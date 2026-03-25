
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox, QWidget, QVBoxLayout, QHBoxLayout,  QLabel, QPushButton, QLineEdit, QStackedWidget, QSizePolicy
)
from services import AppContext
from services.domain_services.metierService import MetierService
from session import Session

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
                
        layout.addWidget(intitule)
        layout.addWidget(self.intitule)
        
        #Boutons
        self.annuler_btn = QPushButton("Annuler x")
        self.enregistrer_btn = QPushButton("Enregister")
        
        layout.addWidget(self.enregistrer_btn)
        layout.addWidget(self.annuler_btn)
        
        #actions boutons
        self.annuler_btn.clicked.connect(self.back_to_hub.emit)
        self.enregistrer_btn.clicked.connect(self.enregistrer_clicked)
        
    def enregistrer_clicked(self):    
            
        intitule = self.intitule.text().strip()
        
        if intitule is not None:           
            data = {
                "ID USER" : self.session.current_user.id, 
                "INTITULE" : intitule,
            }
            
            scenario = self.scenario_service.update_scenario(None, data)
            self.scenario_service.set_scenario_actif(scenario)
            
            self.back_to_hub.emit()

        else: raise ValueError("Veuillez entrer un nom de scénario")
