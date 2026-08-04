
#flattened

from PySide6.QtWidgets import (QHBoxLayout, QVBoxLayout, QWidget, QLabel, QPushButton, QStackedWidget)

from services import AppContext, Page
from session import Session

from .calcul_impot_page import CalculImpotsPage


class OutilsPage(QWidget):
    def __init__(self, appContext : AppContext, session : Session):
        super().__init__()
        self.session = session
        self.navigator = appContext.navigator
        
        layout = QHBoxLayout(self)
        
        outils_widget = QWidget()
        
        sous_layout_names = {"Fiscalité" : {"Calculateur Impôts" : CalculImpotsPage(appContext, session)}}
        
        self.stack = QStackedWidget()
        self.stack.addWidget(outils_widget) # index 0
        
        for category, outils in sous_layout_names.items():
            sous_layout = QHBoxLayout(outils_widget)
            cat_title = QLabel(category) 
            for name, outil_page in outils.items():  
                self.stack.addWidget(outil_page)
                
                outil_btn =  QPushButton(name)
                outil_btn.clicked.connect(lambda checked=False, p=outil_page: self.load_by_name(p))                
                outil_page.back_to_outils.connect(lambda :self.stack.setCurrentIndex(0))
                sous_layout.addWidget(outil_btn)
                
            sous_layout.addWidget(cat_title)
            
        layout.addWidget(self.stack)
        
        self.stack.setCurrentIndex(0)
        
    def load_by_name(self, name):
        self.stack.setCurrentWidget(name)
        
        page = self.stack.currentWidget()
        
        if hasattr(page, "load"):
            page.load()
        
        
        