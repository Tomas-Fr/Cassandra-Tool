from typing import Any, Union
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex, QObject
from backend.table_window.cassandra_table_manager import CassandraTableManager


class TableDescriptionModel(QAbstractTableModel):
    def __init__(self: 'TableDescriptionModel',
                 cassandra_manager: CassandraTableManager,
                 parent: QObject = None) -> None:
        super().__init__(parent)
        self.cassandra_manager = cassandra_manager
        self.header_data = ["Column name", "Type"]
        self.columns_types = self.cassandra_manager.column_types
        self._data = []
        self.generate_data()


    def generate_data(self: 'TableDescriptionModel') -> None:
        for column in self.columns_types:
            self._data.append([column.column_name, column.type])

    def rowCount(self: 'TableDescriptionModel', parent=QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self: 'TableDescriptionModel', parent=QModelIndex()) -> int:
        return len(self.header_data)

    def data(self: 'TableDescriptionModel', index, role=Qt.ItemDataRole.DisplayRole) -> Union[None, Any]:
        if not index.isValid():
            return None
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()][index.column()]
        return None

    def headerData(self: 'TableDescriptionModel',
                   section, orientation,
                   role=Qt.ItemDataRole.DisplayRole) -> Union[None, Any]:
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.header_data[section]
        return None
