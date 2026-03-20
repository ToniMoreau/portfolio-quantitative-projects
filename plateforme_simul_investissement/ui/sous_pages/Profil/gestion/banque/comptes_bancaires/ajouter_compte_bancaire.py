


from PySide6.QtWidgets import QComboBox, QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel, QLineEdit
from PySide6.QtCore import Signal

from services import AppContext
from session import Session

class AjouterCompteBancairePage(QWidget):
    back_to_hub = Signal()
    
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.banque_service = appContext.banque_service
        self.cb_service = appContext.cb_service
        self.session = session
        self.scenario_service = appContext.scenario_service
        layout = QVBoxLayout(self)
        
        #Formulaire
        title =QLabel("Ajouter Compte Bancaire : ")
        self.scenario_label = QLabel("")
        
        type = QLabel("Type de compte (Courant/Livret A/Epargne...)")
        self.type = QLineEdit()
        self.type.setPlaceholderText("Entrer un type de compte")
        
        banque_choix = QLabel("Chez quelle banque")
        self.banque_choix = QComboBox()
        self.banque_choix.addItem("")
        self.banque_choix.addItems(self.banque_service.get_all_banque_names())
        
        montant = QLabel("Montant sur le compte : ")
        self.montant = QLineEdit()
        self.montant.setPlaceholderText("Entrer un montant initial")
        layout.addWidget(title)
        layout.addWidget(self.scenario_label)
        layout.addWidget(type)
        layout.addWidget(self.type)
        layout.addWidget(banque_choix)
        layout.addWidget(self.banque_choix)
        layout.addWidget(montant)
        layout.addWidget(self.montant)
        
        #Boutons
        self.annuler_btn = QPushButton("Annuler x")
        self.enregistrer_btn = QPushButton("Enregister")
        
        layout.addWidget(self.enregistrer_btn)
        layout.addWidget(self.annuler_btn)

        
        #actions boutons
        self.annuler_btn.clicked.connect(self.back_to_hub.emit)
        self.enregistrer_btn.clicked.connect(self.enregistrer_clicked)
        
    def enregistrer_clicked(self):
        data = {}
        type = self.type.text().strip()
        if type:
            data["TYPE"] = type
            
        banque_choix = self.banque_choix.currentText().strip()
        
        if banque_choix:
            banque_id = self.banque_service.get_banque_by_name(banque_choix).id
        else: banque_id = self.cb_service.cb_actif.id_banque
        
        data["ID BANQUE"] = banque_id
        data["ID USER"] = self.session.current_user.id
        data["ID SCENARIO"] = self.scenario_service.scenario_actif.id
        montant = float(self.montant.text().strip())
        if montant:
            data["MONTANT"] = montant
        
        if self.cb_service.cb_actif:
            id = self.cb_service.cb_actif.id
        else: id = None
        cb = self.cb_service.update_cb(id ,data)
        self.back_to_hub.emit()

    def load(self):
        self.banque_choix.clear()
        self.banque_choix.addItem("")
        self.banque_choix.addItems(self.banque_service.get_all_banque_names())
        self.type.setText("")
        self.montant.setText("")
        self.scenario_label.setText(f"Scénario : {self.scenario_service.scenario_actif.intitule}")