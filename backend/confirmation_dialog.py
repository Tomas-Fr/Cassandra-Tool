from PyQt6.QtWidgets import QVBoxLayout, QLabel, QDialog, QVBoxLayout, QDialogButtonBox, QWidget


class ConfirmationDialog(QDialog):
    def __init__(self: 'ConfirmationDialog', message: str, parent: QWidget =None) -> None:
        super(ConfirmationDialog, self).__init__(parent)

        layout = QVBoxLayout()

        label = QLabel(message)
        layout.addWidget(label)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)
        self.setLayout(layout)
