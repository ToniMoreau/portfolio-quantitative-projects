from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

class ParametresPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Page des paramètres"))
        self.setLayout(layout)