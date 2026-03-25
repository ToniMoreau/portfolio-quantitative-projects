


from PySide6.QtWidgets import QTableWidget, QTableWidgetItem,QComboBox, QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel, QLineEdit
from PySide6.QtCore import Signal
from PySide6.QtGui import QIntValidator
from utils.finance_format import euro
from services import AppContext
from session import Session

class AjouterCreditPage(QWidget):
    back_to_hub = Signal()
    
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.banque_service = appContext.banque_service
        self.credit_service = appContext.credit_service
        self.depense_service = appContext.depense_service
        self.cb_service = appContext.cb_service
        self.session = session
        self.scenario_service = appContext.scenario_service
        
        self.mlayout = QVBoxLayout(self)
        
        #Formulaire
        self.scenario_label = QLabel(f"")
        self.capacite_emprunt = QLabel("Capacité maximum d'emprunt : ")
        self.message_emprunt = QLabel()

        self.info_widget = QWidget()
        info_layout = QVBoxLayout(self.info_widget)

        title =QLabel("Ajouter Crédit : ")
        
        banque_layout = QHBoxLayout()
        banque_choix = QLabel("Chez quelle banque : ")
        self.banque_choix = QComboBox()
        self.banque_choix.currentIndexChanged.connect(self.update_variables)
        self.banque_choix.currentTextChanged.connect(self.update_choix)
        self.banque_choix.currentTextChanged.connect(self.on_change)
        # Taux d'intérêt
        self.taux_interet = QLabel("Taux d'intérêt (%) : ")
        
        banque_layout.addWidget(self.banque_choix,2)
        banque_layout.addWidget(self.taux_interet,1)
        
        #Compte
        compte_choix = QLabel("Choix du compte associé au crédit : ")
        self.compte_bancaire_choix = QComboBox()
        self.compte_bancaire_choix.currentTextChanged.connect(self.on_change)
        
        #type d'annuité
        type_lyt = QHBoxLayout()
        
        type_lbl= QLabel("Que voulez vous renseigner :")
        self.type_list = QComboBox()
        self.type_list.addItem("")
        
        self.montant_mensualite = ["MONTANT", "MENSUALITE (€)"]
        self.mensualite_duree = ["MENSUALITE (€)", "DUREE (MOIS)"]
        self.montant_duree = ["MONTANT", "DUREE (MOIS)"]
        
        self.type_list.addItem("Montant + Mensualité ", self.montant_mensualite)
        self.type_list.addItem("Mensualité + Durée", self.mensualite_duree)
        self.type_list.addItem("Montant + Durée", self.montant_duree)
        
        self.type_list.currentIndexChanged.connect(self.update_type)
        self.type_list.currentTextChanged.connect(self.on_change)

        type_lyt.addWidget(type_lbl)
        type_lyt.addWidget(self.type_list)
        
        # Durée différée
        duree_differee = QLabel("Durée différée (années) : ")
        self.duree_differee_input = QLineEdit()
        self.duree_differee_input.setPlaceholderText("Entrer la durée différée")
        self.duree_differee_input.textChanged.connect(self.test_limite_ddiff_input)
        self.duree_differee_input.textChanged.connect(self.update_variables)
        self.duree_diff_msg = QLabel("")

        # Montant du crédit
        self.montant_widget = QWidget()
        montant_lyt = QVBoxLayout(self.montant_widget)
        
        montant_lbl = QLabel("Montant du crédit : ")
        self.montant_input = QLineEdit()
        self.montant_input.setPlaceholderText("Entrer un montant initial")
        self.montant_input.textChanged.connect(self.test_limite_montant_input)
        self.montant_input.textChanged.connect(self.update_variables)
        self.montant_input.textChanged.connect(self.on_change)
        self.montant_msg = QLabel("")
        
        montant_lyt.addWidget(montant_lbl)
        montant_lyt.addWidget(self.montant_input)
        montant_lyt.addWidget(self.montant_msg)
        self.montant_widget.hide()
        
        # Durée du crédit
        self.duree_credit_wgt = QWidget()
        duree_credit_lyt = QVBoxLayout(self.duree_credit_wgt)
        
        duree_credit_lbl = QLabel("Durée du Crédit :")
        self.duree_credit_input = QLineEdit()
        self.duree_credit_input.setPlaceholderText("Entrer la durée du crédit souhaitée")
        self.duree_credit_input.textChanged.connect(self.update_variables)
        self.duree_credit_input.textChanged.connect(self.test_limite_duree_input)
        self.duree_credit_input.textChanged.connect(self.on_change)
        self.duree_credit_msg = QLabel("")
        
        duree_credit_lyt.addWidget(duree_credit_lbl)
        duree_credit_lyt.addWidget(self.duree_credit_input)
        duree_credit_lyt.addWidget(self.duree_credit_msg)
        self.duree_credit_wgt.hide()
        
        # Mensualité cible
        self.mensualite_wgt = QWidget()
        self.mensualite_lyt = QVBoxLayout(self.mensualite_wgt)
        
        mensualite_lbl = QLabel("Mensualité cible :")
        self.mensualite_input = QLineEdit()
        self.mensualite_input.setPlaceholderText("Entrer la mensualité souhaitée")
        self.mensualite_input.textChanged.connect(self.update_variables)
        self.mensualite_input.textChanged.connect(self.test_limite_mensu_input)
        self.mensualite_input.textChanged.connect(self.on_change)
        self.mensualite_msg = QLabel("")
        
        self.mensualite_lyt.addWidget(mensualite_lbl)
        self.mensualite_lyt.addWidget(self.mensualite_input)
        self.mensualite_lyt.addWidget(self.mensualite_msg)
        self.mensualite_wgt.hide()
        
        variables_lyt = QHBoxLayout()
        variables_lyt.addWidget(self.montant_widget,1)
        variables_lyt.addWidget(self.mensualite_wgt,1)
        variables_lyt.addWidget(self.duree_credit_wgt,1)
        
        self.etendu_wgt = QWidget()
        self.etendu_lyt = QHBoxLayout(self.etendu_wgt)
        self.debut_credit_lbl = QLabel("Début au mois n°")
        self.debut_credit_input = QLineEdit()
        self.debut_credit_input.setFixedWidth(60)
        self.debut_credit_input.setValidator(QIntValidator(0,1200))
        
        self.etendu_lyt.addWidget(self.debut_credit_lbl)
        self.etendu_lyt.addWidget(self.debut_credit_input)
        self.etendu_lyt.addStretch()
        
        self.recap_tab = QTableWidget()
        self.recap_tab.setColumnCount(3)
        self.recap_tab.setRowCount(1)
        self.recap_tab.setHorizontalHeaderLabels(["Crédit", "Coût", "Total"])
        self.recap_tab.setMaximumWidth(500)
        
        self.mlayout.addWidget(self.scenario_label)
        self.mlayout.addWidget(self.etendu_wgt)
        self.mlayout.addWidget(self.capacite_emprunt)
        
        self.mlayout.addWidget(self.info_widget)
        
        info_layout.addWidget(title)
        info_layout.addWidget(banque_choix)
        info_layout.addLayout(banque_layout)
        info_layout.addWidget(compte_choix)
        info_layout.addWidget(self.compte_bancaire_choix)
        info_layout.addLayout(type_lyt)
        info_layout.addWidget(duree_differee)
        info_layout.addWidget(self.duree_differee_input)
        info_layout.addWidget(self.duree_diff_msg)        
        info_layout.addLayout(variables_lyt)
        
        info_layout.addWidget(self.recap_tab)

        #Boutons
        self.annuler_btn = QPushButton("Annuler x")
        self.enregistrer_btn = QPushButton("Accepter")
        
        info_layout.addWidget(self.enregistrer_btn)
        self.mlayout.addWidget(self.annuler_btn)

        #actions boutons
        self.annuler_btn.clicked.connect(self.back_to_hub.emit)
        self.enregistrer_btn.clicked.connect(self.enregistrer_clicked)
        self.enregistrer_btn.setEnabled(False)
    
    def on_change(self):
        ok = (
            self.banque_choix.currentText() is not None
            and self.compte_bancaire_choix.currentText() is not None
            and self.type_list.currentText() is not None
            and self.test_limite_mensu_input(self.mensualite_input.text().strip())
            and self.test_limite_duree_input(self.duree_credit_input.text().strip())
            and self.test_limite_montant_input(self.montant_input.text().strip())
        )
        ok = ok or (self.credit_service.credit_actif is not None)
        print(ok)
        self.enregistrer_btn.setEnabled(ok) 

    def test_limite_montant_input(self, montant : str):
        montant = montant.strip() 
        try :
            if montant == "":
                self.montant_msg.setText("")
                return False
            montant = float(montant) 
        except ValueError:
            self.montant_msg.setText("Chiffres uniquement.")
            return False
        else:
            bas = 100
            taux = self.banque_service.get_banque_by_id(self.banque_choix.currentData()).taux_credit_pct
            capa_annuelle = round(self.credit_service.montant_from_mensu_duree(360,self.capa_mensu, taux,0),2)
            if montant <=bas or montant > capa_annuelle:
                self.montant_msg.setText(f"Doit être entre {euro(bas)} et {euro(capa_annuelle)}.")
                return False
            self.montant_msg.setText("valide.")
            return True

    def test_limite_mensu_input(self, mensu : str):
        mensu = mensu.strip() 
        try :
            if mensu == "":
                self.mensualite_msg.setText("")
                return False
            mensu = float(mensu)
            
        except ValueError:
            self.mensualite_msg.setText("Chiffres uniquement.")
            return False
        else:
            capa_mensu = round(self.capa_mensu,2)
            if mensu <=0:
                self.mensualite_msg.setText("Entrer une valeur positive")
                return False
            elif mensu > self.capa_mensu:
                self.mensualite_msg.setText(f"Entrer valeur inférieur à {euro(capa_mensu)}.")
                return False
            
            self.mensualite_msg.setText("valide.")
            return True
     
    def test_limite_duree_input(self, duree : str):
        duree = duree.strip() 
        try :
            if duree =="":
                self.duree_credit_msg.setText("")
                return False
            duree = int(duree)
        except ValueError:
            self.duree_credit_msg.setText("Chiffres uniquement.")
            return False
        else:
            if duree <=0:
                self.duree_credit_msg.setText("Entrer une valeur positive")
                return False
            elif duree > 360:
                self.duree_credit_msg.setText("Entrer une valeur inférieur à 360 mois.")
                return False
            self.duree_credit_msg.setText(f"Donc {int(duree/12)} ans.")
            return True
        
    def test_limite_ddiff_input(self, duree : str):
        duree = duree.strip() 
        try :
            if duree =="":
                self.duree_diff_msg.setText("")
                return False
            duree = int(duree)
        except ValueError:
            self.duree_diff_msg.setText("Chiffres uniquement.")
            return False
        else:
            if duree <0:
                self.duree_diff_msg.setText("Entrer une valeur >= 0.")
                return False
            elif duree > 72:
                self.duree_diff_msg.setText("Entrer une valeur inférieur à 72 mois.")
                return False
            self.duree_diff_msg.setText(f"Donc {int(duree/12)} ans.")
            return True

    def update_variables(self):
        type_actif = self.type_list.currentData()
        banque = self.banque_service.get_banque_by_name(self.banque_choix.currentText().strip())
        ddiff_mois = self.duree_differee_input.text().strip()
        if self.test_limite_ddiff_input(ddiff_mois):
            ddiff_mois = int(ddiff_mois)
        else:
            ddiff_mois = 0
        mensu = None
        montant = None
        duree = None
        if type_actif == self.mensualite_duree:            
            duree = self.duree_credit_input.text().strip()
            mensu = self.mensualite_input.text().strip()
            montant = ""
            self.montant_msg.setText("")
            
            if duree and mensu:
                if self.test_limite_duree_input(duree) and self.test_limite_mensu_input(mensu):
                    mensu = float(mensu)
                    duree = int(duree)
                    montant = round(self.credit_service.montant_from_mensu_duree(duree_mois=duree, mensualite=mensu, taux_annuel_pct = banque.taux_credit_pct, duree_differe_mois=ddiff_mois),2)
                    self.montant_input.setText(str(montant))
                else: 
                    self.montant_input.setText("")
                    self.duree_credit_msg.setText("Saisie incorrect.")

            
        elif type_actif == self.montant_duree: 
            duree = self.duree_credit_input.text().strip()
            montant = self.montant_input.text().strip()
            mensu = ""

            self.mensualite_msg.setText("")
            
            if duree and montant:
                if self.test_limite_duree_input(duree) and self.test_limite_montant_input(montant):
                    montant = float(montant)
                    duree = int(duree)
                    mensu = round(self.credit_service.mensu_from_montant_duree(montant, duree, banque.taux_credit_pct, ddiff_mois),2)
                    
                    self.mensualite_input.setText(str(mensu))
                else: 
                    self.mensualite_input.setText("")
                    self.duree_credit_msg.setText("Saisie incorrect.")

        elif type_actif == self.montant_mensualite:
            mensu = self.mensualite_input.text().strip()
            montant = self.montant_input.text().strip()
            duree = ""

            self.duree_credit_msg.setText("")
            
            if mensu and montant:
                if self.test_limite_mensu_input(mensu) and self.test_limite_montant_input(montant):
                    montant = float(montant)
                    mensu = int(mensu)
                    try:
                        duree = int(self.credit_service.duree_from_montant_mensu(montant, mensu, banque.taux_credit_pct, ddiff_mois))
                        self.duree_credit_input.setText(str(duree))
                        

                    except ValueError as e:
                        self.duree_credit_msg.setText(str(e))
                else: 
                    self.duree_credit_input.setText("")
                    self.duree_credit_msg.setText("Saisie incorrect.")
        
        if mensu and montant and duree:
            total = round(mensu*duree,2)
            interets = round(total - montant,2)
            
            total = euro(total)
            interets = euro(interets)
            montant = euro(montant)
            
            montant_item = QTableWidgetItem(f"{montant}")
            interets_item = QTableWidgetItem(f"{interets}")
            total_item = QTableWidgetItem(f"{total}")
            
            self.recap_tab.setItem(0,0,montant_item)
            self.recap_tab.setItem(0,1,interets_item)
            self.recap_tab.setItem(0,2,total_item)
        else:
            self.recap_tab.clearContents()       
                 
    def update_type(self, type):
        data = self.type_list.currentData()
        if data is not None:
            self.montant_widget.show()
            self.duree_credit_wgt.show()
            self.mensualite_wgt.show()  
            
            if data == self.montant_mensualite:
                self.duree_credit_input.setEnabled(False)
                self.montant_input.setEnabled(True)
                self.mensualite_input.setEnabled(True)
            elif data ==self.mensualite_duree:
                self.duree_credit_input.setEnabled(True)
                self.montant_input.setEnabled(False)
                self.mensualite_input.setEnabled(True)
            elif data == self.montant_duree:
                self.duree_credit_input.setEnabled(True)
                self.montant_input.setEnabled(True)
                self.mensualite_input.setEnabled(False)
            else:
                self.montant_widget.hide()
                self.duree_credit_wgt.hide()
                self.mensualite_wgt.hide()             
        else:
            self.montant_widget.hide()
            self.duree_credit_wgt.hide()
            self.mensualite_wgt.hide()    
            
    def update_choix(self, index):
        banque_name = self.banque_choix.currentText().strip()
        banque = self.banque_service.get_banque_by_name(banque_name)
        filtre = {"ID USER" : self.session.current_user.id, "ID SCENARIO" : self.scenario_service.scenario_actif.id, "ID BANQUE" : banque.id}
        comptes = self.cb_service.all_userCB_from_(filtre)
        self.compte_bancaire_choix.clear()
        self.compte_bancaire_choix.addItem("")
        for compte in comptes:
            self.compte_bancaire_choix.addItem(compte.type, compte.id) 
        self.taux_interet.setText(f"Taux d'intérêt : {banque.taux_credit_pct} %")
        
    def enregistrer_clicked(self):
        credit = self.credit_service.credit_actif
        
        banque = self.banque_service.get_banque_by_id(self.banque_choix.currentData())
        
        compte_choix = self.compte_bancaire_choix.currentData()
        montant = self.montant_input.text().strip()
        mensu = self.mensualite_input.text().strip()
        duree_credit = self.duree_credit_input.text().strip()
        duree_differee = self.duree_differee_input.text().strip() 
        mois_debut_credit = self.debut_credit_input.text().strip()
        if credit is None:
            id = None
            id_depense = None
            banque_id = None if not(banque) else banque.id
            compte_choix = None if not(compte_choix) else compte_choix
            montant = None if not(montant) else float(montant)
            duree_credit = None if not(duree_credit)  else int(duree_credit)
            mensu = None if not(mensu) else float(mensu)
            duree_differee = 0 if not(duree_differee) else int(duree_differee)
            mois_debut_credit = None if not(mois_debut_credit) else int(mois_debut_credit)
            taux_interet = None if not(banque) else banque.taux_credit_pct
            
        else:
            id = credit.id
            id_depense = credit.id_depense
            banque_id = credit.id_banque if not(banque) else banque.id
            compte_choix = credit.id_compte if not(compte_choix) else int(compte_choix)
            montant = credit.montant if not(montant) else float(montant)
            duree_credit = credit.durée_crédit_mois if not(duree_credit) else int(duree_credit)
            mensu = credit.mensualite_constante if not(mensu) else float(mensu)
            duree_differee = credit.duree_diff_mois if not(duree_differee) else int(duree_differee)
            mois_debut_credit = credit.debut if not(mois_debut_credit) else int(mois_debut_credit)
            
            if banque:
                taux_interet = float(banque.taux_credit_pct or 0)
            else:
                banque = self.banque_service.get_banque_by_id(credit.id_banque)
                taux_interet = banque.taux_credit_pct

        if (compte_choix is None 
            or montant is None 
            or taux_interet is None  
            or duree_credit is None
            or mensu is None
            or mois_debut_credit is None) :
            raise ValueError("Vous devez tout renseigner.")
        else:
            data = {}
            data_depense = {}

            
            data["ID COMPTE"] = data_depense["ID COMPTE"] =compte_choix
            data["ID USER"] = data_depense["ID USER"] =self.session.current_user.id
            data["ID SCENARIO"] =data_depense["ID SCENARIO"] =  self.scenario_service.scenario_actif.id
            data["MENSUALITE (€)"] = data_depense["MONTANT"]=mensu            
            data["DATE OUT"] = data_depense["DATE OUT"] = mois_debut_credit + duree_differee -1 + duree_credit -1
            data_depense["DATE IN"] = mois_debut_credit + duree_differee -1
            
            data["ID BANQUE"] = banque_id
            data["DATE IN"]  = mois_debut_credit
            data["DUREE DIFF (MOIS)"] = duree_differee
            data["DUREE (MOIS)"] = duree_credit
            data["TYPE"]     = 'Mensualité Constante'
            data["TAUX (%)"] = taux_interet
            data["MONTANT"] = montant
            
            data_depense["INTITULE"] = f"crédit {duree_differee + duree_credit} mois {euro(montant)}"
            data_depense["NATURE"] = "Crédit"
            data_depense["FREQUENCE"] = "Mensuel"
            
            credit = self.credit_service.update_credit(id ,data)
            depense_credit = self.depense_service.update_depense(id_depense, data_depense)
            
            self.back_to_hub.emit()

    def load(self):
        self.scenario_label.setText(f'Scénario : {self.scenario_service.scenario_actif.intitule}')
        
        self.capa_mensu = self.credit_service.capacite_emprunt(self.scenario_service.scenario_actif.id)
        
        if self.capa_mensu <= 0:
            self.info_widget.hide()
            self.capacite_emprunt.setText(f"Votre capacité actuelle ne vous permet pas d'emprunter. Capacité d'emprunt : {self.capa_mensu:.2f} €")
            self.mlayout.addStretch()
        else:
            self.info_widget.show()
            self.capacite_emprunt.setText(f"Capacité maximum d'emprunt : {self.capa_mensu:.2f} €")
            
        self.banque_choix.clear()
        self.banque_choix.addItem("")
        for banque in self.banque_service.get_all_banques():
            self.banque_choix.addItem(banque.nom, banque.id)

        self.taux_interet.setText("Taux d'intérêt : ")
        self.compte_bancaire_choix.clear()
        
        self.type_list.setCurrentIndex(0)
        
        self.montant_input.setText("")
        self.mensualite_input.setText("")
        self.duree_credit_input.setText("")
        self.duree_differee_input.setText("")
        
        self.mensualite_wgt.hide()
        self.montant_widget.hide()
        self.duree_credit_wgt.hide()
        
        self.mlayout.addStretch()
        
        
