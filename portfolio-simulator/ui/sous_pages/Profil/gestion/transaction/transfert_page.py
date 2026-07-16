from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox, QWidget, QVBoxLayout, QHBoxLayout,  QLabel, QPushButton, QLineEdit, QStackedWidget, QSizePolicy
)
from PySide6.QtGui import QIntValidator, QDoubleValidator
from services import AppContext
from services.domain_services.metierService import MetierService
from session import Session
from utils.finance_format import euro

from datetime import date

class TransfertPage(QWidget):
    back_to_hub = Signal()
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.scenario_service = appContext.scenario_service
        self.cb_service = appContext.cb_service
        self.depense_service = appContext.depense_service
        self.recette_service = appContext.recette_service
        
        self.banque_service = appContext.banque_service
        self.session = session

        layout = QVBoxLayout(self)

        self.scenario_label = QLabel("Scénario : ")
        title = QLabel("Ajouter un transfert interne :")

        emmeteur_lbl = QLabel("De quel compte : ")
        self.emmeteur_input = QComboBox()

        destinataire_lbl = QLabel("Vers quel compte :")
        self.destinataire_input = QComboBox()

        montant_lbl = QLabel("Montant du transfert :")
        self.montant_input = QLineEdit()
        validation = QDoubleValidator(0.0, 1000000000.0, 2)
        self.montant_input.setValidator(validation)

        frequence_lbl = QLabel("Fréquence du transfert :")
        self.frequence_input = QComboBox()
        self.frequence_input.addItems(["","Ponctuel","Mensuel", "Annuel"])
        
        intitule_lbl = QLabel("Intitule du transfert :")
        self.intitule_input = QLineEdit()

        nature_lbl = QLabel("Nature du transfert :")
        self.nature_input = QComboBox()
        self.nature_input.addItems(self.depense_service.natures)
        
        date_wgt = QWidget()
        date_lyt = QHBoxLayout(date_wgt)
        debut_lbl = QLabel("Date de début du transfert :")
        self.month_debut_input = QLineEdit()
        self.month_debut_input.setValidator(QIntValidator(0,12))
        self.year_debut_input = QLineEdit()
        self.year_debut_input.setValidator(QIntValidator(1980,2200))
        
        fin_lbl = QLabel("Date de fin du transfert :")
        self.month_fin_input = QLineEdit()
        self.month_fin_input.setValidator(QIntValidator(0,12))
        self.year_fin_input = QLineEdit()
        self.year_fin_input.setValidator(QIntValidator(1980,2200))
        
        date_lyt.addWidget(debut_lbl)
        date_lyt.addWidget(self.month_debut_input)
        date_lyt.addWidget(self.year_debut_input)
        date_lyt.addWidget(fin_lbl)
        date_lyt.addWidget(self.month_fin_input)
        date_lyt.addWidget(self.year_fin_input)
        
        layout.addWidget(self.scenario_label)
        layout.addWidget(title)
        layout.addWidget(emmeteur_lbl)
        layout.addWidget(self.emmeteur_input)
        layout.addWidget(destinataire_lbl)
        layout.addWidget(self.destinataire_input)
        layout.addWidget(montant_lbl)
        layout.addWidget(self.montant_input)
        layout.addWidget(frequence_lbl)
        layout.addWidget(self.frequence_input)
        layout.addWidget(nature_lbl)
        layout.addWidget(self.nature_input)
        layout.addWidget(intitule_lbl)
        layout.addWidget(self.intitule_input)
        layout.addWidget(date_wgt)

        self.enregistrer_btn = QPushButton("Enregistrer")
        self.retour_btn = QPushButton("Retour <-")
        layout.addWidget(self.enregistrer_btn)
        layout.addWidget(self.retour_btn)

        self.retour_btn.clicked.connect(self.back_to_hub.emit)
        self.enregistrer_btn.clicked.connect(self.enregistrer_clicked)

    def enregistrer_clicked(self):
        id_credite = self.destinataire_input.currentData()
        id_debite = self.emmeteur_input.currentData()
        
        montant = self.montant_input.text().strip()
        montant = None if not(montant) else float(montant)
        
        frequence = self.frequence_input.currentText().strip()
        frequence = None if not(frequence) else frequence
        
        intitule = self.intitule_input.text().strip()
        intitule = None if not(intitule) else intitule
        
        nature = self.nature_input.currentText().strip()
        nature = None if not(nature) else nature
        
        
        month_in = self.month_debut_input.text().strip()
        year_in = self.year_debut_input.text().strip()
        month_out = self.month_fin_input.text().strip()
        year_out = self.year_fin_input.text().strip()
        
        date_in = None if not(month_in and year_in) else date(int(year_in), int(month_in), 1)
        date_out = None if not(date_in and month_out and year_out) else date(int(year_out), int(month_out), 1)
        
        if (id_credite is None
            or id_debite is None
            or montant is None
            or frequence is None
            or intitule is None
            or nature is None
            or date_in is None
            or date_out is None):
            raise ValueError("Vous devez tout renseigner.")
        elif date_out < date_in:
            raise ValueError("Dates invalides (debut < fin)")
        else:
            data = {}
            data["ID COMPTE"] = id_credite
            data["ID SCENARIO"] = self.scenario_service.scenario_actif.id
            data["ID USER"] = self.session.current_user.id
            data["MONTANT"] = montant
            data["FREQUENCE"] = frequence
            data["NATURE"] = nature
            data["INTITULE"] = intitule
            data["DATE IN"] = date_in
            data["DATE OUT"] = date_out
            
            credit = self.recette_service.update_recette(None, data, is_transaction=True) 
            data["ID COMPTE"] = id_debite
            data["ID TRANSACTION"] = credit.id_transaction
            debit = self.depense_service.update_depense(None, data)

            self.back_to_hub.emit()
    
    def load(self):
        scenario = self.scenario_service.scenario_actif
        self.scenario_label.setText(f"Scénario : {scenario.intitule}")
        
        self.emmeteur_input.clear()
        self.destinataire_input.clear()
        self.emmeteur_input.addItem("")
        self.destinataire_input.addItem("")
        cbs = self.cb_service.all_userCB_from_scenario(scenario.id)
        for cb in cbs:
            banque = self.banque_service.get_banque_by_id(cb.id_banque)
            montant = self.cb_service.solde_from_cb(scenario.date_in,cb.id, scenario.date_in)
            self.emmeteur_input.addItem(f"[{banque.nom}] {cb.type} : {euro(montant)}", cb.id)
            self.destinataire_input.addItem(f"[{banque.nom}] {cb.type} : {euro(montant)}", cb.id)

        self.montant_input.clear()
        self.frequence_input.setCurrentIndex(0)
        self.nature_input.setCurrentIndex(0)
        self.intitule_input.clear()
        self.month_debut_input.clear()
        self.month_fin_input.clear()
        self.year_debut_input.clear()
        self.year_fin_input.clear()