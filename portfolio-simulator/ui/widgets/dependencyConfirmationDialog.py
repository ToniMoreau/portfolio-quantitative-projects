from PySide6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton, QLabel, QHBoxLayout
from domain.enums import DependentType

class DependencyConfirmationDialog(QDialog):
    def __init__(self, dependents: list[tuple[int, "DependentType"]], label_resolver, parent=None):
        """
        dependents: list of (id, DependentType) from propagate_downstream.
        label_resolver: callable(id, type) -> str, resolves a readable label
                         (e.g. "Investissement — Appartement Paris, 15/03/2027").
                         Lives outside this dialog since it needs service access
                         this class shouldn't own.
        """
        super().__init__(parent)
        self.setWindowTitle("Confirmer la suppression")

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Cette action supprimera {len(dependents)} élément(s) :"))

        list_widget = QListWidget()
        for entity_id in dependents:
            list_widget.addItem(QListWidgetItem(label_resolver(entity_id)))
        layout.addWidget(list_widget)

        buttons = QHBoxLayout()
        confirm_btn = QPushButton("Confirmer")
        cancel_btn = QPushButton("Annuler")
        confirm_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)
        buttons.addWidget(confirm_btn)
        layout.addLayout(buttons)