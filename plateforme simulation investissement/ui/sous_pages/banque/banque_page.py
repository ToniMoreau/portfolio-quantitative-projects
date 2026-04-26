from PySide6.QtWidgets import QListWidget, QListWidgetItem,QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel
from services import AppContext
from session import Session
from .ajouter_banque_page import AjouterBanquePage

class BanquePage(QWidget):
    def __init__(self, appContext : AppContext, session :Session ):
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
        self.ajouter_page.back_to_hub.connect(lambda : self.load_index(0))
        
    def hub_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        title = QLabel("Banques")
        self.btn_ajouter   = QPushButton("Ajouter une banque")
        
        
        table_wgt = QWidget()
        table_lyt = QVBoxLayout(table_wgt)
        self.banque_table = QListWidget()
        self.banque_table.clicked.connect(self.banque_clicked)
        self.btn_supprimer = QPushButton("Supprimer cette banque")
        self.btn_modifier  = QPushButton("Modifier cette banque")
        self.btn_supprimer.hide()
        self.btn_modifier.hide()
        table_lyt.addWidget(self.btn_ajouter)
        table_lyt.addWidget(self.banque_table)
        table_lyt.addWidget(self.btn_supprimer)
        table_lyt.addWidget(self.btn_modifier)
        
        
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(table_wgt)
        
        self.btn_ajouter.clicked.connect(self.ajouter_clicked)
        self.btn_modifier.clicked.connect(lambda : self.load_index(1))
        self.btn_supprimer.clicked.connect(self.supprimer_clicked)

        return page
    
    def banque_clicked(self):
        self.btn_supprimer.show()
        self.btn_modifier.show()
        banque_id = self.banque_table.currentItem().data(1)
        banque = self.banque_service.get_banque_by_id(banque_id)
        self.banque_service.set_banque_active(banque)
        
    def ajouter_clicked(self):
        self.banque_service.set_banque_active()
        self.load_index(1)
        
    def supprimer_clicked(self):
        self.banque_service.delete_banque(self.banque_service.banque_active)
        self.load()
        
    def load(self):        
        self.banque_service.set_banque_active()
        self.banque_table.clear()
        banques = self.banque_service.get_all_banques()
        for banque in banques:
            banqueItem = QListWidgetItem(banque.nom)
            banqueItem.setData(1, banque.id)
            self.banque_table.addItem(banqueItem)
        self.btn_supprimer.hide()
        self.btn_modifier.hide()
    def load_index(self, index):
        self.stack.setCurrentIndex(index)
        
        page = self.stack.currentWidget()
        if hasattr(page, "load"):
            page.load()
        if index == 0:
            self.load()