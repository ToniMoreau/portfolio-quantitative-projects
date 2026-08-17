from .dependencyConfirmationDialog import *
from services.patrimoine_service import PatrimoineService
# somewhere in your widgets/ layer — a shared ui helper, not tied to one page

def confirm_and_delete(patrimoine_service :PatrimoineService, scenario, entity, parent_widget) -> bool:
    """Runs propagate_downstream, shows confirmation, executes if accepted.
    Returns True if deletion happened, False if cancelled."""
    dependents, excluded_ids = patrimoine_service.propagate_downstream(scenario, entity)
    dialog = DependencyConfirmationDialog(
        excluded_ids, label_resolver=patrimoine_service.resolve_label, parent=parent_widget
    )
    if dialog.exec() == QDialog.Accepted:
        patrimoine_service.delete_financement(dependents)
        return True
    return False