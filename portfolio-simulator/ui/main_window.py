from PySide6.QtWidgets import QLabel, QComboBox, QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget
import sys

# Import des pages
from ui.sous_pages import AccueilPage, ParametresPage
from ui.sous_pages.banque import BanquePage
from services import AuthService, ProfileService
from .sous_pages.Profil.gestion import AddScenarioPage
from repositories.userRepository import UserRepository
from session import Session
from ui.sous_pages.Auth import AuthPage
from ui.sous_pages.Profil import ProfilPage
from services import AppContext, Page
from services.navigator_service import Page

class MainWindow(QMainWindow):
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.session         = session
        self.appContext      = appContext
        self.scenario_service = appContext.scenario_service
        self.navigator = appContext.navigator
        
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
        
        self.scenario_wgt = QWidget()
        self.scenario_lyt = QHBoxLayout(self.scenario_wgt)
        self.scenario_lbl = QLabel("scenario : ")
        self.scenario_choix = QComboBox()
        self.scenario_choix.currentIndexChanged.connect(self.update_scenario)
        
        self.add_scenario_btn = QPushButton("Ajouter")
        self.edit_scenario_btn = QPushButton("Modifier")
        self.edit_scenario_btn.hide()
        self.scenario_lyt.addWidget(self.scenario_lbl)
        self.scenario_lyt.addWidget(self.scenario_choix)
        self.scenario_lyt.addWidget(self.add_scenario_btn)
        self.scenario_lyt.addWidget(self.edit_scenario_btn)
        
        self.btn_logout = QPushButton("Déconnexion")
        
        sidebar_layout.addWidget(btn_accueil)
        sidebar_layout.addWidget(btn_params)
        sidebar_layout.addWidget(btn_profil)
        sidebar_layout.addWidget(self.btn_banque)
        sidebar_layout.addWidget(self.scenario_wgt)
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
        self.add_scenario_page = AddScenarioPage(appContext, session)
        
        self.stack = QStackedWidget()
        self.stack.addWidget(self.accueil_page)   # index 0
        self.stack.addWidget(self.parametre_page) # index 1
        self.stack.addWidget(self.profil_page)    # index 2
        self.stack.addWidget(self.banque_page)    # index 3
        self.stack.addWidget(self.auth_page)      # index 4
        self.stack.addWidget(self.add_scenario_page) # index 5

        self.my_pages = {
            Page.ACCUEIL : self.accueil_page,
            Page.PARAMETRES : self.parametre_page,
            Page.PROFIL : self.profil_page,
            Page.BANQUE_STANDALONE : self.banque_page,
            Page.AUTH : self.auth_page,
            Page.ADD_SCENARIO : self.add_scenario_page
        }
        
        # Connecter les boutons à la navigation
        btn_accueil.clicked.connect(lambda: self.navigator.go_to(Page.ACCUEIL))
        btn_params.clicked.connect(lambda: self.navigator.go_to(Page.PARAMETRES))
        btn_profil.clicked.connect(self.btn_profil_clicked)
        self.btn_banque.clicked.connect(lambda: self.navigator.go_to(Page.BANQUE_STANDALONE))
        self.add_scenario_btn.clicked.connect(lambda : self.navigator.go_to(Page.ADD_SCENARIO))
        self.edit_scenario_btn.clicked.connect(lambda : self.navigator.go_to(Page.ADD_SCENARIO))
        self.btn_logout.clicked.connect(self.on_logout)
        
        main_layout.addWidget(sidebar_widget, 1)
        main_layout.addWidget(self.stack,5)
        
        self.auth_page.auth_success.connect(self.on_auth_success)
        
        self.appContext.navigator.navigation_requested.connect(self.handle_navigation)
        
    def handle_navigation(self, page_key, context):
        if page_key not in self.my_pages:
            return
        page = self.my_pages[page_key]
        self.stack.setCurrentWidget(page)
        if context and hasattr(page, "set_context"):
            page.set_context(context)
        if hasattr(page, "load"):
            page.load()    
            
    def on_auth_success(self, user):
        self.session.login(user) 
        if user.id == 1000000000:
            self.btn_banque.show()
        self.navigator.go_to(Page.PROFIL)  
        self.btn_logout.show()
        self.load()
        
    def btn_profil_clicked(self):
        if self.session.is_authenticated():               #Utilisateur connecté donc page profil
            user = self.session.current_user
            self.navigator.go_to(Page.PROFIL)
           
        else:                                             #Personne de connecté donc page d'authentification
            self.navigator.go_to(Page.AUTH)
        
            
    def on_logout(self):
        self.session.logout()
        self.navigator.go_to(Page.AUTH)
        self.btn_logout.hide()
        self.btn_banque.hide()
        self.load()

    def add_scenario_clicked(self):
        self.scenario_service.set_scenario_actif(None)
        self.navigator.go_to(Page.ADD_SCENARIO)

    def update_scenario(self):
        scenario = self.scenario_service.get_scenario_by_id(self.scenario_choix.currentData())
        print(scenario)
        if scenario:
            self.scenario_service.set_scenario_actif(scenario.id)
            self.edit_scenario_btn.show()
        else : 
            self.scenario_service.set_scenario_actif(None)
            self.edit_scenario_btn.hide()
            
        self.profil_page.load_current_page()
        self.navigator.reload()

        
    
    def load(self):
        self.scenario_choix.clear()
        self.scenario_choix.addItem("")
        
        scenarios = self.scenario_service.get_all_scenario_from_user(self.session.current_user.id) or []
        for scenario in scenarios:
            self.scenario_choix.addItem(scenario.intitule, scenario.id)
        
        