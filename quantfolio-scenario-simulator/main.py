from ui.main_window import MainWindow
from PySide6.QtWidgets import QApplication
import sys
from repositories.repos import Repositories
from services import AppContext, Page
from session import Session

print("wtd")
app = QApplication(sys.argv)
app.setStyle("Fusion")
with open("style.qss", "r") as f:
    app.setStyleSheet(f.read())
print("après style")

session = Session()
print("après session")

repos = Repositories("data/data_profil.xlsx")
print("après repos")

appContext = AppContext(repos)
print("après appContext")

window = MainWindow(appContext, session)
print("après MainWindow", type(window))

window.showMaximized()
print("après showMaximized")

app.exec()
print("après exec")
