from typing import Any, Callable, List
from PyQt6.QtWidgets import QMessageBox, QDialog, QWidget
from PyQt6.QtCore import QModelIndex
from constants.common import ErrorTitles
from backend.confirmation_dialog import ConfirmationDialog


def pop_up_error(error_title: ErrorTitles, message: str) -> None:
    QMessageBox.critical(
        None,
        error_title,
        f"{ErrorTitles.Error.value}: {message}",
    )

def pop_up_confirmation_dialog(parent: QWidget,
                               confirmation_message: str,
                               function_to_execute: Callable[..., Any],
                               *args: Any,
                               **kwargs: Any) -> None:
    dialog = ConfirmationDialog(confirmation_message, parent)
    result = dialog.exec()
    if result == QDialog.DialogCode.Accepted:
        function_to_execute(*args, **kwargs)

def get_root_parent(index: QModelIndex) -> QModelIndex:
    while index.parent() is not None:
        index = index.parent()
    return index

def remove_dashes(my_list: List[Any]) -> List[Any]:
    return [item for item in my_list if not item.startswith('--')]

def remove_empty_strings(my_list: List[Any]) -> List[Any]:
    return [item.strip() for item in my_list if item.strip()]