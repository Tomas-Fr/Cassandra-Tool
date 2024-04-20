from PyQt6.uic import load_ui
from PyQt6.QtWidgets import QFrame
from constants.common import CREATE_COLUMN_FRAME_PATH
from constants.column_model import ColumnModel


class CreateColumnFrame(QFrame):
    def __init__(self: 'CreateColumnFrame') -> None:
        super(CreateColumnFrame, self).__init__()
        load_ui.loadUi(CREATE_COLUMN_FRAME_PATH, self)

    def get_column_model(self: 'CreateColumnFrame') -> ColumnModel:
        return ColumnModel(
            name = self.column_name_line_edit.text(),
            type = self.column_type_combobox.currentText(),
            is_partition_key = self.partition_key_check_box.isChecked(),
            is_clustering_key = self.clustering_key_check_box.isChecked(),
            create_index = self.create_index_check_box.isChecked(),
            order_by = self.order_by_combo_box.currentText()
        )
