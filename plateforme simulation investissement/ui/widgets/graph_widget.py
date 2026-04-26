from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates

class GraphWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        self.ax = self.figure.add_subplot(111)

        layout.addWidget(self.canvas)

    def plot(self, x_data, y_data, labels=None, colors=None):
        """
        Trace une ou plusieurs courbes.
        
        Args:
            x_data: un vecteur x (partagé) OU une liste de vecteurs x
            y_data: un vecteur y OU une liste de vecteurs y
            labels: liste de noms pour la légende (optionnel)
            colors: liste de couleurs (optionnel)
        
        Exemples:
            # Une seule courbe
            plot(dates, soldes)
            
            # Plusieurs courbes, x partagé
            plot(dates, [soldes_lep, soldes_pea], labels=["LEP", "PEA"])
            
            # Plusieurs courbes, x différents
            plot([dates1, dates2], [soldes1, soldes2])
        """
        self.ax.clear()
        
        # Détecte si y_data contient plusieurs courbes
        is_multi_y = y_data and hasattr(y_data[0], '__iter__') and not isinstance(y_data[0], str)
        
        if not is_multi_y:
            # Une seule courbe
            x_data = [x_data]
            y_data = [y_data]
        else:
            # Plusieurs courbes — x partagé ou multiple ?
            is_multi_x = x_data and hasattr(x_data[0], '__iter__') and not isinstance(x_data[0], str)
            
            if not is_multi_x:
                # x partagé → on le duplique pour chaque y
                x_data = [x_data] * len(y_data)
        
        # Valeurs par défaut
        nb_courbes = len(y_data)
        labels = labels or [None] * nb_courbes
        colors = colors or [None] * nb_courbes
        
        # Plot chaque courbe
        for i, (x, y) in enumerate(zip(x_data, y_data)):
            x = list(x)
            y = list(y)
            self.ax.plot(x, y, label=labels[i], color=colors[i])

        self.ax.set_title("Solde du compte")
        self.ax.set_xlabel("Mois")
        self.ax.set_ylabel("Solde (€)")
        
        # Affiche la légende si des labels sont fournis
        if any(labels):
            self.ax.legend()
        
        # Formatage de l'axe X
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%Y'))
        self.ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        self.figure.autofmt_xdate()
        
        self.canvas.draw()