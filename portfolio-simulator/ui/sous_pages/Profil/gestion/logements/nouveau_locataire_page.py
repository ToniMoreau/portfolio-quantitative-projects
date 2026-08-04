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

class NouveauLocatairePage(QWidget):
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.scenario_service = appContext.scenario_service
        self.recette_service = appContext.recette_service
        self.invest_service = appContext.invest_service
        self.cb_service = appContext.cb_service
        self.banque_service = appContext.banque_service
        self.session = session
        self.navigator = appContext.navigator
        
        layout = QVBoxLayout(self)
        
        title_lbl = QLabel("Nouveau Locataire")
        
        mes_logements_vacants_lbl = QLabel("Selectionner un logement vacant :")
        self.mes_logements_vacants_input = QComboBox()
        self.mes_logements_vacants_input.addItem("")
        self.mes_logements_vacants_input.currentIndexChanged.connect(self.update_description_location)
        self.mes_logements_vacants_input.currentIndexChanged.connect(self.update_occupation_tab)
        
        self.occupation_tab = QListWidget()
        
        
        description_projet_lbl = QLabel("Description :")
        self.description_projet = QLabel("")

        loyer_lbl = QLabel("Montant du loyer")
        self.loyer_input = QLineEdit()
        self.loyer_input.setPlaceholderText("€")
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
        self.month_entree_input.textChanged.connect(self.update_comptes_from_date)
        self.month_entree_input.setValidator(QIntValidator(0,12))
        self.year_entree_input  = QLineEdit()
        self.year_entree_input.setPlaceholderText("AAAA")
        self.year_entree_input.textChanged.connect(self.update_comptes_from_date)
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
        
        layout.addWidget(mes_logements_vacants_lbl)
        layout.addWidget(self.mes_logements_vacants_input)
        
        layout.addWidget(description_projet_lbl)
        layout.addWidget(self.description_projet)
        
        layout.addWidget(self.occupation_tab)
        
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
        
        self.retour_btn.clicked.connect(lambda : self.navigator.go_to(Page.MES_LOCATAIRES))
        self.submit_btn.clicked.connect(self.enregistrer_clicked)
    
    def update_description_location(self):
        bien_vacant_id = self.mes_logements_vacants_input.currentData()
        bien_vacant = self.invest_service.get_by_id(bien_vacant_id)
        if bien_vacant is not None:
            self.description_projet.setText(f"{bien_vacant.localisation} | {bien_vacant.type} | {bien_vacant.surface} m² | vente : {bien_vacant.date_out or "Indéterminée"}")
            
    def update_comptes_from_date(self):
        print("updating...")
        month = self.month_entree_input.text().strip()
        year = self.year_entree_input.text().strip()
        if month and year:
            scenario = self.scenario_service.scenario_actif
            date_solde_comptes = date(int(year), int(month), 1)
            if scenario.date_in <= date_solde_comptes <= scenario.date_limite:
                cbs = self.cb_service.all_userCB_from_scenario(self.scenario_service.scenario_actif.id)
                self.quel_compte_box.clear()
                for cb in cbs:
                    banque = self.banque_service.get_banque_by_id(cb.id_banque)
                    self.quel_compte_box.addItem(f"{cb.type} | {banque.nom} | {euro(self.cb_service.solde_from_cb(self.scenario_service.scenario_actif.date_in, cb.id, date_solde_comptes).solde)}", cb.id)
                self.quel_compte_box.setDisabled(False)
        else:
            self.quel_compte_box.setDisabled(True)
  
    def update_occupation_tab(self):
        logement_id = self.mes_logements_vacants_input.currentData()
        logement = self.invest_service.get_by_id(logement_id)
        self.occupation_tab.clear()
        if logement is not None:
            self.occupation_tab.addItem(f"En activité du {logement.date_in} au {logement.date_out} ")
        self.occupation_tab.addItem("Indisponibilités du logement :")
        
        if logement_id is not None:
            locataires = self.recette_service.get_locataires_from_immo(logement_id) or []
            for locataire in locataires:
                self.occupation_tab.addItem(f"{locataire.date_in} - {locataire.date_out}")
                
    def are_dates_right(self):
        month_out = self.month_sortie_input.text().strip()
        year_out = self.year_sortie_input.text().strip()
        month_in = self.month_entree_input.text().strip()
        year_in = self.year_entree_input.text().strip()
        
        bien_vacant = self.invest_service.get_by_id(self.mes_logements_vacants_input.currentData())
        if bien_vacant is None:
            self.page_msg.setText("Aucun Logement Vacant trouvé.")
            return False
        
        if not(month_out and year_out and month_in and year_in):
            self.loyer_msg.setText("Dates incomplètes.")
            return False

        scenario = self.scenario_service.scenario_actif
        
        date_in = date(int(year_in), int(month_in), 1)
        date_out = date(int(year_out), int(month_out),1)
        date_achat = bien_vacant.date_in
        
        if scenario.date_in <= date_achat <= date_in < date_out <= scenario.date_limite:
            if bien_vacant.date_out is not None:
                if date_out > bien_vacant.date_out:
                    self.loyer_msg.setText("Dates incompatibles avec la possession du logement.") 
                    return False
                elif not(self.recette_service.is_immo_free_between_(bien_vacant.id, date_in, date_out)):
                    self.loyer_msg.setText("Le logement est occupé aux dates sélectionnés.")
                    return False
                else:
                    self.loyer_msg.clear()
                    return True
            elif not(self.recette_service.is_immo_free_between_(bien_vacant.id, date_in, date_out)):
                self.loyer_msg.setText("Le logement est occupé aux dates sélectionnés.")
                return False
            else:
                self.loyer_msg.clear()
                return True
        else:
            self.loyer_msg.setText("Les dates sont inscrites dans le mauvais ordre.")
            return False
            
    def enregistrer_clicked(self):
        
        bien_vacant_id = None if not(self.mes_logements_vacants_input.currentText().strip()) else self.mes_logements_vacants_input.currentData()
        loyer = None if not(self.loyer_input.hasAcceptableInput()) else float(self.loyer_input.text().strip())
        month_entree = None if not(self.month_entree_input.hasAcceptableInput()) else int(self.month_entree_input.text().strip())
        year_entree = None if not(self.year_entree_input.hasAcceptableInput()) else int(self.year_entree_input.text().strip())
        month_sortie = None if not(self.month_sortie_input.hasAcceptableInput()) else int(self.month_sortie_input.text().strip())
        year_sortie = None if not(self.year_sortie_input.hasAcceptableInput()) else int(self.year_sortie_input.text().strip())
        indexation_pct = None if not(self.indexation_input.hasAcceptableInput()) else float(self.indexation_input.text().strip().replace(",","."))
        quel_compte_id = None if not(self.quel_compte_box.currentText().strip()) else self.quel_compte_box.currentData()
        
        if not(self.are_dates_right()):
            pass
        elif (loyer is None
            or month_entree is None
            or year_entree is None
            or month_sortie is None
            or year_sortie is None
            or indexation_pct is None
            or bien_vacant_id is None
            ):
            
            self.page_msg.setText("Veuillez tout renseigner avant de submit.")
        else:
            bien_vacant = self.invest_service.get_by_id(bien_vacant_id)
            data = {}
            
            data["ID USER"] = self.session.current_user.id
            data["ID SCENARIO"] = self.scenario_service.scenario_actif.id
            data["ID COMPTE"] = quel_compte_id
            data["INTITULE"] = bien_vacant.titre
            data["MONTANT"] = loyer
            data["FREQUENCE"] = "Mensuel"
            data["DATE IN"] = date(year_entree, month_entree, 1)
            data["DATE OUT"] = date(year_sortie, month_sortie, 1)
            data["INDEXATION"] = indexation_pct/100
            data["NATURE"] = "Locataires"
            
            data["ID INVEST"] = bien_vacant.id
            
            loyer = self.recette_service.update_recette(None, data)
            self.navigator.go_to(Page.MES_LOCATAIRES)
            
    def load(self):
        self.update_occupation_tab()
        self.mes_logements_vacants_input.clear()
        self.mes_logements_vacants_input.addItem("")
        biens_vacants = self.invest_service.get_immo_actif_by_scenario(self.scenario_service.scenario_actif.id)
        
        for bien in biens_vacants:
            self.mes_logements_vacants_input.addItem(bien.titre, bien.id)
    
        self.quel_compte_box.clear()
        self.quel_compte_box.addItem("")
        cbs = self.cb_service.all_userCB_from_scenario(self.scenario_service.scenario_actif.id)
        scenario_date_in = self.scenario_service.scenario_actif.date_in
        
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