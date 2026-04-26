from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,  QLabel, QPushButton, QLineEdit, QStackedWidget, QSizePolicy
)

from .loginWidget import LoginWidget
from .registerWidget import RegisterWidget

from services import AppContext
from session import Session

class AuthPage(QWidget):
    auth_success = Signal(object)
    auth_error = Signal(str)
    
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        
        self.appContext = appContext
        self.session = session
        
        #Layout Principal
        layout = QVBoxLayout(self)
        self.stack = QStackedWidget() 
        layout.addWidget(self.stack)
        
        #Création sous pages
        self.login_page = LoginWidget(self.appContext, self.session)
        self.register_page = RegisterWidget(self.appContext, self.session)
        
        #Ajout à la pile
        self.stack.addWidget(self.login_page)   #index 0
        self.stack.addWidget(self.register_page)   #index 1
        
        self.login_page.auth_success.connect(self.auth_success.emit)
        self.register_page.auth_success.connect(self.auth_success.emit)
        
        self.register_page.switch_to_login.clicked.connect(lambda: self.stack.setCurrentWidget(self.login_page))
        self.login_page.switch_to_register.clicked.connect(lambda: self.stack.setCurrentWidget(self.register_page))
        
        #Affichage initial
        self.stack.setCurrentIndex(0)
        
        
