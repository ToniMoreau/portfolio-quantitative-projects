
from PySide6.QtGui import QIntValidator
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QListWidget, QListWidgetItem, QComboBox, QWidget, QVBoxLayout, QHBoxLayout,  QLabel, QPushButton, QLineEdit, QStackedWidget, QSizePolicy
)
from services import AppContext
from services.domain_services.metierService import MetierService
from session import Session
from utils.finance_format import age, euro

class EditMetierPage(QWidget):
    back_to_hub = Signal()
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.metier_service = appContext.metier_service
        self.recette_service = appContext.recette_service
        self.cb_service = appContext.cb_service
        self.banque_service = appContext.banque_service
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
        print(profil_pro)
        if profil_pro:
            print("got into")
            intitule = self.intitule.text().strip()
            print(intitule)
            intitule = intitule if intitule else profil_pro.intitule_métier
            
            annuel_brut = self.annuel_brut.text().strip()
            annuel_brut = annuel_brut if annuel_brut else profil_pro.annuel_brut
            annuel_brut = float(annuel_brut)
            
            privé = self.privé.currentText().strip().capitalize()
            privé = privé if privé else profil_pro.privé
            
            id_compte = self.sur_quel_compte.currentData()
            id_compte = id_compte if id_compte else profil_pro.id_compte
        else:
            intitule = None if not(self.intitule.text().strip()) else self.intitule.text().strip()
            annuel_brut = None if not(self.annuel_brut.text().strip()) else float(self.annuel_brut.text().strip())
            privé = None if not(self.privé.currentText().strip()) else self.privé.currentText().strip().capitalize()
            id_compte = None if not(self.sur_quel_compte.currentData()) else self.sur_quel_compte.currentData()

        if (intitule is None 
            or annuel_brut is None
            or privé is None
            or id_compte is None):
            self.enregistrer_msg.setText("Vous devez tout renseigner.")
        else:
            
            data = {
                "ID USER" : self.session.current_user.id,
                "ID COMPTE" : id_compte, 
                "ID SCENARIO" : self.scenario_service.scenario_actif.id,
                "INTITULE" : intitule,
                "ANNUEL BRUT (€/AN)" : annuel_brut,
                "PRIVE" : privé
            }
            if profil_pro:
                id = profil_pro.id_metier
            else: id = None
            
            metier = self.metier_service.update_metier(id, data)
            print(metier)
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
        print(metier_id)
        metier = self.metier_service.get_metier_by_id(metier_id)
        self.metier_service.set_metier_actif(metier)
        
    def edit_metier_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        #Formulaire
        self.title =QLabel("Modifier le métier : ")
        
        intitule = QLabel("Intitule")
        self.intitule = QLineEdit()
        self.intitule.setPlaceholderText("Entrer le nouveau nom de métier")
        
        annuel_brut = QLabel("Salaire annuel brut :")
        self.annuel_brut = QLineEdit()
        self.annuel_brut.setPlaceholderText("Entrer le nouveau salaire annuel brut")
        
        privé = QLabel("Dans le privé ?")
        self.privé = QComboBox()
        self.privé.addItem("")
        self.privé.addItems(["", "Oui", "Non"])
        
        self.sur_quel_compte = QComboBox()
        
        self.etendu_wgt = QWidget()
        self.etendu_lyt = QHBoxLayout(self.etendu_wgt)
        self.debut_depense_lbl = QLabel("En activité du mois n°")
        self.debut_depense_input = QLineEdit()
        self.debut_depense_input.setValidator(QIntValidator(0,1200))
        self.debut_depense_input.textChanged.connect(self.fin_periode_intvalidator_updt)
        
        self.fin_depense_lbl = QLabel("jusqu'au mois n°")
        self.fin_depense_input = QLineEdit()
        self.fin_depense_input.setValidator(QIntValidator(0,1200))
        self.etendu_lyt.addWidget(self.debut_depense_lbl)
        self.etendu_lyt.addWidget(self.debut_depense_input)
        self.etendu_lyt.addWidget(self.fin_depense_lbl)
        self.etendu_lyt.addWidget(self.fin_depense_input)
        
        layout.addWidget(self.title)
        layout.addWidget(intitule)
        layout.addWidget(self.intitule)
        layout.addWidget(annuel_brut)
        layout.addWidget(self.annuel_brut)
        layout.addWidget(privé)
        layout.addWidget(self.privé)
        layout.addWidget(self.sur_quel_compte)
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
    
    def fin_periode_intvalidator_updt(self, debut):
        debut = debut.strip()
        if debut:
            debut = int(debut)
        else: 
            debut = 0
        self.fin_depense_input.setValidator(QIntValidator(debut, 1200))   

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
        print("scenar id :", scenario_id)
        metiers = self.metier_service.get_metier_by_scenario(scenario_id)
        self.liste_metier.clear()
        for metier in metiers:
            metier_item = QListWidgetItem(f" Du .. au .. : {metier.intitule_métier}, {euro(metier.annuel_brut)}")
            metier_item.setData(1, metier.id_metier)
            self.liste_metier.addItem(metier_item)
        
        self.intitule.setText("")
        self.annuel_brut.setText("")
        self.privé.setCurrentIndex(0)
        self.scenario_label.setText(f"Scénario : {self.scenario_service.scenario_actif.intitule}")
        
        self.modifier_btn.hide()
        self.suppr_metier_btn.hide()
