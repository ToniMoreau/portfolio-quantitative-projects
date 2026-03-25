from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QStackedWidget, QSizePolicy
)

from session import Session
from .dashboard import DashboardPage
from .gestion_projets import ProjectsPage
from .visualisation_page import VisualisationPage
from.gestion.infos_hub_page import InfoHubPage
from .outils.outils_page import OutilsPage

from services import AppContext

class ProfilPage(QWidget):
    logout_success = Signal()
    
    
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.appContext = appContext
        self.session = session

        # --- Layout principal ---
        layout = QVBoxLayout(self)
        
        sidebar_widget = QWidget()
        sidebar_widget.setObjectName("Sidebar")
        sidebar_layout = QHBoxLayout(sidebar_widget)
        
        self.dashboard_btn = QPushButton("Dashboard")
        self.outils_btn = QPushButton("Outils")
        self.infos_btn = QPushButton("Gestion")
        self.gestion_btn = QPushButton("Projets")
        self.visualisation_btn = QPushButton("Visualisation")

        sidebar_layout.addWidget(self.dashboard_btn)
        sidebar_layout.addWidget(self.outils_btn)
        sidebar_layout.addWidget(self.infos_btn)
        sidebar_layout.addWidget(self.gestion_btn)
        sidebar_layout.addWidget(self.visualisation_btn)

        self.dashboard_page = DashboardPage(self.appContext, self.session)
        self.outils_page = OutilsPage(self.appContext, self.session)
        self.infos_page = InfoHubPage(self.appContext, self.session)
        self.gestion_projet = ProjectsPage()
        self.visualisation_page = VisualisationPage()
        
        #Gestion de la pile de pages
        self.stack = QStackedWidget()
        self.stack.addWidget(self.dashboard_page) #index 0
        self.stack.addWidget(self.outils_page) #index 1
        self.stack.addWidget(self.infos_page) #index 2
        self.stack.addWidget(self.gestion_projet) #index 3
        self.stack.addWidget(self.visualisation_page) #index 4   
        
        layout.addWidget(sidebar_widget, 1)
        layout.addWidget(self.stack, 7)
        
        #Actions boutons
        self.dashboard_btn.clicked.connect(lambda : self.load_by_index(0))
        self.outils_btn.clicked.connect(lambda : self.load_by_index(1))
        self.infos_btn.clicked.connect(lambda : self.load_by_index(2))
        self.gestion_btn.clicked.connect(lambda : self.load_by_index(3))
        self.visualisation_btn.clicked.connect(lambda : self.load_by_index(4))
                
        self.stack.setCurrentIndex(0)

    def load_by_index(self, index):
        self.stack.setCurrentIndex(index)
        page =self.stack.widget(index)
        
        if hasattr(page, "load"):
            page.load()
            
            

        

