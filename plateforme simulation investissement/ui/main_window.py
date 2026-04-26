from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget
import sys

# Import des pages
from ui.sous_pages import AccueilPage, ParametresPage
from ui.sous_pages.banque import BanquePage
from services import AuthService, ProfileService
from repositories.userRepository import UserRepository
from session import Session
from ui.sous_pages.Auth import AuthPage
from ui.sous_pages.Profil import ProfilPage
from services import AppContext

class MainWindow(QMainWindow):
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.session         = session
        self.appContext      = appContext
        self.profil_service  = appContext.profile_Service
        self.auth_service    = appContext.auth_service
        
        self.setWindowTitle("PySide6 - Multi pages")

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Layout principal : sidebar + contenu
        
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)

        # --- Sidebar ---
        sidebar_widget = QWidget()
        sidebar_widget.setObjectName("Sidebar")
        sidebar_layout = QVBoxLayout(sidebar_widget)
        
        btn_accueil = QPushButton("Accueil")
        btn_params = QPushButton("Paramètres")
        btn_profil = QPushButton("Profil")
        self.btn_banque = QPushButton("Banque")
        self.btn_logout = QPushButton("Déconnexion")
        
        sidebar_layout.addWidget(btn_accueil)
        sidebar_layout.addWidget(btn_params)
        sidebar_layout.addWidget(btn_profil)
        sidebar_layout.addWidget(self.btn_banque)
        self.btn_banque.hide()
        
        sidebar_layout.addStretch()  # pousse les boutons en haut
        
        sidebar_layout.addWidget(self.btn_logout)
        self.btn_logout.hide()
        # --- Zone de contenu ---
        self.accueil_page = AccueilPage()
        self.parametre_page = ParametresPage()
        self.profil_page = ProfilPage(appContext=self.appContext, session=self.session)
        self.auth_page = AuthPage(appContext=self.appContext, session=self.session)
        self.banque_page = BanquePage(appContext =self.appContext, session= self.session)
        
        self.stack = QStackedWidget()
        self.stack.addWidget(self.accueil_page)   # index 0
        self.stack.addWidget(self.parametre_page) # index 1
        self.stack.addWidget(self.profil_page)    # index 2
        self.stack.addWidget(self.banque_page)    # index 3
        self.stack.addWidget(self.auth_page)      # index 4

        # Connecter les boutons à la navigation
        btn_accueil.clicked.connect(lambda: self.load_index(0))
        btn_params.clicked.connect(lambda: self.load_index(1))
        btn_profil.clicked.connect(self.btn_profil_clicked)
        self.btn_banque.clicked.connect(lambda: self.load_index(3))
        self.btn_logout.clicked.connect(self.on_logout)
        
        main_layout.addWidget(sidebar_widget, 1)
        main_layout.addWidget(self.stack,5)
        
        self.auth_page.auth_success.connect(self.on_auth_success)
        
    def on_auth_success(self, user):
        self.session.login(user) 
        if user.id == 1000000000:
            self.btn_banque.show()
        self.profil_page.load_by_index(0)          # rafraîchit l’UI du profil
        self.stack.setCurrentWidget(self.profil_page)  
        self.btn_logout.show()
        
    def btn_profil_clicked(self):
        if self.session.is_authenticated():               #Utilisateur connecté donc page profil
            user = self.session.current_user
            self.profil_page.load_by_index(0)
            self.stack.setCurrentWidget(self.profil_page)
        else:                                             #Personne de connecté donc page d'authentification
            self.stack.setCurrentWidget(self.auth_page)
            
    def on_logout(self):
        self.session.logout()
        self.stack.setCurrentWidget(self.auth_page)
        self.btn_logout.hide()
        self.btn_banque.hide()

    def load_index(self, index):
        self.stack.setCurrentIndex(index)
        page=  self.stack.currentWidget()
        if hasattr(page, "load"):
            page.load()