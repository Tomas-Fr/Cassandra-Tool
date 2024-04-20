from typing import Callable, List, Union
from PyQt6.uic import load_ui
from PyQt6.QtWidgets import QFrame
from constants.common import CREATE_TABLE_WINDOW_PATH, ErrorTitles
from constants.utils import pop_up_error
from constants.common import ErrorTitles
from backend.create_table_window.create_column_frame import CreateColumnFrame
from constants.column_model import ColumnModel
from backend.main_window.cassandra_manager import CassandraManager
from constants.create_table_model import CreateTableModel


class CreateTableWindow(QFrame):
    def __init__(self: 'CreateTableWindow',
                 key_space: str,
                 cassandra_manager: CassandraManager,
                 refresh_connection_tree_model: Callable[[], None]) -> None:
        super(CreateTableWindow, self).__init__()
        load_ui.loadUi(CREATE_TABLE_WINDOW_PATH, self)
        self.key_space: str = key_space
        self.cassandra_manager: CassandraManager = cassandra_manager
        self.column_frames: List[CreateColumnFrame] = []
        self.refresh_connection_tree_model = refresh_connection_tree_model

        self.key_space_label.setText(f"Create new table in keyspace '{self.key_space}'.")

        self.add_column_button.clicked.connect(self.add_column_frame)
        self.submit_button.clicked.connect(self.create_table)


    def add_column_frame(self: 'CreateTableWindow') -> None:
        column_frame = CreateColumnFrame()
        column_frame.remove_button.clicked.connect(lambda: self.remove_column(column_frame))
        self.column_frames.append(column_frame)
        self.scroll_area_vlayout.addWidget(column_frame)

    def remove_column(self: 'CreateTableWindow', column_frame: CreateColumnFrame) -> None:
        self.column_frames.remove(column_frame)
        column_frame.deleteLater()

    def create_table(self: 'CreateTableWindow') -> None:
        data = self.get_data_to_create_table()

        if data is None:
            return

        is_success = self.cassandra_manager.create_table(data)
        if is_success:
            self.close()
            self.refresh_connection_tree_model()

    def get_data_to_create_table(self: 'CreateTableWindow') -> Union[CreateTableModel, None]:
        columns: List[ColumnModel] = []

        if self.is_table_name_empty():
            pop_up_error(ErrorTitles.Error.value, f"Table name must not be empty.")
            return

        for column_frame in self.column_frames:
            model = column_frame.get_column_model()
            if self.is_column_name_empty(model.name):
                pop_up_error(ErrorTitles.Error.value, f"Column name must not be empty.")
                return
            columns.append(model)

        return CreateTableModel(self.key_space, self.table_name_line_edit.text(), columns)

    def is_table_name_empty(self: 'CreateTableWindow') -> bool:
        return self.table_name_line_edit.text() == ""

    def is_column_name_empty(self: 'CreateTableWindow', column_name: str) -> bool:
        return column_name == ""