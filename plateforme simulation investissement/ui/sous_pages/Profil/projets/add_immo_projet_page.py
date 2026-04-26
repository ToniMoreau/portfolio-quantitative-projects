from PySide6.QtCore import Signal
from PySide6.QtGui import QIntValidator, QDoubleValidator
from PySide6.QtWidgets import (
    QListWidget, QListWidgetItem, 
    QWidget, QHBoxLayout,QVBoxLayout, 
    QLabel, QPushButton, QLineEdit, 
    QStackedWidget, QSizePolicy, 
    QComboBox
)
from utils.finance_format import euro
from datetime import date
from services import AppContext
from session import Session

class AddImmoProjetPage(QWidget):
    back_to_hub = Signal()
    
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.profil_service = appContext.profile_Service
        self.scenario_service = appContext.scenario_service
        self.invest_service = appContext.invest_service
        self.cb_service = appContext.cb_service
        self.banque_service = appContext.banque_service
        self.session = session
        layout = QVBoxLayout(self)
        
        title_lbl = QLabel("Ajouter un projet Immobilier")
        
        prix_achat_lbl = QLabel("Prix d'achat")
        self.prix_achat_input = QLineEdit()
        self.prix_achat_input.setPlaceholderText("€")
        self.prix_achat_input.setValidator(QDoubleValidator(0,1_000_000,2))
        
        comptant_lbl = QLabel("Part de l'achat en comptant (€)")
        self.comptant_input = QLineEdit()
        self.comptant_input.setValidator(QDoubleValidator(0,1_000_000, 2))

        quel_compte_lbl = QLabel("A partir de quel compte")
        self.quel_compte_box = QComboBox()
        
        date_wgt = QWidget()
        date_lyt = QHBoxLayout(date_wgt)
        date_achat_lbl = QLabel("Date d'achat du bien :")
        self.month_achat_input = QLineEdit()
        self.month_achat_input.setPlaceholderText("MM")
        self.month_achat_input.setValidator(QIntValidator(0,12))
        self.year_achat_input  = QLineEdit()
        self.year_achat_input.setPlaceholderText("AAAA")
        self.year_achat_input.setValidator(QIntValidator(2000,2500))
        
        date_lyt.addWidget(date_achat_lbl)
        date_lyt.addWidget(self.month_achat_input)
        date_lyt.addWidget(self.year_achat_input)
        
        valorisation_pct_lbl = QLabel("Valorisation annuelle (%)")
        self.valorisation_pct_input = QLineEdit()
        self.valorisation_pct_input.setValidator(QDoubleValidator(-500,500, 2))
        
        layout.addWidget(title_lbl)
        layout.addWidget(prix_achat_lbl)
        layout.addWidget(self.prix_achat_input)
        layout.addWidget(comptant_lbl)
        layout.addWidget(self.comptant_input)
        layout.addWidget(quel_compte_lbl)
        layout.addWidget(self.quel_compte_box)
        layout.addWidget(date_wgt)
        layout.addWidget(valorisation_pct_lbl)
        layout.addWidget(self.valorisation_pct_input)
        
        self.submit_btn =QPushButton("Submit ->")
        self.retour_btn = QPushButton("Retour <-")
        self.page_msg = QLabel("")
        layout.addWidget(self.submit_btn)
        layout.addWidget(self.retour_btn)
        layout.addWidget(self.page_msg)
        
        self.retour_btn.clicked.connect(self.back_to_hub.emit)
        self.submit_btn.clicked.connect(self.enregistrer_clicked)
    def enregistrer_clicked(self):
        
        prix = None if not(self.prix_achat_input.hasAcceptableInput()) else float(self.prix_achat_input.text().strip())
        comptant = None if not(self.comptant_input.hasAcceptableInput()) else float(self.comptant_input.text().strip())
        month = None if not(self.month_achat_input.hasAcceptableInput()) else int(self.month_achat_input.text().strip())
        year = None if not(self.year_achat_input.hasAcceptableInput()) else int(self.year_achat_input.text().strip())
        valorisation_pct = None if not(self.valorisation_pct_input.hasAcceptableInput()) else float(self.valorisation_pct_input.text().strip().replace(",","."))
        quel_compte_id = None if not(self.quel_compte_box.currentText().strip()) else self.quel_compte_box.currentData()
        if (prix is None
            or comptant is None
            or month is None
            or year is None
            or valorisation_pct is None):
            self.page_msg.setText("Veuillez tout renseigner avant de submit.")
        else:
            data = {}
            
            data["ID USER"] = self.session.current_user.id
            data["ID SCENARIO"] = self.scenario_service.scenario_actif.id
            data["ID COMPTE"] = quel_compte_id
            data["ID CREDIT"] = None
            data["ID ACHAT"] = None
            data["ID VENTE"] = None
            data["NATURE"] = "Immobilier"
            data["COMPTANT (%)"] = comptant/prix 
            data["PRIX ACHAT"] = prix
            data["DATE ACHAT"] = date(year, month, 1)
            data["DATE VENTE"] = None
            data["VALORISATION (%/AN)"] = valorisation_pct/100
            data["ETAT"] = False
            
            investissement = self.invest_service.update_investissement(None, data)
            
            self.back_to_hub.emit()
            
    def validator_comptant(self):
        prix_input = self.prix_achat_input
        valide = prix_input.hasAcceptableInput()
        if valide:
            prix = prix_input.text().strip()
            self.comptant_input.setValidator(QDoubleValidator(0., float(prix.replace(",",'.')), 2))
            print(f"VLDTR Projet Immo Comptant {prix}")

    def load(self):
        print("j'ai marché")
        self.quel_compte_box.clear()
        self.quel_compte_box.addItem("")
        cbs = self.cb_service.all_userCB_from_scenario(self.scenario_service.scenario_actif.id)
        scenario_date_in = self.scenario_service.scenario_actif.date_in
        for cb in cbs:
            banque = self.banque_service.get_banque_by_id(cb.id_banque)
            self.quel_compte_box.addItem(f"{cb.type} | {banque.id} | {euro(self.cb_service.solde_from_cb(scenario_date_in, cb.id, scenario_date_in).solde)}", cb.id)
        
        self.prix_achat_input.setText("")
        self.month_achat_input.setText("")
        self.year_achat_input.setText("")        
        self.valorisation_pct_input.setText("")    
        self.comptant_input.setText("")
        
        self.page_msg.setText("")
        
        print("je suis arrivé la ")