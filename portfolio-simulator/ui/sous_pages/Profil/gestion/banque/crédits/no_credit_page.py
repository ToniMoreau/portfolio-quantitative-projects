#flattened


from PySide6.QtWidgets import QTableWidget, QTableWidgetItem,QComboBox, QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel, QLineEdit
from PySide6.QtCore import Signal
from PySide6.QtGui import QIntValidator,QDoubleValidator
from utils.finance_format import euro
from utils.date import add_months
from services import AppContext, Page
from session import Session
from datetime import date, timedelta

class NoCreditPage(QWidget):    
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.banque_service = appContext.banque_service
        self.credit_service = appContext.credit_service
        self.depense_service = appContext.depense_service
        self.recette_service = appContext.recette_service
        self.cb_service = appContext.cb_service
        self.session = session
        self.scenario_service = appContext.scenario_service
        self.navigator = appContext.navigator
        self.invest_service = appContext.invest_service
                    
        layout = QVBoxLayout(self)
        
        self.scenario_label = QLabel(f"")
        self.title_label = QLabel("Contraction du crédit")
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
        self.taux_interet_lbl = QLabel("Taux d'intérêt (%) : ")
        self.taux_interet_pct_input = QLineEdit("")
        self.taux_interet_pct_input.setPlaceholderText("%")
        self.taux_interet_pct_input.setValidator(QDoubleValidator(0.,100.,2))
        self.taux_interet_pct_input.editingFinished.connect(lambda: self.capabilité_emprunt(self.taux_interet_pct_input))
        self.taux_interet_pct_input.editingFinished.connect(self.update_variables)
        
        banque_layout.addWidget(self.banque_choix,2)
        banque_layout.addWidget(self.taux_interet_lbl,1)
        banque_layout.addWidget(self.taux_interet_pct_input,1)
        
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
        self.montant_duree = ["MONTANT", "DUREE (MOIS)"]
        
        self.type_list.addItem("Montant + Mensualité ", self.montant_mensualite)
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
        self.montant_input = QLabel()

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
        self.debut_credit_lbl = QLabel("Début au")
        self.debut_date_lbl = QLabel()
        self.debut_date_lbl.setFixedWidth(60)
        
        self.etendu_lyt.addWidget(self.debut_credit_lbl)
        self.etendu_lyt.addWidget(self.debut_date_lbl)
        self.etendu_lyt.addStretch()
        
        self.recap_tab = QTableWidget()
        self.recap_tab.setColumnCount(3)
        self.recap_tab.setRowCount(1)
        self.recap_tab.setHorizontalHeaderLabels(["Crédit", "Coût", "Total"])
        self.recap_tab.setMaximumWidth(500)
        
        layout.addWidget(self.scenario_label)
        layout.addWidget(self.etendu_wgt)
        layout.addWidget(self.capacite_emprunt)
        
        layout.addWidget(self.info_widget)
        
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
        self.reload_btn = QPushButton("Reload o")
        self.reload_btn.hide()
        
        info_layout.addWidget(self.enregistrer_btn)
        layout.addWidget(self.annuler_btn)
        layout.addWidget(self.reload_btn)

        #actions boutons
        self.annuler_btn.clicked.connect(lambda : self.navigator.go_to(Page.INVESTISSEMENT_HUB))
        self.enregistrer_btn.clicked.connect(self.enregistrer_clicked)
        self.enregistrer_btn.setEnabled(False)
        self.reload_btn.clicked.connect(self.load)
                 
    def on_change(self):
        ok = (
            self.banque_choix.currentText() is not None
            and self.compte_bancaire_choix.currentText() is not None
            and self.type_list.currentText() is not None
            and self.test_limite_mensu_input(self.mensualite_input.text().strip())
            and self.test_limite_duree_input(self.duree_credit_input.text().strip())
        )
        ok = ok or (self.credit_service.credit_actif is not None)

        self.enregistrer_btn.setEnabled(ok) 

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
    
    def test_limite_duree_input(self,duree : str):
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
        invest_id = self.invest_service.invest_actif_id
        invest = self.invest_service.get_by_id(invest_id)
        taux_emprunt = self.taux_interet_pct_input.text().strip()
        if taux_emprunt:
            taux_emprunt_pct = float(taux_emprunt)
            
            type_actif = self.type_list.currentData()
            ddiff_mois = self.duree_differee_input.text().strip()
            if self.test_limite_ddiff_input(ddiff_mois):
                ddiff_mois = int(ddiff_mois)
            else:
                ddiff_mois = 0
            mensu = None
            montant = None
            duree = None
                
            if type_actif == self.montant_duree: 
                duree = self.duree_credit_input.text().strip()
                montant = invest.prix_achat*(1-invest.comptant_pct)
                mensu = ""

                self.mensualite_msg.setText("")
                
                if duree and montant:
                    if self.test_limite_duree_input(duree):
                        montant = float(montant)
                        duree = int(duree)
                        mensu = round(self.credit_service.mensu_from_montant_duree(montant, duree, taux_emprunt_pct, ddiff_mois),2)
                        
                        self.mensualite_input.setText(str(mensu))
                    else: 
                        self.mensualite_input.setText("")
                        self.duree_credit_msg.setText("Saisie incorrect.")

            elif type_actif == self.montant_mensualite:
                mensu = self.mensualite_input.text().strip()
                montant = invest.prix_achat*(1-invest.comptant_pct)
                duree = ""

                self.duree_credit_msg.setText("")
                
                if mensu and montant:
                    if self.test_limite_mensu_input(mensu):
                        montant = float(montant)
                        mensu = int(mensu)
                        try:
                            duree = int(self.credit_service.duree_from_montant_mensu(montant, mensu, taux_emprunt_pct, ddiff_mois))
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

    def update_capa_emprunt(self):
        try:
            date_credit = date(int(self.debut_year_input.text().strip()), int(self.debut_date_lbl.text().strip()), 1)
            self.capa_mensu = self.credit_service.capacite_emprunt(self.scenario_service.scenario_actif.id, date_credit)
            
            self.capacite_emprunt.setText(f"Capacité maximum d'emprunt : {euro(self.capa_mensu)}")
            
            if self.capa_mensu <= 0:
                self.info_widget.hide()
                self.capacite_emprunt.setText(f"Votre capacité actuelle ne vous permet pas d'emprunter. Capacité d'emprunt : {self.capa_mensu:.2f} €")
            else:
                self.info_widget.show()
                self.capacite_emprunt.setText(f"Capacité maximum d'emprunt : {self.capa_mensu:.2f} €")

        except:
            pass
    
    def update_choix(self, index):
        banque_name = self.banque_choix.currentText().strip()
        banque = self.banque_service.get_banque_by_name(banque_name)
        filtre = {"ID USER" : self.session.current_user.id, "ID SCENARIO" : self.scenario_service.scenario_actif.id, "ID BANQUE" : banque.id}
        comptes = self.cb_service.all_userCB_from_(filtre)
        self.compte_bancaire_choix.clear()
        self.compte_bancaire_choix.addItem("")
        for compte in comptes:
            self.compte_bancaire_choix.addItem(compte.type, compte.id) 
    
    def capabilité_emprunt(self, taux : QLineEdit):
        taux_pct = taux.text().strip()
        if taux_pct:
            taux_pct = float(taux_pct)
            invest = self.invest_service.invest_actif()
            if invest is not None:
                credit_montant = invest.prix_achat*(1-invest.comptant_pct)
                if self.capa_mensu <= self.credit_service.mensu_from_montant_duree(credit_montant, 360, taux_pct,0):
                    self.info_widget.hide()
                    self.capacite_emprunt.setText(f"Votre capacité actuelle ne vous permet pas d'emprunter. Capacité d'emprunt : {self.capa_mensu:.2f} €")
                    self.reload_btn.show()
                else:
                    self.info_widget.show()
                    self.capacite_emprunt.setText(f"Capacité maximum d'emprunt : {self.capa_mensu:.2f} €")
                    
        else:
            self.info_widget.show()
            
    def enregistrer_clicked(self):
            credit = self.credit_service.credit_actif
            invest_id = self.invest_service.invest_actif_id
            invest = self.invest_service.get_by_id(invest_id)
            
            banque = self.banque_service.get_banque_by_id(self.banque_choix.currentData())
            
            compte_choix = self.compte_bancaire_choix.currentData()
            montant = invest.prix_achat*(1-invest.comptant_pct)
            mensu = self.mensualite_input.text().strip()
            duree_credit = self.duree_credit_input.text().strip()
            duree_differee = self.duree_differee_input.text().strip() 
            taux_emprunt_pct = self.taux_interet_pct_input.text().strip()
                        
            if credit is None:
                id = None
                id_depense = None
                id_recette = None
                banque_id = None if not(banque) else banque.id
                compte_choix = None if not(compte_choix) else compte_choix
                montant = None if not(montant) else float(montant)
                duree_credit = None if not(duree_credit)  else int(duree_credit)
                mensu = None if not(mensu) else float(mensu)
                duree_differee = 0 if not(duree_differee) else int(duree_differee)
                            
                date_in = None if not(invest.date_in) else invest.date_in
                taux_emprunt_pct = None if not(taux_emprunt_pct) else float(taux_emprunt_pct)
                
            else:
                id = credit.id
                id_depense = credit.id_depense
                id_recette = credit.id_recette
                banque_id = credit.id_banque if not(banque) else banque.id
                compte_choix = credit.id_compte if not(compte_choix) else int(compte_choix)
                montant = credit.montant if not(montant) else float(montant)
                duree_credit = credit.durée_crédit_mois if not(duree_credit) else int(duree_credit)
                mensu = credit.mensualite_constante if not(mensu) else float(mensu)
                duree_differee = credit.duree_diff_mois if not(duree_differee) else int(duree_differee)
                
                date_in = credit.debut if not(invest.date_in) else invest.date_in
                
                taux_emprunt_pct =credit.taux_crédit_pct if not(taux_emprunt_pct) else float(taux_emprunt_pct)    
                         
            date_out = None if not(date_in) else add_months(date_in, duree_differee + duree_credit)

            if (compte_choix is None 
                or montant is None 
                or taux_emprunt_pct is None  
                or duree_credit is None
                or mensu is None
                or date_in is None) :
                raise ValueError("Vous devez tout renseigner.")
            else:
                
                data = {}
                data_depense = {}
                data_recette = {}

                data["ID COMPTE"] = data_depense["ID COMPTE"] = data_recette["ID COMPTE"] = compte_choix
                data["ID USER"] = data_depense["ID USER"] = data_recette["ID USER"]= self.session.current_user.id
                data["ID SCENARIO"] =data_depense["ID SCENARIO"] =data_recette["ID SCENARIO"]=  self.scenario_service.scenario_actif.id
                data["ID INVEST"] = invest_id
                
                data["MENSUALITE (€)"] = data_depense["MONTANT"]=mensu            
                data["DATE OUT"] = data_depense["DATE OUT"] = date_out
                data_depense["DATE IN"] = add_months(date_in, duree_differee)
                
                data["ID BANQUE"] = banque_id
                data["DATE IN"]  = data_recette["DATE IN"]= data_recette["DATE OUT"] = date_in
                data["DUREE DIFF (MOIS)"] = duree_differee
                data["DUREE (MOIS)"] = duree_credit
                data["TYPE"]     = 'Mensualité Constante'
                data["TAUX (%)"] = taux_emprunt_pct
                data["MONTANT"] = data_recette["MONTANT"]= montant
                
                data_depense["INTITULE"] = data_recette["INTITULE"]=f"crédit {duree_differee + duree_credit} mois {euro(montant)}"
                data_depense["NATURE"] =data_recette["NATURE"]= "Crédit"
                data_depense["FREQUENCE"] = "Mensuel"
                data_recette["FREQUENCE"]= "Ponctuel"
                
                depense_credit = self.depense_service.update_depense(id_depense, data_depense)
                recette_credit = self.recette_service.update_recette(id_recette, data_recette)
                
                data["ID RECETTE"] = recette_credit.id
                data["ID DEPENSE"] = depense_credit.id
                
                credit = self.credit_service.update_credit(id ,data)
                invest = self.invest_service.update_investissement(invest_id, {"ID CREDIT" : credit.id, "ETAT" : "à conclure"})
                
                self.navigator.go_to(Page.CREDITS)
               
    def load(self):
        self.scenario_label.setText(f'Scénario : {self.scenario_service.scenario_actif.intitule}')
        invest = self.invest_service.get_by_id(self.invest_service.invest_actif_id)
        
        date_credit = date(invest.date_in.year, invest.date_in.month, invest.date_in.day)
        self.capa_mensu = self.credit_service.capacite_emprunt(self.scenario_service.scenario_actif.id, date_credit)
        
            
        self.banque_choix.clear()
        self.banque_choix.addItem("")
        for banque in self.banque_service.get_all_banques():
            self.banque_choix.addItem(banque.nom, banque.id)

        self.compte_bancaire_choix.clear()
        
        self.type_list.setCurrentIndex(0)
        
        self.montant_input.setText(str(euro(invest.prix_achat*(1-invest.comptant_pct))))
        
        date_str = f"{0 if date_credit.month < 10 else""}{date_credit.month}/{date_credit.year}"
        self.debut_date_lbl.setText(date_str)
        
        self.mensualite_input.setText("")
        self.duree_credit_input.setText("")
        self.duree_differee_input.setText("")
        self.taux_interet_pct_input.setText("")
        self.capabilité_emprunt(self.taux_interet_pct_input)
        
        self.mensualite_wgt.hide()
        self.montant_widget.hide()
        self.duree_credit_wgt.hide()
        self.reload_btn.hide()
                
        
