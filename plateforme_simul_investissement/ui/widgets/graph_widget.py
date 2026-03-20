from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class GraphWidget(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        # figure matplotlib
        self.figure = Figure()

        # canvas Qt
        self.canvas = FigureCanvas(self.figure)

        layout.addWidget(self.canvas)

    def plot(self, x, y):

        ax = self.figure.add_subplot(111)
        
        ax.plot(x, y)

        ax.set_title("Solde du compte")
        ax.set_xlabel("Mois")
        ax.set_ylabel("Solde (€)")

        self.canvas.draw()