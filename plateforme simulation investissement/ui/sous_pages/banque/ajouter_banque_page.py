from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel, QLineEdit
from PySide6.QtCore import Signal

from services import AppContext

class AjouterBanquePage(QWidget):
    back_to_hub = Signal()
    
    def __init__(self, appContext : AppContext, session):
        super().__init__()
        self.banque_service = appContext.banque_service
        self.session = session
        
        layout = QVBoxLayout(self)
        
        #Formulaire
        self.title =QLabel("Ajouter Banque : ")
        
        intitule = QLabel("Intitule")
        self.intitule = QLineEdit()
        self.intitule.setPlaceholderText("Entrer le nom de la banque")
        
        taux = QLabel("Taux appliqué aux crédits (%) : ")
        self.taux = QLineEdit()
        self.taux.setPlaceholderText("Entrer un taux en %")
        
        layout.addWidget(intitule)
        layout.addWidget(self.intitule)
        layout.addWidget(taux)
        layout.addWidget(self.taux)
        layout.addStretch()
        
        #Boutons
        self.annuler_btn = QPushButton("Annuler x")
        self.enregistrer_btn = QPushButton("Enregister")
        
        layout.addWidget(self.enregistrer_btn)
        layout.addWidget(self.annuler_btn)

        
        #actions boutons
        self.annuler_btn.clicked.connect(self.back_to_hub.emit)
        self.enregistrer_btn.clicked.connect(self.enregistrer_clicked)
        
    def enregistrer_clicked(self):
        banque = self.banque_service.banque_active
        intitule = self.intitule.text().strip()
        taux = self.taux.text().strip()

        if banque:
            id = banque.id
            intitule = banque.nom if not(intitule) else str(intitule)
            taux = banque.taux_credit_pct if not(taux) else float(taux)
        else:
            id = None
            intitule =None if not(intitule) else str(intitule)
            taux = None if not(taux) else float(taux)
            
        if (intitule is None 
            or taux is None):
            raise ValueError("Vous devez tout renseigner.")
        else:
            data = {}
            data["INTITULE"] = intitule
            data["TAUX CREDIT (%)"] = taux      
            
        banque = self.banque_service.update_banque(id, data)
        self.intitule.setText("")
        self.taux.setText("")
        self.back_to_hub.emit()
        
