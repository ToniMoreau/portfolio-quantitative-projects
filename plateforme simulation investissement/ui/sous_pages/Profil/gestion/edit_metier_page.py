
from PySide6.QtGui import QIntValidator, QDoubleValidator
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QListWidget, QListWidgetItem, QComboBox, QWidget, QVBoxLayout, QHBoxLayout,  QLabel, QPushButton, QLineEdit, QStackedWidget, QSizePolicy
)
from services import AppContext
from services.domain_services.metierService import MetierService
from session import Session
from utils.finance_format import age, euro
from datetime import date

class EditMetierPage(QWidget):
    back_to_hub = Signal()
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.metier_service = appContext.metier_service
        self.recette_service = appContext.recette_service
        self.cb_service = appContext.cb_service
        self.banque_service = appContext.banque_service
        self.fiscalite_service = appContext.fisca_service
        self.scenario_service = appContext.scenario_service
        self.session = session
        
        layout = QVBoxLayout(self)
        self.infos_metier = self.infos_metier_page()
        self.edit_metier = self.edit_metier_page()
        #self.add_metier = self.add_metier_page()
        
        self.stack = QStackedWidget()
        self.stack.addWidget(self.infos_metier) #index 0
        self.stack.addWidget(self.edit_metier) #index 1
        #self.stack.addWidget(self.add_metier)#index 2
        
        layout.addWidget(self.stack)
        
        self.stack.setCurrentIndex(0)   
        

    def enregistrer_clicked(self):
        profil_pro = self.metier_service.metier_actif
        
        intitule = self.intitule.text().strip()
        annuel_brut = self.annuel_brut.text().strip()
        annuel_net = self.annuel_net_input.text().strip()
        privé = self.privé.currentText().strip().capitalize()
        id_compte = self.sur_quel_compte.currentData()
        prlvt_source_pct = self.prlvt_source_input.text().strip()

        month_in = self.debut_month_input.text().strip()
        year_in = self.debut_annee_input.text().strip()
        month_out = self.fin_month_input.text().strip()
        year_out = self.fin_annee_input.text().strip()
        
        if profil_pro:
            id = profil_pro.id_metier
            id_salaire = profil_pro.id_recette
            
            intitule = profil_pro.intitule_métier if not(intitule) else intitule
            annuel_brut = profil_pro.annuel_brut if not(annuel_brut) else annuel_brut
            annuel_net = profil_pro.annuel_net if not(annuel_net) else annuel_net
            privé = profil_pro.privé if not(privé) else privé
            id_compte = profil_pro.id_compte if not(id_compte) else int(id_compte)
            prlvt_source_pct = profil_pro.prélèvement_source_pct if not(prlvt_source_pct) else float(prlvt_source_pct)
            
            date_in = profil_pro.date_in if not(month_in and year_in) else date(int(year_in), int(month_in), 1)
            date_out = profil_pro.date_out if not(month_out and year_out) else date(int(year_out), int(month_out),1)
        else:
            id = None
            id_salaire = None
            
            intitule = None if not(intitule) else intitule
            annuel_brut = None if not(annuel_brut) else float(annuel_brut)
            annuel_net = None if not(annuel_net) else float(annuel_net)
            privé = None if not(privé) else privé
            id_compte = None if not(id_compte) else id_compte
            prlvt_source_pct = None if not(prlvt_source_pct) else float(prlvt_source_pct)

            date_in = None if not(month_in and year_in) else date(int(year_in), int(month_in), 1)
            date_out = None if not(month_out and year_out) else date(int(year_out), int(month_out),1)
        
        if (intitule is None 
            or annuel_brut is None
            or privé is None
            or id_compte is None
            or prlvt_source_pct is None
            or date_in is None
            or date_out is None):
            self.enregistrer_msg.setText("Vous devez tout renseigner.")
        elif (date_out < date_in):
            self.enregistrer_msg.setText("Le début est après la fin. (dates)")
        else:
            if annuel_net is None:
                annuel_net = self.fiscalite_service.annuel_net_from_brut(annuel_brut, privé)
                
            recette_data = {
                "ID SCENARIO" : self.scenario_service.scenario_actif.id,
                "ID USER" : self.session.current_user.id,
                "ID COMPTE" : id_compte,
                "DATE IN" : date_in,
                "DATE OUT" : date_out,
                "INTITULE" : intitule, 
                "NATURE" : "Revenus", 
                "MONTANT" : annuel_net/12 * (1-prlvt_source_pct/100),
                "FREQUENCE" : "Mensuel"
            }
            salaire = self.recette_service.update_recette(id_salaire, recette_data)
            
            data = {
                "ID USER" : self.session.current_user.id,
                "ID COMPTE" : id_compte, 
                "ID SCENARIO" : self.scenario_service.scenario_actif.id,
                "ID SALAIRE" : salaire.id,
                "INTITULE" : intitule,
                "ANNUEL BRUT (€/AN)" : annuel_brut,
                "PRIVE" : privé,
                "ANNUEL NET (€/AN)" : annuel_net,
                "PAS (%)" : prlvt_source_pct,
                "DATE IN" : date_in,
                "DATE OUT": date_out
            }
            
            metier = self.metier_service.update_metier(id, data)
            
            self.load()
            self.stack.setCurrentIndex(0)
    
    def infos_metier_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        #Formulaire
        title =QLabel("Fiche Métier : ")
        self.scenario_label = QLabel()
        
        self.liste_wgt = QWidget()
        self.liste_lyt = QVBoxLayout(self.liste_wgt)
        self.liste_metier = QListWidget()
        self.liste_metier.clicked.connect(self.btn_metier_clicked)
        self.liste_lyt.addWidget(self.liste_metier)
        
        layout.addWidget(title)
        layout.addWidget(self.liste_wgt)
        #Boutons
        self.retour_btn = QPushButton("Retour <-")
        self.modifier_btn = QPushButton("Modifier ->")
        self.add_metier_btn = QPushButton("Ajouter Métier")
        self.suppr_metier_btn = QPushButton("Supprimer x")
        self.modifier_btn.hide()
        self.suppr_metier_btn.hide()
        
        layout.addWidget(self.add_metier_btn)
        layout.addWidget(self.modifier_btn)
        layout.addWidget(self.suppr_metier_btn)
        layout.addWidget(self.retour_btn)

        
        #actions boutons
        self.add_metier_btn.clicked.connect(lambda : self.add_edit_clicked("add"))
        self.retour_btn.clicked.connect(self.back_to_hub.emit)
        self.modifier_btn.clicked.connect(lambda : self.add_edit_clicked("edit"))
        self.suppr_metier_btn.clicked.connect(self.suppr_clicked)
        
        return page
    
    def suppr_clicked(self):
        id_salaire = self.metier_service.metier_actif.id_recette
        self.recette_service.delete_recette(self.recette_service.get_recette_by_id(id_salaire))
        self.metier_service.delete(self.metier_service.metier_actif.id_metier)
        self.load()
        
    def add_edit_clicked(self, mode :str):
        if mode == "add":
            self.title.setText("Ajouter un métier")
            self.metier_service.set_metier_actif(None)
        else: 
            self.title.setText("Modifier le métier : ")
        self.stack.setCurrentIndex(1)
        
    def btn_metier_clicked(self, metier_item : QListWidgetItem):
        self.suppr_metier_btn.show()
        self.modifier_btn.show()
        
        metier_id = metier_item.data(1)
        metier = self.metier_service.get_metier_by_id(metier_id)
        self.metier_service.set_metier_actif(metier)
        
    def edit_metier_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        #Formulaire
        self.title =QLabel("Modifier le métier : ")
        
        intitule = QLabel("*Intitule")
        self.intitule = QLineEdit()
        self.intitule.setPlaceholderText("Entrer le nouveau nom de métier")
        
        annuel_brut = QLabel("*Salaire annuel brut :")
        self.annuel_brut = QLineEdit()
        self.annuel_brut.setPlaceholderText("Entrer le nouveau salaire annuel brut")
        
        annuel_net_lbl = QLabel("Salaire annuel net :")
        self.annuel_net_input = QLineEdit()
        self.annuel_net_input.setPlaceholderText("Entrer le nouveau salaire annuel net")
        
        privé = QLabel("*Dans le privé ?")
        self.privé = QComboBox()
        self.privé.addItem("")
        self.privé.addItems(["Oui", "Non"])
        
        self.sur_quel_compte = QComboBox()
        
        prlvt_source_lbl = QLabel("*Taux actuel de prélèvement à la source :")
        self.prlvt_source_input = QLineEdit()
        self.prlvt_source_input.setPlaceholderText("taux (%)")
        self.prlvt_source_input.setValidator(QDoubleValidator(0,100,2))
        
        self.etendu_wgt = QWidget()
        self.etendu_lyt = QHBoxLayout(self.etendu_wgt)
        self.debut_metier_lbl = QLabel("*En activité du ")
        
        self.debut_month_input = QLineEdit()
        self.debut_month_input.setPlaceholderText("Mois")
        self.debut_month_input.setValidator(QIntValidator(0,12))
        
        self.debut_annee_input = QLineEdit()
        self.debut_annee_input.setPlaceholderText("Année")
        self.debut_annee_input.setValidator(QIntValidator(1980, 2200))
        
        self.fin_metier_lbl = QLabel("jusqu'au")
        
        self.fin_month_input = QLineEdit()
        self.fin_month_input.setPlaceholderText("Mois")
        self.fin_month_input.setValidator(QIntValidator(0,12))
        
        self.fin_annee_input = QLineEdit()
        self.fin_annee_input.setPlaceholderText("Année")
        self.fin_annee_input.setValidator(QIntValidator(1980,2200))

        self.etendu_lyt.addWidget(self.debut_metier_lbl)
        self.etendu_lyt.addWidget(self.debut_month_input)
        self.etendu_lyt.addWidget(self.debut_annee_input)
        self.etendu_lyt.addWidget(self.fin_metier_lbl)
        self.etendu_lyt.addWidget(self.fin_month_input)
        self.etendu_lyt.addWidget(self.fin_annee_input)
        
        layout.addWidget(self.title)
        layout.addWidget(intitule)
        layout.addWidget(self.intitule)
        layout.addWidget(annuel_brut)
        layout.addWidget(self.annuel_brut)
        layout.addWidget(annuel_net_lbl)
        layout.addWidget(self.annuel_net_input)
        layout.addWidget(privé)
        layout.addWidget(self.privé)
        layout.addWidget(self.sur_quel_compte)
        layout.addWidget(prlvt_source_lbl)
        layout.addWidget(self.prlvt_source_input)
        layout.addWidget(self.etendu_wgt)
        
        #Boutons
        self.annuler_btn = QPushButton("Annuler x")
        self.enregistrer_btn = QPushButton("Enregister")
        self.enregistrer_msg = QLabel()
        
        layout.addWidget(self.enregistrer_btn)
        layout.addWidget(self.enregistrer_msg)
        layout.addWidget(self.annuler_btn)
        
        #actions boutons
        self.annuler_btn.clicked.connect(lambda : self.stack.setCurrentIndex(0))
        self.enregistrer_btn.clicked.connect(self.enregistrer_clicked)
        return page


    def load(self):
        self.metier_service.set_metier_actif(None)
        self.sur_quel_compte.clear()
        for compte in self.cb_service.all_userCB_from_scenario(self.scenario_service.scenario_actif.id):
            banque= self.banque_service.get_banque_by_id(compte.id_banque)
            self.sur_quel_compte.addItem(f"{compte.type}, {banque.nom}", compte.id)
        
        metier = self.metier_service.metier_actif
        if metier:
            self.title.setText(f"Modifier le métier actuel : {metier.intitule_métier}, {euro(metier.annuel_brut)}.")
            
        scenario_id = self.scenario_service.scenario_actif.id
        metiers = self.metier_service.get_metier_by_scenario(scenario_id)
        self.liste_metier.clear()
        for metier in metiers:
            metier_item = QListWidgetItem(f" Du {metier.date_in} au {metier.date_out} : {metier.intitule_métier}, {euro(metier.annuel_brut)}")
            metier_item.setData(1, metier.id_metier)
            self.liste_metier.addItem(metier_item)
        
        self.intitule.setText("")
        self.annuel_brut.setText("")
        self.annuel_net_input.setText("")
        self.privé.setCurrentIndex(0)
        self.sur_quel_compte.setCurrentIndex(0)
        self.prlvt_source_input.setText("")
        
        self.scenario_label.setText(f"Scénario : {self.scenario_service.scenario_actif.intitule}")
        
        self.modifier_btn.hide()
        self.suppr_metier_btn.hide()
