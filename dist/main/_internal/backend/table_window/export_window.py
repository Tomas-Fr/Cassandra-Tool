import csv
import os
from PyQt6.uic import load_ui
from PyQt6.QtWidgets import QFrame, QFileDialog, QPlainTextEdit
from constants.common import EXPORT_WINDOW_PATH
from constants.utils import pop_up_error
from constants.common import ExportTypes, ErrorTitles, RESULT_STATISTICS
from backend.table_window.cassandra_table_model import CassandraTableModel


class ExportWindow(QFrame):
    def __init__(self: 'ExportWindow',
                 cassandra_model: CassandraTableModel,
                 result_statistics_plain_text_edit: QPlainTextEdit) -> None:
        super(ExportWindow, self).__init__()
        load_ui.loadUi(EXPORT_WINDOW_PATH, self)
        self.cassandra_model = cassandra_model
        self.result_statistics_plain_text_edit = result_statistics_plain_text_edit
        self.export_push_button.clicked.connect(self.export)
        self.select_directory_push_button.clicked.connect(self.show_folder_dialog)


    def export(self: 'ExportWindow') -> None:
        match self.export_type_combo_box.currentText():
            case ExportTypes.CSV.value:
                self.export_to_csv()
            case ExportTypes.JOSN.value:
                pop_up_error("Info", "Not implemented yet.")
            case ExportTypes.XML.value:
                pop_up_error("Info", "Not implemented yet.")

    def validate_input(self: 'ExportWindow') -> bool:
        return all([self.name_line_edit.text() != "", self.path_line_edit.text() != ""])

    def export_to_csv(self: 'ExportWindow') -> None:
        if self.validate_input():
            file_path = f"{os.path.join(self.path_line_edit.text(), self.name_line_edit.text())}.csv"
            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                csv_writer = csv.DictWriter(csvfile, fieldnames=self.cassandra_model.header_data)
                csv_writer.writeheader()
                for count, row in enumerate(self.cassandra_model.data, 1):
                    csv_writer.writerow(row._asdict())
            self.result_statistics_plain_text_edit.setPlainText(f"{RESULT_STATISTICS} Successfully exported {count} rows.")
            self.close()
        else:
            pop_up_error(ErrorTitles.Error.value, "'Name' and 'Path' must not be empty")

    def show_folder_dialog(self: 'ExportWindow') -> None:
        folder_path = QFileDialog.getExistingDirectory(self, "Select File Path")
        if folder_path:
            self.path_line_edit.setText(folder_path)