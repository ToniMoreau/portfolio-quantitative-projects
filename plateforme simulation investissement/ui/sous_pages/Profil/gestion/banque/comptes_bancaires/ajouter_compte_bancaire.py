


from PySide6.QtWidgets import QComboBox, QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel, QLineEdit
from PySide6.QtCore import Signal
from PySide6.QtGui import QIntValidator, QDoubleValidator
from services import AppContext
from session import Session

class AjouterCompteBancairePage(QWidget):
    back_to_hub = Signal()
    
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.banque_service = appContext.banque_service
        self.recette_service = appContext.recette_service
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
        
        taux_crediteur_lbl = QLabel("Taux de rendement : (%)")
        self.taux_crediteur_input = QLineEdit()
        self.taux_crediteur_input.setPlaceholderText("")
        self.taux_crediteur_input.setValidator(QDoubleValidator(0, 100, 2))
        
        banque_choix = QLabel("Chez quelle banque")
        self.banque_choix = QComboBox()
        self.banque_choix.addItem("")
        self.banque_choix.addItems(self.banque_service.get_all_banque_names())
        
        montant = QLabel("Depot initial sur le compte : ")
        self.montant = QLineEdit()
        self.montant.setPlaceholderText("Entrer un montant initial")
        layout.addWidget(title)
        layout.addWidget(self.scenario_label)
        layout.addWidget(type)
        layout.addWidget(self.type)
        layout.addWidget(taux_crediteur_lbl)
        layout.addWidget(self.taux_crediteur_input)
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
        cb = self.cb_service.cb_actif 
        print("cb_actif = ", cb)
        
        banque_choix = self.banque_choix.currentText().strip()
        banque = self.banque_service.get_banque_by_name(banque_choix)
        type = self.type.text().strip()
        taux_crediteur = self.taux_crediteur_input.text().strip()
        montant = self.montant.text().strip()
        
        if cb:
            id = cb.id
            recette = self.recette_service.get_by_(dict_bys={"ID COMPTE" : id,"NATURE" : "Dépots"})
            id_recette = None if recette is None else recette.pop().id
            id_banque = cb.id_banque if not(banque) else int(banque.id)
            type = cb.type if not(type) else str(type)
            montant = cb.solde_initial if not(montant) else float(montant)
            taux_crediteur = cb.taux_annuel if not(taux_crediteur) else float(taux_crediteur.replace(",","."))/100
        else:
            id = None
            id_recette = None
            id_banque = None if not(banque) else int(banque.id)
            type = None if not(type)  else str(type)
            montant = None if not(montant) else float(montant)
            taux_crediteur = None if not(taux_crediteur) else float(taux_crediteur.replace(",","."))/100
            
        if (id_banque is None
            or type is None
            or montant is None):
            pass
        else:
            data = {}
            
            data["ID BANQUE"] = id_banque
            data["ID USER"] = self.session.current_user.id
            data["ID SCENARIO"] = self.scenario_service.scenario_actif.id
            data["SOLDE INITIAL"] = montant            
            data["TYPE"] = type
            data["RENDEMENT (%/AN)"] = taux_crediteur
            
            cb = self.cb_service.update_cb(id ,data)

            data_recette = {}
            data_recette["ID COMPTE"] = cb.id
            data_recette["ID USER"] = self.session.current_user.id
            data_recette["ID SCENARIO"] = self.scenario_service.scenario_actif.id
            data_recette["MONTANT"] = montant
            data_recette["DATE IN"] = data_recette["DATE OUT"] = self.scenario_service.scenario_actif.date_in            
            data_recette["INTITULE"] = "Ouverture compte"
            data_recette["NATURE"] = "Dépots"
            data_recette["FREQUENCE"] = "Ponctuel"
            
            recette = self.recette_service.update_recette(id_recette, data_recette)
            self.back_to_hub.emit()

    def load(self):
        self.banque_choix.clear()
        self.banque_choix.addItem("")
        self.banque_choix.addItems(self.banque_service.get_all_banque_names())
        self.type.setText("")
        self.taux_crediteur_input.setText("")
        self.montant.setText("")
        self.scenario_label.setText(f"Scénario : {self.scenario_service.scenario_actif.intitule}")