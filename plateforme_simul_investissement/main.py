from ui.main_window import MainWindow
from PySide6.QtWidgets import QApplication
import sys
from repositories.repositories import Repositories
from services import AppContext
from session import Session

app = QApplication(sys.argv)
app.setStyle("Fusion")
with open("style.qss", "r") as f:
    app.setStyleSheet(f.read())

session = Session()

repos = Repositories("data/data_profil.xlsx")
appContext = AppContext(repos)

window = MainWindow(appContext, session )
window.resize(800, 500)

print(type(window))
print(window)
window.show()
app.exec()