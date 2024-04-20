import re
from typing import List, Optional
from PyQt6.uic import load_ui
from PyQt6.QtWidgets import QFrame, QLineEdit
from constants.common import TABLE_UI_PATH, ErrorTitles
from backend.table_window.cassandra_table_manager import CassandraTableManager
from backend.table_window.cassandra_table_model import CassandraTableModel
from backend.table_window.table_description_model import TableDescriptionModel
from backend.table_window.primary_key_description import PrimaryKeyDescription
from backend.table_window.indexes_description_model import IndexesDescription
from constants.connection_model import Connection
from constants.utils import pop_up_confirmation_dialog, remove_dashes, remove_empty_strings
from constants.common import ConfirmationMessages
from backend.table_window.export_window import ExportWindow
from backend.table_window.import_window import ImportWindow
from PyQt6.QtCore import Qt, QModelIndex
from constants.show_result_utils import ShowResultUtils
from constants.insert_row_utils import InsertRowUtils


class DatabaseTable(QFrame):
    opened_windows = []
    def __init__(self: 'DatabaseTable', connection: Connection, key_space: str, table: str) -> None:
        super(DatabaseTable, self).__init__()
        load_ui.loadUi(TABLE_UI_PATH, self)
        self.splitter.setSizes([50, 700, 200])
        self.cluster = connection.cluster
        self.session = self.cluster.connect(keyspace=key_space)
        self.key_space = key_space
        self.table = table
        self.cassandra_manager = CassandraTableManager(self.cluster,
                                                       self.session,
                                                       self.key_space,
                                                       self.table,
                                                       self.results_plain_text_edit,
                                                       self.result_statistics_plain_text_edit)
        self.original_cassandra_model = CassandraTableModel(self.cassandra_manager,
                                                            self.results_plain_text_edit,
                                                            self.result_statistics_plain_text_edit)
        self.cassandra_model = self.original_cassandra_model
        self.table_description_model = TableDescriptionModel(self.cassandra_manager)
        self.primary_key_description_model = PrimaryKeyDescription(self.cassandra_manager)
        self.indexes_description_model = IndexesDescription(self.cassandra_manager)

        self.show_result_utils = ShowResultUtils(self.results_plain_text_edit, self.result_statistics_plain_text_edit)
        self.insert_row_utils = InsertRowUtils()

        self.set_up_database_data_view(self.cassandra_model)
        self.set_up_table_description_data(self.table_description_model)
        self.set_up_primary_key_description_data(self.primary_key_description_model)
        self.set_up_indexes_description_data(self.indexes_description_model)
        self.set_up_ddl_description()

        self.delete_push_button.clicked.connect(
            lambda: pop_up_confirmation_dialog(
                self,
                ConfirmationMessages.DELETE.value,
                lambda: self.delete_rows()
            )
        )
        self.refresh_push_button.clicked.connect(self.refresh)
        self.cancel_edit_push_button.clicked.connect(self.refresh)
        self.commit_push_button.clicked.connect(self.commit)
        self.add_row_push_button.clicked.connect(self.add_row)
        self.export_push_button.clicked.connect(self.export_popup_window)
        self.import_push_button.clicked.connect(self.import_popup_window)
        self.clear_results_push_button.clicked.connect(self.show_result_utils.clear_results)
        self.table_view.doubleClicked.connect(self.handle_double_clicked)
        self.execute_push_button.clicked.connect(self.execute)
        self.clear_editor_push_button.clicked.connect(self.clear_cql_editor)


    def export_popup_window(self: 'DatabaseTable') -> None:
        window = ExportWindow(self.cassandra_model, self.result_statistics_plain_text_edit)
        DatabaseTable.opened_windows.append(window)
        window.show()

    def import_popup_window(self: 'DatabaseTable') -> None:
        window = ImportWindow(self.cassandra_manager, self.cassandra_model, self.results_plain_text_edit, self.result_statistics_plain_text_edit)
        DatabaseTable.opened_windows.append(window)
        window.show()

    def clear_cql_editor(self: 'DatabaseTable') -> None:
        self.query_plain_text_edit.setPlainText("")

    def set_key_space_to_session(self: 'DatabaseTable') -> None:
        if self.key_space is not None:
            self.session.set_keyspace(self.key_space)

    def set_up_database_data_view(self: 'DatabaseTable', model: CassandraTableModel) -> None:
        self.table_view.setModel(model)
        self.table_view.resizeColumnsToContents()

    def prepare_queries(self: 'DatabaseTable') -> List[str]:
        queries_from_cql_editor = self.query_plain_text_edit.toPlainText()
        queries = remove_dashes(queries_from_cql_editor.split('\n'))
        return remove_empty_strings(' '.join(queries).split(';'))

    def set_table(self: 'DatabaseTable', key_space: str, table: str, data: List[dict] = None) -> None:
        self.cassandra_manager = CassandraTableManager(self.cluster,
                                                       self.session,
                                                       key_space,
                                                       table,
                                                       self.results_plain_text_edit,
                                                       self.result_statistics_plain_text_edit)
        self.cassandra_model = CassandraTableModel(self.cassandra_manager,
                                                   self.results_plain_text_edit,
                                                   self.result_statistics_plain_text_edit,
                                                   new_data=data)

    def extract_key_space_from_query(self: 'DatabaseTable', query: str) -> str:
        pattern = r'from ([^.]+)\.(\w+)'

        match = re.search(pattern, query, re.IGNORECASE)

        key_space = None
        if match:
            key_space = match.group(1)
        return key_space

    def extract_table_from_query(self: 'DatabaseTable', query: str) -> str:
        pattern = r'from ([^.]+\.|)(\w+)'

        match = re.search(pattern, query, re.IGNORECASE)

        table = None
        if match:
            table = match.group(2)
        return table

    def check_for_select(self: 'DatabaseTable', query: str, data: List[dict] = None) -> None:
        if "select" in query.lower():
            key_space = self.extract_key_space_from_query(query) or self.key_space
            table = self.extract_table_from_query(query)
            if key_space and table:
                self.set_table(key_space, table, data)
                self.set_up_database_data_view(self.cassandra_model)

    def execute(self: 'DatabaseTable') -> Optional[Exception]:
        for query in self.prepare_queries():
            try:
                result = self.session.execute(query).all()
            except Exception as error_message:
                error_message = f"{ErrorTitles.Failed.value} {error_message}\nquery: {query}\n"
                self.show_result_utils.show_result(error_message)
            else:
                self.show_result_utils.show_success()

                self.check_for_select(query, result)

                for item in result:
                    self.show_result_utils.show_result(str(item))

    def refresh(self: 'DatabaseTable') -> None:
        self.cassandra_model = self.original_cassandra_model
        self.set_up_database_data_view(self.original_cassandra_model)
        self.original_cassandra_model.refresh()

    def commit(self: 'DatabaseTable') -> None:
        self.cassandra_model.update_rows()
        self.cassandra_model.commit_new_rows()

    def cancel_edit(self: 'DatabaseTable', edit_widget: QLineEdit, index: QModelIndex, original_value: str) -> None:
        if edit_widget:
            edit_widget.close()
            self.table_view.closePersistentEditor(index)
            self.register_edited_cell(original_value, index)

    def register_edited_cell(self: 'DatabaseTable', original_value: str, index: QModelIndex) -> None:
        edited_value = index.data(Qt.ItemDataRole.DisplayRole)
        if original_value != edited_value:
            self.cassandra_model.edited_cells_indexes.append(index)

    def is_edit_allowed(self: 'DatabaseTable') -> bool:
        return len(self.cassandra_model.header_data) == len(self.cassandra_manager.header_data)

    def handle_double_clicked(self: 'DatabaseTable', index: QModelIndex) -> None:
        original_value = index.data(Qt.ItemDataRole.DisplayRole)
        if original_value is not None and self.is_edit_allowed():
            self.table_view.openPersistentEditor(index)
            edit_widget = self.table_view.indexWidget(index)
            self.set_edited_cell(edit_widget, original_value, index)

    def set_edited_cell(self: 'DatabaseTable', edit_widget: QLineEdit, original_value: str, index: QModelIndex) -> None:
        if edit_widget and isinstance(edit_widget, QLineEdit):
            edit_widget.setText(original_value)
            edit_widget.selectAll()
            edit_widget.setStyleSheet("background-color: orange; color: blue;")
            edit_widget.editingFinished.connect(lambda: self.cancel_edit(edit_widget, index, original_value))

    def add_row(self: 'DatabaseTable') -> None:
        self.cassandra_model.addRow()

    def delete_rows(self: 'DatabaseTable') -> None:
        self.cassandra_model.delete_rows(self.table_view)

#######################################################################################################
# Table description
    def set_up_table_description_data(self: 'DatabaseTable', model: TableDescriptionModel) -> None:
        self.table_description_table_view.setModel(model)
        self.table_description_table_view.resizeColumnsToContents()

    def set_up_primary_key_description_data(self: 'DatabaseTable', model: TableDescriptionModel) -> None:
        self.primary_key_description_table_view.setModel(model)
        self.primary_key_description_table_view.resizeColumnsToContents()

    def set_up_indexes_description_data(self: 'DatabaseTable', model: TableDescriptionModel) -> None:
        self.indexes_description_table_view.setModel(model)
        self.indexes_description_table_view.resizeColumnsToContents()

    def set_up_ddl_description(self: 'DatabaseTable') -> None:
        if not self.cassandra_manager.ddl:
            return None
        create_statements: list[str] = []
        for row in self.cassandra_manager.ddl:
            create_statements.append(row.create_statement)
        ddl_description = "\n".join(create_statements)
        self.ddl_description_plain_text_edit.setPlainText(ddl_description)