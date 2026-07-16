from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,  QLabel, QPushButton, QLineEdit, QStackedWidget, QSizePolicy
)

from session import Session
from services import AppContext
from utils.finance_format import euro,percent

class CalculImpotsPage(QWidget):
    back_to_outils = Signal()
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        
        self.fisca_service = appContext.fisca_service
        self.metier_service = appContext.metier_service
        self.scenario_service = appContext.scenario_service
        self.session = session
        
        layout = QVBoxLayout(self)
        
        title = QLabel("Calculateur d'impots")
        
        annuel_brut_label = QLabel("Revenu annuel brut (€)")
        self.annuel_brut = QLabel("")

        annuel_net_label = QLabel("Revenu annuel net (€)")
        self.annuel_net = QLabel("")
        
        calcul_btn = QPushButton("Calculer Imposition")
        self.resultat_label = QLabel("")
        
        self.retour_btn = QPushButton("Retour")
        
        calcul_btn.clicked.connect(lambda : self.calcul_impot_clicked(self.net_imposable))
        self.retour_btn.clicked.connect(self.retour_clicked)
        
        layout.addWidget(title)
        layout.addWidget(annuel_brut_label)
        layout.addWidget(self.annuel_brut)
        layout.addWidget(annuel_net_label)
        layout.addWidget(self.annuel_net)
        layout.addWidget(calcul_btn)
        layout.addWidget(self.resultat_label)
        layout.addStretch()
        
        layout.addWidget(self.retour_btn)
        
        
    def retour_clicked(self):
        self.resultat_label.setText("")
        self.back_to_outils.emit()
        
    def load(self):
        profils_pro = self.metier_service.get_metier_by_scenario(self.scenario_service.scenario_actif.id) or []
        self.net_imposable =0
        brut = 0
        for profil_pro in profils_pro:
            brut += profil_pro.annuel_brut
            self.net_imposable += profil_pro.annuel_net
                
        self.annuel_brut.setText(f"{euro(brut)}")
        self.annuel_net.setText(f"{euro(self.net_imposable)}")
    
    def calcul_impot_clicked(self, revenu):
        resultat = self.fisca_service.imposition_salaire(revenu)
        prvmt_source = resultat *100/ float(self.net_imposable)
        self.resultat_label.setText(f"Estimation Imposition : {euro(resultat)}, ({percent(prvmt_source)})")
        
        
        
        
        