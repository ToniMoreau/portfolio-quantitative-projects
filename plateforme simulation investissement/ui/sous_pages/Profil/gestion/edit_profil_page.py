from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,  QLabel, QPushButton, QLineEdit, QStackedWidget, QSizePolicy
)

from services import ProfileService
from session import Session


class EditProfilPage(QWidget):
    back_to_hub = Signal()
    def __init__(self, profile_service : ProfileService, session : Session):
        super().__init__()
        self.profile_service = profile_service
        self.session = session
        
        self.mlayout = QVBoxLayout(self)
        
        self.infos_profil = self.infos_profil_page() 
        self.edit_profil = self.edit_profil_page()
        
        self.stack = QStackedWidget()
        self.stack.addWidget(self.infos_profil) #index 0
        self.stack.addWidget(self.edit_profil)  #index 1
        
        self.mlayout.addWidget(self.stack)
        
        self.stack.setCurrentIndex(0)  
        
    def infos_profil_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        title =QLabel("Profil : ")
        
        self.username_label = QLabel("")
        
        self.fname_label = QLabel(f"Prénom : ")
        
        self.lname_label = QLabel(f"Nom de famille : ")
        
        self.age_label = QLabel(f"Age :")

        layout.addWidget(title)
        layout.addWidget(self.username_label)
        layout.addWidget(self.fname_label)
        layout.addWidget(self.lname_label)
        layout.addWidget(self.age_label)
        
        modifier_btn = QPushButton("Modifier ->")
        retour_btn = QPushButton("Retour <-")
        
        layout.addWidget(modifier_btn)
        layout.addWidget(retour_btn)
        modifier_btn.clicked.connect(lambda : self.stack.setCurrentIndex(1))
        retour_btn.clicked.connect(self.back_to_hub.emit)
        
        return page

    def edit_profil_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        title =QLabel("Modifier le profil : ")
        
        username_label = QLabel("Pseudo")
        self.username = QLineEdit()
        self.username.setPlaceholderText("Entrer le nouveau Pseudo")
        
        fname_label = QLabel("Prénom")
        self.fname = QLineEdit()
        self.fname.setPlaceholderText("Entrer le nouveau prénom")
        
        lname_label = QLabel("Nom de famille")
        self.lname = QLineEdit()
        self.lname.setPlaceholderText("Entrer le nouveau nom de famille")
        
        age_label = QLabel("Age")
        self.age = QLineEdit()
        self.age.setPlaceholderText("Entrer le nouvel age")
        
        layout.addWidget(title)
        layout.addWidget(username_label)
        layout.addWidget(self.username)
        layout.addWidget(fname_label)
        layout.addWidget(self.fname)
        layout.addWidget(lname_label)
        layout.addWidget(self.lname)
        layout.addWidget(age_label)
        layout.addWidget(self.age)
        
        #Boutons
        self.annuler_btn = QPushButton("Annuler x")
        self.enregistrer_btn = QPushButton("Enregister")
        
        layout.addWidget(self.enregistrer_btn)
        layout.addWidget(self.annuler_btn)
        
        #actions boutons
        self.annuler_btn.clicked.connect(lambda : self.stack.setCurrentIndex(0))
        self.enregistrer_btn.clicked.connect(self.enregistrer_clicked)

        return page
    
    def enregistrer_clicked(self):
        username = self.username.text().strip()
        username = username if username else self.session.current_user.username
        
        fname = self.fname.text().strip()
        fname = fname if fname else self.session.current_user.firstname
        
        lname = self.lname.text().strip()
        lname = lname if lname else self.session.current_user.lastname
        
        age = self.age.text()
        age = int(age) if age.isdigit() else int(self.session.current_user.age)
        data = {
            "username" : username,
            "firstname" : fname,
            "lastname" : lname,
            "age" : age
        }
        
        fresh_user = self.profile_service.update_profile(self.session.current_user.id, data)
        self.session.current_user = fresh_user
        
        self.load()
        self.stack.setCurrentIndex(0)
        

    def load(self):
        user = self.session.current_user
        
        self.username_label.setText(f"Pseudo : {user.username}")
        self.fname_label.setText(f"Prénom : {user.firstname}")
        self.lname_label.setText(f"Nom : {user.lastname}")
        self.age_label.setText(f"Age : {user.age}")
        
        self.username.setText("")
        self.fname.setText("")
        self.lname.setText("")
        self.age.setText("")
