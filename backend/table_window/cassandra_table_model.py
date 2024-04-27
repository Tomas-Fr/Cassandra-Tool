from typing import Any, List, Union
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex, QObject
from PyQt6.QtWidgets import QPlainTextEdit, QTableView
from constants.model_wrapper import ModelWrapper
from constants.cassandra_row_list import CassandraRowList
from constants.show_result_utils import ShowResultUtils
from constants.insert_row_utils import InsertRowUtils
from constants.common import CASSANDRA_TYPE_MAPPING
from backend.table_window.cassandra_table_manager import CassandraTableManager
from cassandra.cluster import ResultSet, PreparedStatement


class CassandraTableModel(QAbstractTableModel):
    def __init__(self: 'CassandraTableModel',
                 cassandra_manager: CassandraTableManager,
                 results_plain_text_edit: QPlainTextEdit,
                 result_statistics_plain_text_edit: QPlainTextEdit,
                 parent: QObject = None,
                 new_data: ResultSet = None) -> None:
        super().__init__(parent)
        self.cassandra_manager = cassandra_manager
        self.data = new_data or self.cassandra_manager.select_all()
        self.header_data = list(self.data[0]._asdict().keys()) if self.data else self.cassandra_manager.header_data
        self.cassandra_row = CassandraRowList(self)
        self.edited_cells_indexes = []
        self.results_plain_text_edit = results_plain_text_edit
        self.result_statistics_plain_text_edit = result_statistics_plain_text_edit
        self.insert_row_utils = InsertRowUtils()
        self.show_result_utils = ShowResultUtils(self.results_plain_text_edit, self.result_statistics_plain_text_edit)


    def setData(self: 'CassandraTableModel', index: QModelIndex, value: str, role=Qt.ItemDataRole.EditRole) -> bool:
        if role == Qt.ItemDataRole.EditRole:
            row = index.row()
            column = index.column()
            value = self.retype_edited_value(column, value)

            if isinstance(self.data[row], ModelWrapper):
                setattr(self.data[row], self.header_data[column], value)
            else:
                updated_row = self.data[row]._replace(**{self.header_data[column]: value})
                self.data[row] = updated_row

            self.layoutChanged.emit()
            return True
        return False

    def retype_edited_value(self: 'CassandraTableModel', column_index: int, value: str) -> Union[Any, None]:
        column_name = self.headerData(column_index, Qt.Orientation.Horizontal)
        for column_type in self.cassandra_manager.column_types:
            if column_name == column_type.column_name:
                _type = column_type.type.split('<')[0]
                return self.insert_row_utils.convert_column(value, CASSANDRA_TYPE_MAPPING[_type])

    def rowCount(self: 'CassandraTableModel', parent: QModelIndex = QModelIndex()) -> int:
        return len(self.data) if self.data else 0

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.data[0]) if self.data else 0

    def data(self: 'CassandraTableModel',
             index: QModelIndex,
             role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole) -> Union[str, None]:
        if role == Qt.ItemDataRole.DisplayRole:
            return str(getattr(self.data[index.row()], self.header_data[index.column()], None))
        return None

    def headerData(self: 'CassandraTableModel',
                   section: int,
                   orientation: Qt.Orientation,
                   role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            if self.header_data:
                return self.header_data[section]
        return super().headerData(section, orientation, role)

    def removeRow(self: 'CassandraTableModel', row: int, parent: QModelIndex =QModelIndex()) -> None:
        self.beginRemoveRows(parent, row, row)
        del self.data[row]
        self.endRemoveRows()

    def addRow(self: 'CassandraTableModel') -> None:
        self.cassandra_row.add_row()

    def refresh(self: 'CassandraTableModel') -> None:
        self.cassandra_row.remove_rows()
        self.data = self.cassandra_manager.select_all()
        self.layoutChanged.emit()

    def clear_edited_row_indexes(self: 'CassandraTableModel') -> None:
        self.edited_cells_indexes = []

    def delete_rows(self: 'CassandraTableModel', table_view: QTableView) -> None:
        selected_indexes = table_view.selectionModel().selectedIndexes()
        unique_rows = set(index.row() for index in selected_indexes)

        for row in sorted(unique_rows, reverse=True):
            self.cassandra_manager.delete_row(self.data, row)
            self.removeRow(row)

    def update_rows(self: 'CassandraTableModel') -> None:
        row_indexes = self.get_row_indexes()

        for row_index in sorted(row_indexes, reverse=True):
            row = self.data[row_index]
            if not isinstance(row, ModelWrapper):
                row = row._asdict()
            self.cassandra_manager.update_row(self.data, row_index, row)

    def get_row_indexes(self: 'CassandraTableModel') -> List[int]:
        row_indexes = set()
        for cell_index in self.edited_cells_indexes:
            row_index = cell_index.row()
            row_indexes.add(row_index)
        return list(row_indexes)

    def commit_new_rows(self: 'CassandraTableModel') -> None:
        column_types = self.cassandra_manager.get_column_types()
        query = self.cassandra_manager.prepare_insert_query()

        self.insert_rows(query, column_types)

        self.cassandra_row.remove_rows()
        self.clear_edited_row_indexes()

    def insert_rows(self: 'CassandraTableModel', query: PreparedStatement, column_types: List[dict]) -> None:
        error_count = 0
        added_rows_count = 0
        for new_row in self.cassandra_row.new_rows:
            error_message = self.cassandra_manager.insert_row(query, self.insert_row_utils.prepare_row(column_types, new_row))
            if not error_message:
                added_rows_count += 1
            else:
                error_count += 1
            self.show_result_utils.show_result(error_message)
            self.show_result_utils.show_result_statistics(added_rows_count, error_count)