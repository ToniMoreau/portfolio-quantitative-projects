from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QStackedWidget, QSizePolicy
)
from services import AppContext
from session import Session
class RegisterWidget(QWidget):
    auth_success = Signal(object)
    auth_error = Signal(str)
    
    
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.auth_service = appContext.auth_service
        self.session = session
        
        layout = QVBoxLayout(self)
        
        self.signup_username = QLineEdit()
        self.signup_username.setPlaceholderText("Entrer un nom d'utilisateur")
        self.signup_pw = QLineEdit()
        self.signup_pw.setPlaceholderText("Entrer un mot de passe")
        self.signup_lname = QLineEdit()
        self.signup_lname.setPlaceholderText("Entrer un nom")
        self.signup_fname = QLineEdit()
        self.signup_fname.setPlaceholderText("Entrer un prénom")
        self.signup_age = QLineEdit()
        self.signup_age.setPlaceholderText("Age")
        suivant_btn = QPushButton("Créer")
        self.signup_error = QLabel("")
        self.switch_to_login = QPushButton("← Retour à la connexion")
        
        suivant_btn.clicked.connect(self.create_clicked)
        
        layout.addWidget(QLabel("Création de profil"))
        layout.addWidget(self.signup_username)
        layout.addWidget(self.signup_pw)
        layout.addWidget(self.signup_lname)
        layout.addWidget(self.signup_fname)
        layout.addWidget(self.signup_age)
        layout.addWidget(suivant_btn)
        layout.addWidget(self.signup_error)
        layout.addWidget(self.switch_to_login)        
        
    def create_clicked(self):
        username = self.signup_username.text().strip()
        password = self.signup_pw.text().strip()
        print(username, password)
        try:
            user = self.auth_service.register(
                username, 
                password)
            
            self.auth_success.emit(user)
        except Exception as e:
            self.signup_error.setText(str(e))
            self.auth_error.emit(str(e))