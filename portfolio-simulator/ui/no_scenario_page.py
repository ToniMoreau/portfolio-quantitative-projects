from PySide6.QtWidgets import (
    QLabel, QHBoxLayout, QVBoxLayout, QWidget
)

from services import AppContext
from session import Session

from services import Page
class NoScenarioPage(QWidget):
    def __init__(self, appContext: AppContext, session : Session):
        super().__init__()
        self.appContext = appContext
        self.session = session
        self.navigator = appContext.navigator
        
        self.holding = None
        
        layout = QVBoxLayout(self)
        
        no_scenario_label = QLabel("Veuillez selectionner un scenario pour afficher cette page.")
        
        layout.addWidget(no_scenario_label)
        
        
        
        
        
