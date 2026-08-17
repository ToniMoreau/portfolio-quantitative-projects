#flattened

from PySide6.QtCore import Signal
from PySide6.QtGui import QIntValidator, QDoubleValidator
from PySide6.QtWidgets import (
    QMessageBox, QTableWidget, QTableWidgetItem,
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QLineEdit, QStackedWidget, QSizePolicy
)

from services import AppContext, Page, PatrimoineService
from session import Session

from utils.finance_format import euro
from utils.date import month_count
from datetime import date
from .nouveau_projet_page import NouveauProjetPage
from .infos_projet_page import InfosProjetPage
from domain.enums import investType
from ui.widgets import confirm_and_delete
from domain.errors import *

class InvestissementHubPage(QWidget):
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.patrimoine_service = appContext.patrimoine_service
        self.scenario_service = appContext.scenario_service
        self.invest_service = appContext.invest_service
        self.credit_service = appContext.credit_service
        self.depense_service = appContext.depense_service
        self.recette_service = appContext.recette_service
        self.session = session
        self.navigator = appContext.navigator
        
        layout = QVBoxLayout(self)
        
        self.hub_page = self.hub()        
        layout.addWidget(self.hub_page) 
        
    def hub(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        self.title = QLabel("Incomings/Actifs/Old")
        
        self.filter_wgt = QWidget()
        self.filter_layout = QHBoxLayout(self.filter_wgt)
        
        self.date_lbl = QLabel("Investissements antérieur au ")
        self.month_input = QLineEdit("")
        self.month_input.setValidator(QIntValidator(0,12))
        self.month_input.setPlaceholderText("MM")
        
        self.year_input = QLineEdit("")
        self.year_input.setPlaceholderText("AAAA")
        self.year_input.setValidator(QIntValidator(1980, 2200))
        
        self.actualiser_date_btn = QPushButton("Actualiser")
        self.actualiser_date_btn.clicked.connect(self.load)
        
        self.effacer_filtre_btn = QPushButton("Effacer filtre")
        
        self.filter_layout.addWidget(self.date_lbl,1)
        self.filter_layout.addWidget(self.month_input,1)
        self.filter_layout.addWidget(self.year_input, 2)
        self.filter_layout.addWidget(self.actualiser_date_btn, 3)
        self.filter_layout.addWidget(self.effacer_filtre_btn,2)
        
        self.invest_tab = QTableWidget()
        self.invest_tab.setColumnCount(12)
        self.invest_tab.setHorizontalHeaderLabels([
            "Type", "Nom","Date Achat", "Prix Achat", "Coût Réel Achat","Valeur Corrigée Actuelle", "Paiement Comptant", "Crédit Restant", "Duréee Crédit Restante", "Date Vente","Prix Vente","Etat"
        ])
        self.invest_tab.cellClicked.connect(self.invest_cell_clicked)
        
        btns_wgt = QWidget()
        self.btns_lyt = QHBoxLayout(btns_wgt)
        
        left_btns_wgt = QWidget()
        self.left_btns_lyt = QHBoxLayout(left_btns_wgt)
        self.nouveau_projet_btn = QPushButton("Nouveau Projet")
        
        right_btns_wgt = QWidget()
        self.right_btns_lyt = QHBoxLayout(right_btns_wgt)
        self.infos_btn = QPushButton("+ d'infos")
        self.vendre_btn =QPushButton("Vendre")
        self.supprimer_btn = QPushButton("Supprimer")
        self.credit_btn = QPushButton("vers Crédit")
        self.conclure_btn = QPushButton("Conclure")
        
        self.btns_lyt.addWidget(left_btns_wgt)
        self.left_btns_lyt.addWidget(self.nouveau_projet_btn)

        self.btns_lyt.addStretch()
        
        self.btns_lyt.addWidget(right_btns_wgt)
        self.right_btns_lyt.addWidget(self.infos_btn)
        self.right_btns_lyt.addWidget(self.vendre_btn)
        self.right_btns_lyt.addWidget(self.supprimer_btn)
        self.right_btns_lyt.addWidget(self.credit_btn)
        self.right_btns_lyt.addWidget(self.conclure_btn)
        
        layout.addWidget(self.title)
        layout.addWidget(self.filter_wgt)
        layout.addWidget(self.invest_tab)
        layout.addWidget(btns_wgt)
    
        layout.addStretch()
        
        self.supprimer_btn.clicked.connect(self.suppr_clicked)

        self.nouveau_projet_btn.clicked.connect(lambda : self.navigator.go_to(Page.NOUVEAU_PROJET))
        self.infos_btn.clicked.connect(lambda : self.navigator.go_to(Page.INFOS_PROJET))
        self.credit_btn.clicked.connect(self.go_to_credit)
        self.conclure_btn.clicked.connect(self.conclure_clicked)
        self.vendre_btn.clicked.connect(self.vendre_clicked)
        
        self.conclure_btn.hide()
        self.credit_btn.hide()
        self.infos_btn.hide()
        self.vendre_btn.hide()
        
        return page
    
    def vendre_clicked(self):
        scenario = self.scenario_service.get_scenario_by_id(self.scenario_service.scenario_actif_id)   

        invest_row = self.invest_tab.currentRow()
        invest_id = self.invest_tab.item(invest_row, 0).data(1)
        if invest_id is not None:
            invest = self.invest_service.get_by_id(invest_id)
            month = self.month_input.text().strip()
            year = self.year_input.text().strip()
            
            if invest.etat == "actif" and month and year:
                month = int(month)
                year = int(year)
                date_vente = date(year, month, 1)
                if invest.date_in <= date_vente and date_vente <= scenario.date_limite:
                    data_recette = {}
                    data_recette["DATE IN"] = data_recette["DATE OUT"] = date_vente
                    data_recette["ID SCENARIO"] = self.scenario_service.scenario_actif_id
                    data_recette["ID USER"] = self.session.current_user.id
                    data_recette["ID COMPTE"] = invest.id_compte
                    data_recette["INTITULE"] = f"Vente {invest.titre}"
                    data_recette["ID SOURCE"] = invest.id
                    data_recette["NATURE"] = "Investissement"
                    data_recette["MONTANT"] = invest.prix_vente(date_vente)
                    data_recette["FREQUENCE"] = "Ponctuel"
                    
                    achat= self.recette_service.update_recette(None, data_recette)
                    self.invest_service.update_investissement(invest.id, {"ID VENTE" : achat.id, "ETAT" : "vendu", "DATE VENTE" : date_vente})
                    if invest.nature == investType.STOCK and invest.id_dividendes is not None:
                        dividendes = self.recette_service.update_recette(invest.id_dividendes, {"DATE OUT" : date_vente})
                    elif invest.nature == investType.IMMO:
                        self.recette_service.update_location_from_vente_immo(invest.id, date_vente)                    
                    self.load()
                    
            return
    
    def conclure_clicked(self):
        scenario = self.scenario_service.get_scenario_by_id(self.scenario_service.scenario_actif_id)   
        invest_row = self.invest_tab.currentRow()
        invest_id = self.invest_tab.item(invest_row, 0).data(1)
        print(invest_id)
        if invest_id is not None:
            invest = self.invest_service.get_by_id(invest_id)
            if invest.etat == "à conclure":
                data_depense = {}
                
                data_depense["DATE IN"] = data_depense["DATE OUT"] = invest.date_in
                data_depense["ID SCENARIO"] = self.scenario_service.scenario_actif_id
                data_depense["ID USER"] = self.session.current_user.id
                data_depense["ID COMPTE"] = invest.id_compte
                data_depense["INTITULE"] = f"Achat {invest.titre}"
                data_depense["NATURE"] = "Investissement"
                data_depense["MONTANT"] = invest.prix_achat
                data_depense["FREQUENCE"] = "Ponctuel"
                data_depense["ID SOURCE"] = invest.id
                
                achat= self.depense_service.update_depense(None, data_depense)
                self.invest_service.update_investissement(invest.id, {"ID ACHAT" : achat.id, "ETAT" : "actif"})
                if invest.nature == "Stock":
                    data_dividendes = {}
                    
                    data_dividendes["DATE IN"] = invest.date_in
                    data_dividendes["DATE OUT"] = scenario.date_limite
                    data_dividendes["ID SCENARIO"] = self.scenario_service.scenario_actif_id
                    data_dividendes["ID USER"] = self.session.current_user.id
                    data_dividendes["ID COMPTE"] = invest.id_compte
                    data_dividendes["INTITULE"] = f"Dividendes {invest.titre}"
                    data_dividendes["NATURE"] = "Investissement"
                    data_dividendes["MONTANT"] = invest.dividendes_montant()
                    data_dividendes["FREQUENCE"] = "Annuel"
                    data_dividendes["ID SOURCE"] = invest.id
                    
                    divids= self.recette_service.update_recette(None, data_dividendes)
                    self.invest_service.update_investissement(invest.id, {"ID DIVIDENDES" : divids.id})
                self.load()
                    
        return
                  
    def go_to_credit(self):
        invest_row = self.invest_tab.currentRow()
        invest_id = self.invest_tab.item(invest_row, 0).data(1)
        print(invest_id)
        if invest_id is not None:
            invest = self.invest_service.get_by_id(invest_id)
            self.invest_service.set_invest_actif(invest_id)
            if invest.id_credit is None:
                self.navigator.go_to(Page.NO_CREDIT)
            else:
                pass
           
    def invest_cell_clicked(self, row,col):
        self.vendre_btn.hide()
        self.supprimer_btn.hide()
        self.credit_btn.hide()
        self.conclure_btn.hide()
        
        item_ref = self.invest_tab.item(row, 0)
        if item_ref is None:
            return
        invest_id = item_ref.data(1)
        invest = self.invest_service.get_by_id(invest_id)         
        if invest is not None:
            self.invest_service.set_invest_actif(invest_id)
            if invest.etat =="à créditer":
                self.credit_btn.show()
            elif invest.etat == "à conclure":
                self.conclure_btn.show()
            elif invest.etat =="actif":
                self.vendre_btn.show()
            else:
                return
        self.supprimer_btn.show()
        return
    
    def suppr_clicked(self):
        scenario = self.scenario_service.get_scenario_by_id(self.scenario_service.scenario_actif_id)   
        item_row = self.invest_tab.currentRow()
        if item_row <0:
            return
        item_ref = self.invest_tab.item(item_row, 0)
        if item_ref is None:
            return
        invest = self.invest_service.get_by_id(item_ref.data(1))
        if invest is None:
            QMessageBox.warning(self, "Erreur.", "Aucun investissement sélectionné.")
            return
        try:
            if confirm_and_delete(self.patrimoine_service,scenario, invest, self):
                self.load()
        except QuantFolioError as e:
            QMessageBox.critical(self, "Suppression impossible :", str(e))
        
    def load(self):
        print("j'ai load")
        scenario = self.scenario_service.get_scenario_by_id(self.scenario_service.scenario_actif_id)   
        if scenario:
            month = self.month_input.text().strip()
            year = self.year_input.text().strip()
            if month and year:
                date_seuil = date(int(year), int(month), 1)
            else:
                self.month_input.setText(str(scenario.date_in.month))
                self.year_input.setText(str(scenario.date_in.year))
                
                date_seuil = scenario.date_in
            invests = self.invest_service.get_by_scenario(scenario.id) or []

            self.invest_tab.setRowCount(len(invests))
            for i,invest in enumerate(invests):
                if invest.date_in <= date_seuil:
                    print("invest 1")
                    
                    nature_item = QTableWidgetItem(str(invest.nature))
                    nature_item.setData(1,invest.id)
                    self.invest_tab.setItem(i,0, nature_item)
                    
                    if invest.nature == investType.IMMO:
                        self.invest_tab.setItem(i,1, QTableWidgetItem(str(invest.titre)))
                        self.invest_tab.setItem(i,2, QTableWidgetItem(str(invest.date_in)))
                        self.invest_tab.setItem(i,3, QTableWidgetItem(str(euro(invest.prix_achat))))
                        self.invest_tab.setItem(i,5, QTableWidgetItem(str(euro(invest.present_value(date_seuil)))))
                        self.invest_tab.setItem(i,6, QTableWidgetItem(str(euro(invest.apport_personnel))))
                        credit = self.credit_service.get_credit_by_id(invest.id_credit)
                        if credit is not None:
                            self.invest_tab.setItem(i,4, QTableWidgetItem(str(euro(credit.present_value()+invest.prix_achat-credit.montant))))

                            montant_credit_restant = credit.credit_restant_from_date(date_seuil)
                            duree_credit_restante = credit.duree_restante_from_date(date_seuil)
                            self.invest_tab.setItem(i,7, QTableWidgetItem(str(euro(montant_credit_restant))))
                            self.invest_tab.setItem(i,8, QTableWidgetItem(str((duree_credit_restante))))
                        
                        self.invest_tab.setItem(i,9, QTableWidgetItem(str(invest.date_out) or ""))
                        self.invest_tab.setItem(i,10, QTableWidgetItem(str(euro(invest.prix_vente(date_seuil)))))
                        self.invest_tab.setItem(i,11, QTableWidgetItem(str(invest.etat)))
                    elif invest.nature == investType.STOCK:
                        self.invest_tab.setItem(i,1, QTableWidgetItem(str(invest.titre)))
                        self.invest_tab.setItem(i,2, QTableWidgetItem(str(invest.date_in)))
                        self.invest_tab.setItem(i,3, QTableWidgetItem(str(euro(invest.prix_achat))))
                        self.invest_tab.setItem(i,5, QTableWidgetItem(str(euro(invest.present_value(date_seuil)))))
                        
                        self.invest_tab.setItem(i,9, QTableWidgetItem(str(invest.date_out) or ""))
                        self.invest_tab.setItem(i,10, QTableWidgetItem(str(euro(invest.prix_vente(date_seuil)))))
                        self.invest_tab.setItem(i,11, QTableWidgetItem(str(invest.etat)))
                    
            self.conclure_btn.hide()
            self.credit_btn.hide()
            self.infos_btn.hide()
            self.vendre_btn.hide()
            self.supprimer_btn.hide()
            self.invest_service.set_invest_actif(None)
                
        else:
            self.navigator.go_to(Page.NO_SCENARIO)
        self.navigator.hold_page(Page.INVESTISSEMENT_HUB)