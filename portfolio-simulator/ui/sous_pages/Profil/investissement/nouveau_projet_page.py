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
from domain.enums import investType

from domain.errors import (
    SoldeInsuffisantError, 
    ScenarioNotFoundError, 
    NegativeAmountError, 
    QuantFolioError,
)
class NouveauProjetPage(QWidget):
    back_to_hub = Signal()
    
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.scenario_service = appContext.scenario_service
        self.invest_service = appContext.invest_service
        self.cb_service = appContext.cb_service
        self.banque_service = appContext.banque_service
        self.session = session
        self.navigator = appContext.navigator
        
        layout = QVBoxLayout(self)
        
        title_lbl = QLabel("Ajouter un projet")
        
        #---GESTION DU TYPE D'INVESTISSEMENT---------------------#
        self.type_wgt = QWidget()
        type_lyt = QHBoxLayout(self.type_wgt)
        
        type_lbl = QLabel("Type d'investissement : ")
        self.type_box = QComboBox()
        self.type_box.addItems([t.value for t in investType])
        self.type_box.currentTextChanged.connect(self.update_type_invest)
        
        type_lyt.addWidget(type_lbl)
        type_lyt.addWidget(self.type_box)
        
        #---COMMON WGT
        self.common_wgt = QWidget()
        common_lyt = QVBoxLayout(self.common_wgt)
        self.common_wgt.hide()
        
        #----IMMO WGT--------------------------------------#
        self.immo_wgt = QWidget()
        immo_lyt = QVBoxLayout(self.immo_wgt)
        self.immo_wgt.hide()
        #---STOCK WGT--------------------------------------#
        self.stock_wgt = QWidget()
        stock_lyt = QVBoxLayout(self.stock_wgt)
        self.stock_wgt.hide()
        #--------------------------------------------------#
        
        #---titre -----------------------------------------#
        self.titre_wgt = QWidget()
        titre_lyt = QHBoxLayout(self.titre_wgt)
        
        titre_projet_lbl = QLabel("titre :")
        self.titre_projet = QPlainTextEdit()
        self.titre_projet.setPlaceholderText("titre du projet...")
        self.titre_projet.setFixedHeight(100)
        
        titre_lyt.addWidget(titre_projet_lbl)
        titre_lyt.addWidget(self.titre_projet)
        #--------------------------------------------------------#
        
        #---PRIX D'ACHAT-----------------------------------------#
        self.prix_achat_wgt = QWidget()
        prix_achat_lyt = QHBoxLayout(self.prix_achat_wgt)
        
        prix_achat_lbl = QLabel("Montant")
        self.prix_achat_input = QLineEdit()
        self.prix_achat_input.setPlaceholderText("€")
        self.prix_achat_input.setValidator(QDoubleValidator(0,1_000_000_000,2))
        
        prix_achat_lyt.addWidget(prix_achat_lbl)
        prix_achat_lyt.addWidget(self.prix_achat_input)
        #--------------------------------------------------------#
        
        #----COMPTANT SECTION : HIDE/SHOW selon Stock/IMMO----#
        self.comptant_widget = QWidget()
        comptant_layout = QHBoxLayout(self.comptant_widget)
        comptant_lbl = QLabel("Part de l'achat en comptant (€)")
        self.comptant_input = QLineEdit()
        self.comptant_input.setValidator(QDoubleValidator(0,1_000_000, 2))
        
        comptant_layout.addWidget(comptant_lbl)
        comptant_layout.addWidget(self.comptant_input)
        #--------------------------------------------------------#
        
        #---QUEL COMPTE------------------------------------------#
        self.quel_compte_wgt = QWidget()
        quel_compte_lyt = QHBoxLayout(self.quel_compte_wgt)
        quel_compte_lbl = QLabel("A partir de quel compte")
        self.quel_compte_box = QComboBox()
        
        quel_compte_lyt.addWidget(quel_compte_lbl)
        quel_compte_lyt.addWidget(self.quel_compte_box)
        #--------------------------------------------------------#
        
        #---DATE IN----------------------------------------------#
        date_wgt = QWidget()
        date_lyt = QHBoxLayout(date_wgt)
        date_achat_lbl = QLabel("Date d'achat du bien :")
        self.month_achat_input = QLineEdit()
        self.month_achat_input.setPlaceholderText("MM")
        self.month_achat_input.textChanged.connect(self.update_comptes_from_date)
        self.month_achat_input.setValidator(QIntValidator(0,12))
        self.year_achat_input  = QLineEdit()
        self.year_achat_input.setPlaceholderText("AAAA")
        self.year_achat_input.textChanged.connect(self.update_comptes_from_date)
        self.year_achat_input.setValidator(QIntValidator(2000,2500))
        
        date_lyt.addWidget(date_achat_lbl)
        date_lyt.addWidget(self.month_achat_input)
        date_lyt.addWidget(self.year_achat_input)
        #--------------------------------------------------------#
        
        #---VALO ANNUELLE----------------------------------------#
        self.valo_wgt = QWidget()
        valo_lyt = QHBoxLayout(self.valo_wgt)
        valorisation_pct_lbl = QLabel("Valorisation annuelle (%)")
        self.valorisation_pct_input = QLineEdit()
        self.valorisation_pct_input.setValidator(QDoubleValidator(-500,500, 2))
        
        valo_lyt.addWidget(valorisation_pct_lbl)
        valo_lyt.addWidget(self.valorisation_pct_input)
        #--------------------------------------------------------#
        
        #---IMMO DETAILS-----------------------------------------#
        self.immo_details_wgt = QWidget()
        immo_details_lyt = QHBoxLayout(self.immo_details_wgt)
        
        ville_lbl = QLabel("Ville")
        self.ville_input= QLineEdit()
        self.ville_input.setPlaceholderText("ville")
        
        surface_lbl = QLabel("Surface du bien")
        self.surface_input = QLineEdit()
        self.surface_input.setPlaceholderText("m²")
        
        type_bien_lbl = QLabel("Type du Bien")
        self.type_bien_input = QComboBox()
        self.type_bien_input.addItems([
            "",
            "Studio",
            "T1 BIS",
            "T2",
            "T3",
            "T4",
            "T5",
            "T6"
        ])
        
        immo_details_lyt.addWidget(ville_lbl)
        immo_details_lyt.addWidget(self.ville_input)
        immo_details_lyt.addWidget(surface_lbl)
        immo_details_lyt.addWidget(self.surface_input)
        immo_details_lyt.addWidget(type_bien_lbl)
        immo_details_lyt.addWidget(self.type_bien_input)
        #--------------------------------------------------------#
        #---DIVIDENDES-------------------------------------------#
        self.dividendes_wgt = QWidget()
        dividendes_lyt = QHBoxLayout(self.dividendes_wgt)
        dividendes_lbl = QLabel("Dividendes")
        self.dividendes_pct_input = QLineEdit()
        self.dividendes_pct_input.setPlaceholderText("%")
        self.dividendes_pct_input.setValidator(QDoubleValidator(0.,100.,2))
        
        dividendes_lyt.addWidget(dividendes_lbl)
        dividendes_lyt.addWidget(self.dividendes_pct_input)
        
        #---LAYER INFOS (HIDEABLE)-------------------------------#
        common_lyt.addWidget(self.titre_wgt)
        common_lyt.addWidget(self.prix_achat_wgt)
        common_lyt.addWidget(date_wgt)
        common_lyt.addWidget(self.quel_compte_wgt)
        immo_lyt.addWidget(self.comptant_widget)
        common_lyt.addWidget(self.valo_wgt)
        stock_lyt.addWidget(self.dividendes_wgt)
        immo_lyt.addWidget(self.immo_details_wgt)
                
        #---MAINE LAYERING---------------------------------------#
        layout.addWidget(title_lbl)
        layout.addWidget(self.type_wgt)
        
        layout.addWidget(self.stock_wgt)
        layout.addWidget(self.immo_wgt)
        layout.addWidget(self.common_wgt)
        #--------------------------------------------------------#
        
        #---BTNS-------------------------------------------------#
        self.submit_btn =QPushButton("Submit ->")
        self.retour_btn = QPushButton("Retour <-")
        self.page_msg = QLabel("")
        common_lyt.addWidget(self.submit_btn)
        layout.addWidget(self.retour_btn)
        
        self.retour_btn.clicked.connect(lambda : self.navigator.go_to(Page.INVESTISSEMENT_HUB))
        self.submit_btn.clicked.connect(self.enregistrer_clicked)
        #--------------------------------------------------------#
        layout.addWidget(self.page_msg)
    
    def update_type_invest(self):
        curr_text =self.type_box.currentText().strip() 
        if curr_text == investType.IMMO:
            self.immo_mode()
        elif curr_text == investType.STOCK:
            self.stock_mode()
        else:
            self.default_mode()
            
    def default_mode(self):
        self.immo_wgt.hide()
        self.stock_wgt.hide()
    def immo_mode(self):
        self.stock_wgt.hide()
        self.immo_wgt.show()
        self.common_wgt.show()
        
    def stock_mode(self):
        self.immo_wgt.hide()
        self.stock_wgt.show()
        self.common_wgt.show()
    
    
    def update_comptes_from_date(self):
        print("updating...")
        scenario = self.scenario_service.get_scenario_by_id(self.scenario_service.scenario_actif_id)   
        month = self.month_achat_input.text().strip()
        year = self.year_achat_input.text().strip()
        if month and year:
            date_solde_comptes = date(int(year), int(month), 1)
            if scenario.date_in <= date_solde_comptes <= scenario.date_limite:
                cbs = self.cb_service.all_userCB_from_scenario(self.scenario_service.scenario_actif_id)
                self.quel_compte_box.clear()
                for cb in cbs:
                    banque = self.banque_service.get_banque_by_id(cb.id_banque)
                    self.quel_compte_box.addItem(f"{cb.type} | {banque.nom} | {euro(self.cb_service.solde_from_cb(scenario.date_in, cb.id, date_solde_comptes).solde)}", cb.id)
                self.quel_compte_box.setDisabled(False)
        else:
            self.quel_compte_box.setDisabled(True)
    
    def enregistrer_clicked(self):
        type = self.type_box.currentText().strip()
        if type == investType.IMMO:
            self.enregistrer_immo()
        elif type == investType.STOCK:
            self.enregistrer_stock()
        else:
            self.page_msg.setText("Veuillez selectionner un type d'investissement avant de submit.")
        
    def enregistrer_stock(self):
        prix = None if not(self.prix_achat_input.hasAcceptableInput()) else float(self.prix_achat_input.text().strip())
        month = None if not(self.month_achat_input.hasAcceptableInput()) else int(self.month_achat_input.text().strip())
        year = None if not(self.year_achat_input.hasAcceptableInput()) else int(self.year_achat_input.text().strip())
        valorisation_pct = None if not(self.valorisation_pct_input.hasAcceptableInput()) else float(self.valorisation_pct_input.text().strip().replace(",","."))
        quel_compte_id = None if not(self.quel_compte_box.currentText().strip()) else self.quel_compte_box.currentData()
        titre = None if not(self.titre_projet.toPlainText().strip()) else self.titre_projet.toPlainText().strip()
        dividendes_pct = None if not(self.dividendes_pct_input.hasAcceptableInput()) else float(self.dividendes_pct_input.text().strip())
        
        if (prix is None
            or month is None
            or year is None
            or valorisation_pct is None
            or titre is None
            or quel_compte_id is None
            or dividendes_pct is None):
            self.page_msg.setText("Veuillez tout renseigner avant de submit.")
        else:
            data = {}
            
            data["ID USER"] = self.session.current_user.id
            data["ID SCENARIO"] = self.scenario_service.scenario_actif_id
            data["ID COMPTE"] = quel_compte_id
            data["TITRE"] = titre
            data["PRIX ACHAT"] = prix
            data["DATE ACHAT"] = date(year, month, 1)
            data["VALORISATION (%/AN)"] = valorisation_pct/100
            data["ETAT"] = "à conclure"
            data["DIVIDENDES (%)"] = dividendes_pct
            try:
                investissement = self.invest_service.save_invest(investType.STOCK, None, data)
                self.navigator.go_to(Page.INVESTISSEMENT_HUB)
            except SoldeInsuffisantError as e:
                self.page_msg.setText(f"Solde insuffisant : {e.solde}€ disponible, {e.montant_demande}€ requis")
            except ScenarioNotFoundError as e:
                self.page_msg.setText("Scénario introuvable — veuillez réessayer.")
            except NegativeAmountError as e:
                self.page_msg.setText(str(e))
            except QuantFolioError as e:
                self.page_msg.setText("Une erreur est survenue lors de l'enregistrement.")
    
    def enregistrer_immo(self):
        
        prix = None if not(self.prix_achat_input.hasAcceptableInput()) else float(self.prix_achat_input.text().strip())
        comptant = None if not(self.comptant_input.hasAcceptableInput()) else float(self.comptant_input.text().strip())
        month = None if not(self.month_achat_input.hasAcceptableInput()) else int(self.month_achat_input.text().strip())
        year = None if not(self.year_achat_input.hasAcceptableInput()) else int(self.year_achat_input.text().strip())
        valorisation_pct = None if not(self.valorisation_pct_input.hasAcceptableInput()) else float(self.valorisation_pct_input.text().strip().replace(",","."))
        quel_compte_id = None if not(self.quel_compte_box.currentText().strip()) else self.quel_compte_box.currentData()
        titre = None if not(self.titre_projet.toPlainText().strip()) else self.titre_projet.toPlainText().strip()
        ville = None if not(self.ville_input.text().strip()) else self.ville_input.text().strip()
        surface = None if not(self.surface_input.text().strip()) else float(self.surface_input.text().strip())
        type = None if not(self.type_bien_input.currentText().strip()) else self.type_bien_input.currentText().strip()

        print(prix is None,
             comptant is None,
             month is None,
             year is None,
             valorisation_pct is None,
             titre is None,
             surface is None,
             type is None,
             ville is None)
        if (prix is None
            or comptant is None
            or month is None
            or year is None
            or valorisation_pct is None
            or titre is None
            or surface is None
            or type is None
            or ville is None):
            self.page_msg.setText("Veuillez tout renseigner avant de submit.")
        else:
            data = {}
            
            data["ID USER"] = self.session.current_user.id
            data["ID SCENARIO"] = self.scenario_service.scenario_actif_id
            data["ID COMPTE"] = quel_compte_id
            data["TITRE"] = titre
            data["COMPTANT (%)"] = comptant/prix 
            data["PRIX ACHAT"] = prix
            data["DATE ACHAT"] = date(year, month, 1)
            data["VALORISATION (%/AN)"] = valorisation_pct/100
            data["ETAT"] = "à créditer"
            data["LOCALISATION"] = ville
            data["TYPE"] = type
            data["SURFACE"] = surface
            
            try:
                investissement = self.invest_service.save_invest(investType.IMMO,None, data)
                self.navigator.go_to(Page.INVESTISSEMENT_HUB)
            except SoldeInsuffisantError as e:
                self.page_msg.setText(f"Solde insuffisant : {e.solde}€ disponible, {e.montant_demande}€ requis")
            except ScenarioNotFoundError as e:
                self.page_msg.setText("Scénario introuvable — veuillez réessayer.")
            except NegativeAmountError as e:
                self.page_msg.setText(str(e))
            except QuantFolioError as e:
                self.page_msg.setText("Une erreur est survenue lors de l'enregistrement.")
            
    def validator_comptant(self):
        prix_input = self.prix_achat_input
        valide = prix_input.hasAcceptableInput()
        if valide:
            prix = prix_input.text().strip()
            self.comptant_input.setValidator(QDoubleValidator(0., float(prix.replace(",",'.')), 2))
            print(f"VLDTR Projet Immo Comptant {prix}")

    def load(self):
        scenario = self.scenario_service.get_scenario_by_id(self.scenario_service.scenario_actif_id)   
        if scenario:
            self.type_box.setCurrentIndex(0)
            self.immo_wgt.hide()
            self.stock_wgt.hide()
            self.common_wgt.show()
            
            self.quel_compte_box.clear()
            self.quel_compte_box.addItem("")
            cbs = self.cb_service.all_userCB_from_scenario(self.scenario_service.scenario_actif_id)
            scenario_date_in = scenario.date_in
            for cb in cbs:
                banque = self.banque_service.get_banque_by_id(cb.id_banque)
                self.quel_compte_box.addItem(f"{cb.type} | {banque.id} | {euro(self.cb_service.solde_from_cb(scenario_date_in, cb.id, scenario_date_in).solde)}", cb.id)
            
            self.titre_projet.clear()
            self.prix_achat_input.setText("")
            self.month_achat_input.setText("")
            self.year_achat_input.setText("")    
            self.valorisation_pct_input.setText("")    
            self.comptant_input.setText("")
            self.surface_input.clear()
            self.ville_input.clear()
            self.type_bien_input.setCurrentIndex(0)
            
            self.page_msg.setText("")
        else: 
            self.navigator.go_to(Page.NO_SCENARIO)
        self.navigator.hold_page(Page.NOUVEAU_PROJET)