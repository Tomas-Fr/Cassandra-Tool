from typing import Any, Union
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex, QObject
from backend.table_window.cassandra_table_manager import CassandraTableManager


class IndexesDescription(QAbstractTableModel):
    def __init__(self: 'IndexesDescription',
                 cassandra_manager: CassandraTableManager,
                 parent: QObject = None) -> None:
        super().__init__(parent)
        self.cassandra_manager = cassandra_manager
        self.header_data = ["Name", "Create statement"]
        self.ddl = self.cassandra_manager.ddl
        self._data = []
        self.generate_data()


    def generate_data(self: 'IndexesDescription') -> None:
        if not self.ddl:
            return None
        for row in self.ddl:
            if row.type == "index":
                self._data.append([row.name, row.create_statement])

    def rowCount(self: 'IndexesDescription', parent=QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self: 'IndexesDescription', parent=QModelIndex()) -> int:
        return len(self.header_data)

    def data(self: 'IndexesDescription', index, role=Qt.ItemDataRole.DisplayRole) -> Union[None, Any]:
        if not index.isValid():
            return None
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()][index.column()]
        return None

    def headerData(self: 'IndexesDescription',
                   section, orientation,
                   role=Qt.ItemDataRole.DisplayRole) -> Union[None, Any]:
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.header_data[section]
        return None