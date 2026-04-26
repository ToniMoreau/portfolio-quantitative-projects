
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox, QWidget, QVBoxLayout, QHBoxLayout,  QLabel, QPushButton, QLineEdit, QStackedWidget, QSizePolicy
)
from PySide6.QtGui import QIntValidator
from services import AppContext
from services.domain_services.metierService import MetierService
from session import Session

from datetime import date

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
        self.debut_revenu_lbl = QLabel("Valable du")
        self.debut_month_input = QLineEdit()
        self.debut_month_input.setValidator(QIntValidator(0,1200))
        
        self.debut_year_input = QLineEdit()
        self.debut_year_input.setValidator(QIntValidator(0,1200))

        self.fin_revenu_lbl = QLabel("jusqu'au")
        self.fin_month_input = QLineEdit()
        self.fin_month_input.setValidator(QIntValidator(0,1200))
        
        self.fin_year_input = QLineEdit()
        self.fin_year_input.setValidator(QIntValidator(0,1200))

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
        self.etendu_lyt.addWidget(self.debut_month_input)
        self.etendu_lyt.addWidget(self.debut_year_input)
        self.etendu_lyt.addWidget(self.fin_revenu_lbl)
        self.etendu_lyt.addWidget(self.fin_month_input)
        self.etendu_lyt.addWidget(self.fin_year_input)
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
            self.fin_month_input.hide()
            self.fin_year_input.hide()
        else :
            self.debut_revenu_lbl.setText("Valable du mois n° :")
            self.fin_revenu_lbl.show()
            self.fin_month_input.show()
            self.fin_year_input.show()         
    
    def enregistrer_clicked(self):
        
        compte_choix = self.compte_bancaire_choix.currentData()
        montant = None if not(self.montant.text().strip()) else float(self.montant.text().strip())
        intitule = self.intitule.text().strip()
        freq_choix = self.frequence_choix.currentText().strip()
        
        month_in = self.debut_month_input.text().strip()
        year_in = self.debut_year_input.text().strip()
        month_out = self.fin_month_input.text().strip()
        year_out = self.fin_year_input.text().strip()
        
        date_in = None if not(month_in and year_in) else date(int(year_in), int(month_in), 1)
                
        if freq_choix == "Ponctuel":
            date_out = date_in
        else: date_out = None if not(date_in and month_out and year_out) else date(int(year_out), int(month_out), 1)
        nature = self.nature.currentText().strip()
        
        if date_in is None or date_out is None or (date_out < date_in):
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
            data["DATE IN"] = date_in
            data["DATE OUT"] = date_out
            
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
        
        self.debut_month_input.setText("")
        self.debut_year_input.setText("")
        self.fin_month_input.setText("")
        self.fin_year_input.setText("")

        self.scenario_label.setText(f'Scénario : {self.scenario_service.scenario_actif.intitule}')
