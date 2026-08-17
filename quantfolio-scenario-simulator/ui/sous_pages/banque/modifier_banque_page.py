#flattened

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel, QLineEdit
from PySide6.QtCore import Signal

from services import AppContext, Page

class ModifierBanqueP(QWidget):
    
    def __init__(self, appContext : AppContext, session):
        super().__init__()
        self.banque_service = appContext.banque_service
        self.session = session
        self.navigator = appContext.navigator
        layout = QVBoxLayout(self)
        
        #Formulaire
        self.title =QLabel("Modifier Banque : ")
        
        intitule = QLabel("Intitule")
        self.intitule = QLineEdit()
        self.intitule.setPlaceholderText("Entrer le nom de la banque")
                
        layout.addWidget(intitule)
        layout.addWidget(self.intitule)
        
        #Boutons
        self.annuler_btn = QPushButton("Annuler x")
        self.enregistrer_btn = QPushButton("Enregister")
        
        layout.addWidget(self.enregistrer_btn)
        layout.addWidget(self.annuler_btn)

        
        #actions boutons
        self.annuler_btn.clicked.connect(lambda : self.navigator.go_to(Page.BANQUE_STANDALONE))
        self.enregistrer_btn.clicked.connect(self.enregistrer_clicked)
        
    def enregistrer_clicked(self):
        data = {}
        intitule = self.intitule.text().strip()
        if intitule:
            data["INTITULE"] = intitule
            
        banque = self.banque_service.update_banque(self.banque_service.banque_active.id, data)
        self.banque_service.set_banque_active(banque)
        self.navigator.go_to(Page.BANQUE_STANDALONE)
