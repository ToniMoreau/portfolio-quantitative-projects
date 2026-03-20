from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,  QLabel, QPushButton, QLineEdit, QStackedWidget, QSizePolicy
)

from session import Session
from services import AppContext

class CalculImpotsPage(QWidget):
    back_to_outils = Signal()
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        
        self.fisca_service = appContext.fisca_service
        self.metier_service = appContext.metier_service
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
        
        calcul_btn.clicked.connect(lambda : self.calcul_impot_clicked(float(self.annuel_net.text())))
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
        profil_pro = self.metier_service.get_metier_by_id(self.session.current_user.profil_pro_id)
        
        user_revenu = profil_pro.annuel_brut if profil_pro.annuel_brut else 0
        
        self.annuel_brut.setText(f"{user_revenu}")
        self.annuel_net.setText(f"{profil_pro.annuel_net}")
    
    def calcul_impot_clicked(self, revenu):
        resultat = self.fisca_service.imposition_salaire(revenu)
        prvmt_source = resultat *100/ float(self.annuel_net.text())
        self.resultat_label.setText(f"Estimation Imposition : {round(resultat, 2)} €, ({round(prvmt_source)} %)")
        
        
        
        
        