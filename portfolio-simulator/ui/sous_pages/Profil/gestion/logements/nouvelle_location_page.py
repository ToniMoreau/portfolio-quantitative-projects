#flattened

from PySide6.QtCore import Signal
from PySide6.QtGui import QIntValidator, QDoubleValidator
from PySide6.QtWidgets import (
    QPlainTextEdit,
    QListWidget, QListWidgetItem, 
    QWidget, QHBoxLayout,QVBoxLayout, 
    QLabel, QPushButton, QLineEdit, 
    QStackedWidget, QSizePolicy, 
    QComboBox
)
from utils.finance_format import euro
from datetime import date
from services import AppContext, Page
from session import Session

class NouvelleLocationPage(QWidget):
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.metier_service = appContext.metier_service
        self.scenario_service = appContext.scenario_service
        self.depense_service = appContext.depense_service
        self.cb_service = appContext.cb_service
        self.banque_service = appContext.banque_service
        self.session = session
        self.navigator = appContext.navigator
        
        layout = QVBoxLayout(self)
        
        title_lbl = QLabel("Nouvelle Location")
        
        description_projet_lbl = QLabel("Description :")
        self.description_projet = QPlainTextEdit()
        self.description_projet.setPlaceholderText("Description nouvelle location")
        self.description_projet.setFixedHeight(100)
        
        loyer_lbl = QLabel("Montant du loyer")
        self.loyer_input = QLineEdit()
        self.loyer_input.setPlaceholderText("€")
        self.loyer_input.textChanged.connect(self.is_loyer_good)
        self.loyer_input.setValidator(QDoubleValidator(0,100_000,2))
        self.loyer_msg = QLabel("")
        self.limite_loyer = 0
        
        #-----------DATE SECTION--------------#
        date_wgt = QWidget()
        date_lyt = QVBoxLayout(date_wgt)
        entree_wgt = QWidget()
        entree_lyt = QHBoxLayout(entree_wgt)
        sortie_wgt = QWidget()
        sortie_lyt = QHBoxLayout(sortie_wgt)
        
        date_entree_lbl = QLabel("Date d'entrée en logement")
        self.month_entree_input = QLineEdit()
        self.month_entree_input.setPlaceholderText("MM")
        self.month_entree_input.textChanged.connect(self.is_loyer_good)
        self.month_entree_input.textChanged.connect(self.update_comptes_from_date)
        self.month_entree_input.textChanged.connect(self.update_capa_loyer_from_date)
        self.month_entree_input.setValidator(QIntValidator(0,12))
        self.year_entree_input  = QLineEdit()
        self.year_entree_input.setPlaceholderText("AAAA")
        self.year_entree_input.textChanged.connect(self.is_loyer_good)
        self.year_entree_input.textChanged.connect(self.update_comptes_from_date)
        self.year_entree_input.textChanged.connect(self.update_capa_loyer_from_date)
        self.year_entree_input.setValidator(QIntValidator(2000,2500))
        
        entree_lyt.addWidget(date_entree_lbl)
        entree_lyt.addWidget(self.month_entree_input)
        entree_lyt.addWidget(self.year_entree_input)
        
        date_sortie_lbl = QLabel("Date de sortie du logement")
        self.month_sortie_input = QLineEdit()
        self.month_sortie_input.setPlaceholderText("MM")
        self.month_sortie_input.setValidator(QIntValidator(0,12))
        self.year_sortie_input  = QLineEdit()
        self.year_sortie_input.setPlaceholderText("AAAA")
        self.year_sortie_input.setValidator(QIntValidator(2000,2500))
        
        sortie_lyt.addWidget(date_sortie_lbl)
        sortie_lyt.addWidget(self.month_sortie_input)
        sortie_lyt.addWidget(self.year_sortie_input)
        
        date_lyt.addWidget(entree_wgt)
        date_lyt.addWidget(sortie_wgt)
        #--------------------------------------------------------------#
        quel_compte_lbl = QLabel("A partir de quel compte")
        self.quel_compte_box = QComboBox()

        #--------------Valorisation section----------------------------#
        indexation_lbl = QLabel("indexation annuelle (%)")
        self.indexation_input = QLineEdit()
        self.indexation_input.setValidator(QDoubleValidator(-500,500, 2))
        #--------------------------------------------------------------#
        
        layout.addWidget(title_lbl)
        layout.addWidget(description_projet_lbl)
        layout.addWidget(self.description_projet)
        
        layout.addWidget(date_wgt)
        
        layout.addWidget(quel_compte_lbl)
        layout.addWidget(self.quel_compte_box)
        
        layout.addWidget(loyer_lbl)
        layout.addWidget(self.loyer_input)
        layout.addWidget(self.loyer_msg)
        
        layout.addWidget(indexation_lbl)
        layout.addWidget(self.indexation_input)
        
        self.submit_btn =QPushButton("Submit ->")
        self.retour_btn = QPushButton("Retour <-")
        self.page_msg = QLabel("")
        layout.addWidget(self.submit_btn)
        layout.addWidget(self.retour_btn)
        layout.addWidget(self.page_msg)
        
        self.retour_btn.clicked.connect(lambda : self.navigator.go_to(Page.MON_DOMICILE))
        self.submit_btn.clicked.connect(self.enregistrer_clicked)
    
    def update_comptes_from_date(self):
        print("updating...")
        month = self.month_entree_input.text().strip()
        year = self.year_entree_input.text().strip()
        if month and year:
            scenario = self.scenario_service.get_scenario_by_id(self.scenario_service.scenario_actif_id)   
            date_solde_comptes = date(int(year), int(month), 1)
            if scenario.date_in <= date_solde_comptes <= scenario.date_limite:
                cbs = self.cb_service.all_userCB_from_scenario(self.scenario_service.scenario_actif_id)
                self.quel_compte_box.clear()
                for cb in cbs:
                    banque = self.banque_service.get_banque_by_id(cb.id_banque)
                    self.quel_compte_box.addItem(f"{cb.type} | {banque.nom} | {euro(self.cb_service.solde_from_cb(scenario.date_in, cb.id, date_solde_comptes).solde)}", cb.id)
                
    def update_capa_loyer_from_date(self):
        depense = self.depense_service.get_depense_by_id(self.depense_service.depense_active_id)
        if depense is not None:
            month = self.month_entree_input.text().strip()
            month = month if month else depense.date_in.month
            year = self.year_entree_input.text().strip()
            year = year if year else depense.date_in.year
        else:
            month = self.month_entree_input.text().strip() 
            year = self.year_entree_input.text().strip()
            
        if month and year:
            scenario = self.scenario_service.get_scenario_by_id(self.scenario_service.scenario_actif_id)   
            date_verif = date(int(year), int(month), 1)
            if scenario.date_in <= date_verif <= scenario.date_limite:
                salaire_moyen = self.metier_service.get_salaires_moyens_x_mois(scenario.id, 3, date_verif)
                self.limite_loyer = salaire_moyen*0.33
                self.loyer_msg.setText(f"Capacité de location : {euro(self.limite_loyer)} /mois")
                self.loyer_input.setValidator(QDoubleValidator(0,self.limite_loyer, 2))
        else:
            self.limite_loyer = 0
            self.loyer_msg.setText(f"Capacité de location : {euro(self.limite_loyer)} /mois")
            self.loyer_input.setValidator(QDoubleValidator(0,self.limite_loyer, 2))
    
    def are_dates_good(self):
        depense = self.depense_service.get_depense_by_id(self.depense_service.depense_active_id)
        if depense is not None:
            month = self.month_entree_input.text().strip()
            month = month if month else depense.date_in.month
            year = self.year_entree_input.text().strip()
            year = year if year else depense.date_in.year
        else:
            month = self.month_entree_input.text().strip() 
            year = self.year_entree_input.text().strip()
        if month and year:
            scenario = self.scenario_service.get_scenario_by_id(self.scenario_service.scenario_actif_id)   
            date_verif = date(int(year), int(month), 1)
            if scenario.date_in <= date_verif <= scenario.date_limite:
                return True
        return False
    
    def is_loyer_good(self):
        depense = self.depense_service.get_depense_by_id(self.depense_service.depense_active_id)
        if depense is not None:
            loyer = self.loyer_input.text().strip()
            loyer = loyer if loyer else depense.montant
        else:
            loyer = self.loyer_input.text().strip()
        if loyer != "":
            loyer = float(loyer)
            if loyer > self.limite_loyer:
                self.loyer_msg.setText(f"Le loyer dépasse la capacité maximale ({euro(self.limite_loyer)})")
                return False
            else:
                self.loyer_msg.setText(f"Capacité de location : {euro(self.limite_loyer)} /mois")
                return True
            
    def enregistrer_clicked(self):
        depense_active = self.depense_service.get_depense_by_id(self.depense_service.depense_active_id)
        print(depense_active)
        
        depense_id = None
        loyer = None if not(self.loyer_input.hasAcceptableInput()) else float(self.loyer_input.text().strip())
        month_entree = None if not(self.month_entree_input.hasAcceptableInput()) else int(self.month_entree_input.text().strip())
        year_entree = None if not(self.year_entree_input.hasAcceptableInput()) else int(self.year_entree_input.text().strip())
        month_sortie = None if not(self.month_sortie_input.hasAcceptableInput()) else int(self.month_sortie_input.text().strip())
        year_sortie = None if not(self.year_sortie_input.hasAcceptableInput()) else int(self.year_sortie_input.text().strip())
        indexation_pct = None if not(self.indexation_input.hasAcceptableInput()) else float(self.indexation_input.text().strip().replace(",","."))
        quel_compte_id = None if not(self.quel_compte_box.currentText().strip()) else self.quel_compte_box.currentData()
        description = None if not(self.description_projet.toPlainText().strip()) else self.description_projet.toPlainText().strip()
        
        if depense_active is not None:
            depense_id = depense_active.id 
            loyer = loyer or depense_active.montant  
            month_entree =month_entree or depense_active.date_in.month  
            year_entree =  year_entree or depense_active.date_in.year 
            print("year entree")
            month_sortie = month_sortie or depense_active.date_out.month 
            year_sortie =  year_sortie or depense_active.date_out.year 
            indexation_pct = indexation_pct or depense_active.indexation*100 
            quel_compte_id = quel_compte_id or depense_active.id_compte 
            description =  description or depense_active.intitule

        if (loyer is None
            or month_entree is None
            or year_entree is None
            or month_sortie is None
            or year_sortie is None
            or indexation_pct is None
            or description is None
            ):
            self.page_msg.setText("Veuillez tout renseigner avant de submit.")
        elif not(self.is_loyer_good()):
            self.page_msg.setText("Le loyer n'entre pas dans les limites fixées.")
        elif not(self.are_dates_good()):
            self.page_msg.setText("Les dates ne correspondent pas.")
        else:
            data = {}
            
            data["ID USER"] = self.session.current_user.id
            data["ID SCENARIO"] = self.scenario_service.scenario_actif_id
            data["ID COMPTE"] = quel_compte_id
            data["INTITULE"] = description
            data["MONTANT"] = loyer
            data["FREQUENCE"] = "Mensuel"
            data["DATE IN"] = date(year_entree, month_entree, 1)
            data["DATE OUT"] = date(year_sortie, month_sortie, 1)
            data["INDEXATION"] = indexation_pct/100
            data["NATURE"] = "Loyers"
            
            loyer = self.depense_service.update_depense(depense_id, data)
            self.depense_service.set_depense_active(None)
            self.navigator.go_to(Page.MON_DOMICILE)
            
    def load(self):
        scenario = self.scenario_service.get_scenario_by_id(self.scenario_service.scenario_actif_id)   
        if scenario:
            self.update_capa_loyer_from_date()
            self.quel_compte_box.clear()
            self.quel_compte_box.addItem("")
            cbs = self.cb_service.all_userCB_from_scenario(scenario.id)
            scenario_date_in = scenario.date_in
            for cb in cbs:
                banque = self.banque_service.get_banque_by_id(cb.id_banque)
                self.quel_compte_box.addItem(f"{cb.type} | {banque.id} | {euro(self.cb_service.solde_from_cb(scenario_date_in, cb.id, scenario_date_in).solde)}", cb.id)
            
            self.loyer_input.setText("")
            self.month_entree_input.setText("")
            self.year_entree_input.setText("")        
            self.month_sortie_input.setText("")
            self.year_sortie_input.setText("")
            
            self.indexation_input.setText("")    
            
            self.page_msg.setText("")
        else: 
            self.navigator.go_to(Page.NO_SCENARIO)
        self.navigator.hold_page(Page.NOUVELLE_LOCATION)
        