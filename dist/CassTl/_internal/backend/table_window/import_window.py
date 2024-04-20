import csv
from PyQt6.uic import load_ui
from PyQt6.QtWidgets import QFrame, QFileDialog, QPlainTextEdit
from constants.common import IMPORT_WINDOW_PATH, ExportTypes
from constants.utils import pop_up_error
from constants.show_result_utils import ShowResultUtils
from constants.insert_row_utils import InsertRowUtils
from backend.table_window.cassandra_table_model import CassandraTableModel
from backend.table_window.cassandra_table_manager import CassandraTableManager


class ImportWindow(QFrame):
    def __init__(self: 'ImportWindow',
                 cassandra_manager: CassandraTableManager,
                 cassandra_model: CassandraTableModel,
                 results_plain_text_edit: QPlainTextEdit,
                 result_statistics_plain_text_edit: QPlainTextEdit) -> None:
        super(ImportWindow, self).__init__()
        load_ui.loadUi(IMPORT_WINDOW_PATH, self)
        self.cassandra_manager = cassandra_manager
        self.cassandra_model = cassandra_model
        self.results_plain_text_edit = results_plain_text_edit
        self.result_statistics_plain_text_edit = result_statistics_plain_text_edit
        self.import_push_button.clicked.connect(self.import_data)
        self.select_file_push_button.clicked.connect(self.show_file_dialog)
        self.show_result_utils = ShowResultUtils(self.results_plain_text_edit, self.result_statistics_plain_text_edit)
        self.insert_row_utils = InsertRowUtils()


    def import_data(self: 'ImportWindow') -> None:
        match self.import_type_combo_box.currentText():
            case ExportTypes.CSV.value:
                self.import_from_csv()
            case ExportTypes.JOSN.value:
                pop_up_error("Info", "Not implemented yet.")
            case ExportTypes.XML.value:
                pop_up_error("Info", "Not implemented yet.")

    def show_file_dialog(self: 'ImportWindow') -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file_path:
            self.file_path_line_edit.setText(file_path)

    def import_from_csv(self: 'ImportWindow') -> None:
        column_types = self.cassandra_manager.get_column_types()
        query = self.cassandra_manager.prepare_insert_query()
        error_count = 0
        added_rows_count = 0

        with open(self.file_path_line_edit.text(), newline='', encoding='utf-8') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                error_message = self.cassandra_manager.insert_row(query, self.insert_row_utils.prepare_row(column_types, row))
                if not error_message:
                    added_rows_count += 1
                else:
                    error_count += 1
                self.show_result_utils.show_result(error_message)
                self.show_result_utils.show_result_statistics(added_rows_count, error_count)
        self.cassandra_model.refresh()
        self.close()
