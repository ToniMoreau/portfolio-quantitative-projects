from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QStackedWidget, QSizePolicy
)


from services import AppContext
from session import Session

class DashboardPage(QWidget):
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.profil_service = appContext.profile_Service
        self.session = session
        layout = QVBoxLayout(self)
        
        #Element de la page
        self.title = QLabel("")
        self.infos = QLabel("")
    
        #Ajouter physiquement à la page
        layout.addWidget(self.title)
        layout.addWidget(self.infos)
        
        
    def load(self):
        user = self.session.current_user
        if user is not None:
            self.title.setText(f"Profil chargé : {user.username}")
            self.infos.setText(self.profil_service.get_infos(user))
        else:
            self.title.setText("Aucun utilisateur connecté")

