from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel
from services import AppContext
from .ajouter_banque_page import AjouterBanquePage

class BanquePage(QWidget):
    def __init__(self, appContext : AppContext, session):
        super().__init__()
        self.banque_service = appContext.banque_service
        
        self.session = session
        
        self.mlayout = QVBoxLayout(self)
        
        self.ajouter_page = AjouterBanquePage(appContext, self.session)
        self.hub = self.hub_page()
        
        self.stack = QStackedWidget()
        self.stack.addWidget(self.hub)
        self.stack.addWidget(self.ajouter_page)
        
        self.mlayout.addWidget(self.stack)
        
        self.stack.setCurrentIndex(0)
        self.ajouter_page.back_to_hub.connect(self.load)
        
    def hub_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        title = QLabel("Banques")
        
        layout.addWidget(title)
        self.btns = []
        for name in self.banque_service.get_all_banque_names():
            btn_banque= QPushButton(name)
            layout.addWidget(btn_banque)
            btn_banque.clicked.connect(lambda : self.btn_banque_clicked(name))
            self.btns.append(btn_banque)
        
        layout.addStretch()
        self.btn_ajouter   = QPushButton("Ajouter une banque")
        self.btn_supprimer = QPushButton("Supprimer cette banque")
        self.btn_modifier  = QPushButton("Modifier cette banque")
        
        layout.addWidget(self.btn_ajouter)
        layout.addWidget(self.btn_supprimer)
        layout.addWidget(self.btn_modifier)
        self.btn_supprimer.hide()
        self.btn_modifier.hide()
        
        self.btn_ajouter.clicked.connect(self.ajouter_clicked)
        self.btn_modifier.clicked.connect(lambda : self.stack.setCurrentIndex(1))
        self.btn_supprimer.clicked.connect(self.supprimer_clicked)

        return page
    
    def btn_banque_clicked(self, name):
        self.btn_supprimer.show()
        self.btn_modifier.show()
        banque = self.banque_service.get_banque_by_name(name)
        self.banque_service.set_banque_active(banque)
        
    def ajouter_clicked(self):
        self.banque_service.set_banque_active()
        self.stack.setCurrentIndex(1)
        
    def supprimer_clicked(self):
        self.banque_service.delete_banque(self.banque_service.banque_active)
        self.load()
        
    def load(self):
        self.mlayout.removeWidget(self.stack)
    
        self.hub = self.hub_page()
        self.stack = QStackedWidget()
        self.stack.addWidget(self.hub)
        self.stack.addWidget(self.ajouter_page)
        
        self.mlayout.addWidget(self.stack)
        self.stack.setCurrentIndex(0)
        
        self.banque_service.set_banque_active()

        