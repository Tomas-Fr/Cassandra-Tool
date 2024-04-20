from typing import Any
from PyQt6.QtSql import QSqlTableModel
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QStyledItemDelegate, QLineEdit, QMainWindow
from backend.connection_profiles.connection_profiles_database import PASSWORD_COLUMN_INDEX
from backend.connection_profiles.master_password_manager import MasterPasswordManager
from backend.connection_profiles.connection_profiles_database import ConnectionProfilesDatabase


class CustomQSqlTableModel(QSqlTableModel):
    def __init__(self: 'CustomQSqlTableModel',
                 parent: QMainWindow,
                 master_password_manager: MasterPasswordManager,
                 conn_prof_db: ConnectionProfilesDatabase,
                 *args,
                 **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.master_password_manager = master_password_manager
        self.conn_prof_db = conn_prof_db


    def data(self: 'CustomQSqlTableModel', index: int, role=Qt.ItemDataRole.DisplayRole) -> Any:
        if role == Qt.ItemDataRole.DisplayRole and index.column() == PASSWORD_COLUMN_INDEX:
            return '*' * 16
        else:
            return super().data(index, role)

    def setData(self: 'CustomQSqlTableModel', index: int, value: Any, role=Qt.ItemDataRole.EditRole) -> bool:
        if index.column() == PASSWORD_COLUMN_INDEX:
            connection_name: str = self.data(index.sibling(index.row(), 0))
            password_encrypted: bytes = None
            if isinstance(value, bytes):
                password_encrypted = value
            else:
                if self.master_password_manager.is_master_password_created():
                    password_encrypted = self.master_password_manager.encrypt_aes_256(value)
                else:
                    password_encrypted = value.encode('utf-8')
            self.conn_prof_db.update_password(connection_name, password_encrypted)
            return True
        else:
            return super().setData(index, value, role)


class PasswordLineEdit(QLineEdit):
    def __init__(self: 'PasswordLineEdit', parent=None) -> None:
        super().__init__(parent)
        self.setEchoMode(QLineEdit.EchoMode.Password)

class PasswordDelegate(QStyledItemDelegate):
    def createEditor(self: 'PasswordDelegate', parent, option, index) -> PasswordLineEdit:
        editor = PasswordLineEdit(parent)
        return editor