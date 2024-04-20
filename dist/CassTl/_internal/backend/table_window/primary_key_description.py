from itertools import zip_longest
from typing import Any, List, Tuple, Union
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex, QObject
from backend.table_window.cassandra_table_manager import CassandraTableManager
from constants.utils import remove_empty_strings


class PrimaryKeyDescription(QAbstractTableModel):
    def __init__(self: 'PrimaryKeyDescription',
                 cassandra_manager: CassandraTableManager,
                 parent: QObject = None) -> None:
        super().__init__(parent)
        self.cassandra_manager = cassandra_manager
        self.header_data = ["Primary key", "Partition key", "Clustering key"]
        self.ddl = self.cassandra_manager.ddl
        self._data = []
        self.generate_data()


    def generate_data(self: 'PrimaryKeyDescription') -> None:
        if self.ddl:
            primary_key, partition_key, clustering_key = self.find_primary_key(self.ddl[0].create_statement)
            self._data = list(zip_longest(primary_key, partition_key, clustering_key))

    def find_primary_key(self: 'PrimaryKeyDescription', ddl: str) -> Tuple[List[str], List[str], List[str]]:
        primary_key: list[str] = []
        partition_key: list[str] = []
        clustering_key: list[str] = []
        clustering_keys_order: list[str] = []
        rows = ddl.split('\n')
        for row in rows:
            row = row.strip()
            if row.startswith("PRIMARY KEY"):
                partition_key, clustering_key = self.process_primary_key(row)
            if row.endswith("PRIMARY KEY,"):
                partition_key = self.process_primary_key_in_column_definition(row)
            if row.startswith(") WITH CLUSTERING ORDER BY"):
                clustering_keys_order = self.process_clustering_key_order(row)
        primary_key = partition_key + clustering_key
        return (primary_key, partition_key, clustering_keys_order)

    def calculate_composite_partition_key(self: 'PrimaryKeyDescription', keys: str) -> Tuple[List[str], List[str]]:
        partition_keys, _, clustering_keys = keys.partition(")")
        partition_key = remove_empty_strings(partition_keys.lstrip("(").split(","))
        clustering_key = remove_empty_strings(clustering_keys.lstrip(",").split(","))
        return (partition_key, clustering_key)

    def calculate_single_partition_key(self: 'PrimaryKeyDescription', keys: str) -> Tuple[List[str], List[str]]:
        keys = remove_empty_strings(keys.split(","))
        partition_key = [keys[0]]
        clustering_key = keys[1:]
        return (partition_key, clustering_key)

    def process_primary_key(self: 'PrimaryKeyDescription', row: str) -> Tuple[List[str], List[str]]:
        _, _, keys = row.partition("(")
        keys = keys.rstrip(")")
        if "(" in keys:
            return self.calculate_composite_partition_key(keys)
        else:
            return self.calculate_single_partition_key(keys)

    def process_primary_key_in_column_definition(self: 'PrimaryKeyDescription', row: str) -> List[str]:
        return [row.split(" ", 1)[0]]

    def process_clustering_key_order(self: 'PrimaryKeyDescription', row: str) -> List[str]:
        ") WITH CLUSTERING ORDER BY (publication_year DESC, title ASC)"
        _, _, clustering_keys_order = row.partition("(")
        return clustering_keys_order[:-1].split(", ")

    def rowCount(self: 'PrimaryKeyDescription', parent=QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self: 'PrimaryKeyDescription', parent=QModelIndex()) -> int:
        return len(self.header_data)

    def data(self: 'PrimaryKeyDescription',
             index: QModelIndex,
             role=Qt.ItemDataRole.DisplayRole) -> Union[None, Any]:
        if not index.isValid():
            return None
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()][index.column()]
        return None

    def headerData(self: 'PrimaryKeyDescription',
                   section: int,
                   orientation: Qt.Orientation,
                   role=Qt.ItemDataRole.DisplayRole) -> Union[None, Any]:
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.header_data[section]
        return None