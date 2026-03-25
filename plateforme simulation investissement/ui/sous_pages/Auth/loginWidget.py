from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QStackedWidget, QSizePolicy
)

from services import AppContext
from session import Session
    
class LoginWidget(QWidget):
    auth_success = Signal(object)
    auth_error = Signal(str)

    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.auth_service = appContext.auth_service
        self.session = session

        layout = QVBoxLayout(self)
        
        self.login_name = QLineEdit()
        self.login_name.setPlaceholderText("Nom d’utilisateur")
        self.login_pw = QLineEdit()
        self.login_pw.setPlaceholderText("Mot de passe")
        login_btn = QPushButton("Se connecter")
        self.login_error_label = QLabel('Erreur')
        self.login_error_label.hide()
        self.login_error_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.switch_to_register = QPushButton("Créer un profil")
        
        login_btn.clicked.connect(self.login_clicked)    
            
        layout.addWidget(QLabel("Connexion"))
        layout.addWidget(self.login_name)
        layout.addWidget(self.login_pw)
        layout.addWidget(login_btn)
        layout.addWidget(self.login_error_label)
        layout.addWidget(self.switch_to_register)
        
    def login_clicked(self):
        username = self.login_name.text().strip()
        password = self.login_pw.text().strip()
        
        try:
            print("try")
            user = self.auth_service.login(
                username,
                password
            )
            
            self.auth_success.emit(user)
        except Exception as e:
            self.login_error_label.show()
            self.login_error_label.setText(str(e))
            self.auth_error.emit(str(e))        
            raise e
            