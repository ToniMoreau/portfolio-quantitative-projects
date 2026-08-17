from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

class AccueilPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Page d'accueil"))
        self.setLayout(layout)