
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox, QWidget, QVBoxLayout, QHBoxLayout,  QLabel, QPushButton, QLineEdit, QStackedWidget, QSizePolicy
)
from PySide6.QtGui import QIntValidator
from services import AppContext
from services.domain_services.metierService import MetierService
from session import Session


class AjouterRevenuPage(QWidget):
    back_to_hub = Signal()
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.banque_service = appContext.banque_service
        self.cb_service = appContext.cb_service
        self.session = session
        self.scenario_service = appContext.scenario_service
        self.recette_service = appContext.recette_service
        
        layout = QVBoxLayout(self)
        
        #Formulaire
        title =QLabel("Ajouter Revenu : ")
        self.scenario_label = QLabel(f"")
        
        cb_choix_label = QLabel("Choisissez un compte bancaire ")
        self.compte_bancaire_choix = QComboBox()
        
        montant = QLabel("Montant du revenu : ")
        self.montant = QLineEdit()
        self.montant.setPlaceholderText("Entrer un montant initial")
        intitule = QLabel("Libélé : ")
        self.intitule = QLineEdit()
        self.intitule.setPlaceholderText("Entrer un libélé")
        frequence = QLabel("Indiquer la fréquence du revenu")
        self.frequence_choix = QComboBox()
        self.frequence_choix.addItems(["","Ponctuel", "Mensuel", "Annuel"])
        self.frequence_choix.currentIndexChanged.connect(self.update_periode_from_freq)
        
        self.etendu_wgt = QWidget()
        self.etendu_lyt = QHBoxLayout(self.etendu_wgt)
        self.debut_revenu_lbl = QLabel("Valable du mois n°")
        self.debut_revenu_input = QLineEdit()
        self.debut_revenu_input.setValidator(QIntValidator(0,1200))
        self.debut_revenu_input.textChanged.connect(self.fin_periode_intvalidator_updt)
        
        self.fin_revenu_lbl = QLabel("jusqu'au mois n°")
        self.fin_revenu_input = QLineEdit()
        self.fin_revenu_input.setValidator(QIntValidator(0,1200))

        nature = QLabel("Nature du revenu :")
        self.nature = QComboBox()
        self.nature.addItems(["Revenus locatifs", "Revenus", "Autres"])
        
        layout.addWidget(title)
        layout.addWidget(self.scenario_label)
        
        layout.addWidget(cb_choix_label)
        layout.addWidget(self.compte_bancaire_choix)
        
        layout.addWidget(intitule)
        layout.addWidget(self.intitule)
        
        layout.addWidget(montant)
        layout.addWidget(self.montant)
        
        layout.addWidget(frequence)
        layout.addWidget(self.frequence_choix)
        
        self.etendu_lyt.addWidget(self.debut_revenu_lbl)
        self.etendu_lyt.addWidget(self.debut_revenu_input)
        self.etendu_lyt.addWidget(self.fin_revenu_lbl)
        self.etendu_lyt.addWidget(self.fin_revenu_input)
        layout.addWidget(self.etendu_wgt)

        layout.addWidget(nature)
        layout.addWidget(self.nature)
        
        #Boutons
        self.annuler_btn = QPushButton("Annuler x")
        self.enregistrer_btn = QPushButton("Enregister")
        self.enregistrer_msg = QLabel()

        layout.addWidget(self.enregistrer_btn)
        layout.addWidget(self.enregistrer_msg)
        layout.addWidget(self.annuler_btn)

        
        #actions boutons
        self.annuler_btn.clicked.connect(self.back_to_hub.emit)
        self.enregistrer_btn.clicked.connect(self.enregistrer_clicked)
        
    def update_periode_from_freq(self):
        if self.frequence_choix.currentText().strip() == "Ponctuel":
            self.debut_revenu_lbl.setText("Pour le mois n° :")
            self.fin_revenu_lbl.hide()
            self.fin_revenu_input.hide()
        else :
            self.debut_revenu_lbl.setText("Valable du mois n° :")
            self.fin_revenu_lbl.show()
            self.fin_revenu_input.show()
            
    def fin_periode_intvalidator_updt(self, debut):
        debut = debut.strip()
        if debut:
            debut = int(debut)
        else: 
            debut = 0
        self.fin_revenu_input.setValidator(QIntValidator(debut, 1200))   
         
    
    def enregistrer_clicked(self):
        
        compte_choix = self.compte_bancaire_choix.currentData()
        montant = None if not(self.montant.text().strip()) else float(self.montant.text().strip())
        intitule = self.intitule.text().strip()
        freq_choix = self.frequence_choix.currentText().strip()
        debut = None if not(self.debut_revenu_input.hasAcceptableInput()) else int(self.debut_revenu_input.text().strip())
        if freq_choix == "Ponctuel":
            fin = debut
        else : fin = None if not(self.fin_revenu_input.hasAcceptableInput()) else int(self.fin_revenu_input.text().strip())
        nature = self.nature.currentText().strip()
        
        if debut is None or fin is None:
            self.enregistrer_msg.setText("Assurez vous que les périodes de début et fin soient valides (0< début < fin < 1200)")
        elif (compte_choix is None 
            or montant is None 
            or intitule is None 
            or freq_choix is None 
            or nature is None):
            
            self.enregistrer_msg.setText("Vous devez tout renseigner.")
        else :
            data = {}
            data["ID COMPTE"] = compte_choix
            data["ID USER"] = self.session.current_user.id
            data["ID SCENARIO"] = self.scenario_service.scenario_actif.id
            data["INTITULE"] = intitule
            data["FREQUENCE"] = freq_choix
            data["MONTANT"] = montant
            data["NATURE"] = nature
            data["DATE IN"] = debut
            data["DATE OUT"] = fin
            
            revenu = self.recette_service.update_recette(None ,data)
            self.back_to_hub.emit()

    def load(self):
        self.compte_bancaire_choix.clear()
        for cb in self.cb_service.all_userCB_from_scenario(self.scenario_service.scenario_actif.id):
            banque = self.banque_service.get_banque_by_id(cb.id_banque)
            self.compte_bancaire_choix.addItem(f"{cb.type, banque.nom}", cb.id)
            
        self.montant.setText("")
        self.intitule.setText("")
        self.frequence_choix.setCurrentIndex(0)
        
        self.scenario_label.setText(f'Scénario : {self.scenario_service.scenario_actif.intitule}')
