from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class GraphWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        self.ax = self.figure.add_subplot(111)

        layout.addWidget(self.canvas)

    def plot(self, x, y):
        self.ax.clear()   # efface l'ancien graphique

        self.ax.plot(x, y)

        self.ax.set_title("Solde du compte")
        self.ax.set_xlabel("Mois")
        self.ax.set_ylabel("Solde (€)")

        self.canvas.draw()