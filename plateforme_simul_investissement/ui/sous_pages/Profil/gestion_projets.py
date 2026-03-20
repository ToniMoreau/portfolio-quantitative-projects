from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,  QLabel, QPushButton, QLineEdit, QStackedWidget, QSizePolicy
)


class ProjectsPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        
        self.title = QLabel("Projets")
        
        
        
        layout.addWidget(self.title)