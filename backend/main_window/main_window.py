from typing import Union
from PyQt6.QtWidgets import QMainWindow, QMenu
from PyQt6 import uic
from PyQt6.QtCore import Qt, QModelIndex, QPoint
from constants.common import MAIN_WINDOW_UI_PATH, DATABASE_NAVIGATION_HEADER, TreeViewActionType, TreeViewDepthLevel, NO_TABLE
from backend.main_window.custom_cassandra_tree_model import CustomCassandraTreeModel
from constants.connection_model import Connection
from backend.table_window.database_table import DatabaseTable
from PyQt6.QtGui import QAction, QCloseEvent, QStandardItem
from backend.main_window.cassandra_manager import CassandraManager
from constants.utils import pop_up_confirmation_dialog
from backend.create_table_window.create_table_window import CreateTableWindow
from backend.create_key_space_window.create_key_space import CreateKeySpaceWindow


class MainWindow(QMainWindow):
    opened_windows = []

    def __init__(self: 'MainWindow', connections: list[Connection]) -> None:
        super(MainWindow, self).__init__()
        uic.loadUi(MAIN_WINDOW_UI_PATH, self)
        self.splitter.setSizes([200, 700])
        self.connections = connections
        self.is_open = True
        self.refresh_connection_tree_model()
        self.set_closeable_tabs()
        self.database_navigation_tree_view.doubleClicked.connect(self.open_table)
        self.database_navigation_tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.database_navigation_tree_view.customContextMenuRequested.connect(self.show_context_menu)


    def set_closeable_tabs(self: 'MainWindow') -> None:
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.closeTab)
        [self.tab_widget.removeTab(0) for _ in range(2)]

    def closeTab(self: 'MainWindow', index: int) -> None:
        widget = self.tab_widget.widget(index)
        if widget is not None:
            widget.deleteLater()
        self.tab_widget.removeTab(index)

    def closeEvent(self: 'MainWindow', event: QCloseEvent) -> None:
        self.is_open = False
        self.connections.clear()
        event.accept()

    def refresh_connection_tree_model(self: 'MainWindow') -> None:
        cassandra_model = CustomCassandraTreeModel(self.connections)
        self.custom_model = cassandra_model.create_custom_model()
        self.custom_model.setHorizontalHeaderLabels([DATABASE_NAVIGATION_HEADER])
        self.database_navigation_tree_view.setModel(self.custom_model)

    def add_tab(self: 'MainWindow', item: QStandardItem) -> None:
        if not item.parent():
            return None
        table = item.text()
        key_space = item.parent().text()
        table_name = f"{table} ({key_space})"
        tab_content = DatabaseTable(self.select_connection(item), key_space, table)
        self.tab_widget.addTab(tab_content, table_name)

    def select_connection(self: 'MainWindow', item: QStandardItem) -> Connection:
        for connection in self.connections:
            if self.get_text_from_root_parent(item) == connection.connection_profile_name:
                return connection

    def get_text_from_root_parent(self: 'MainWindow', item: QStandardItem) -> Union[str, None]:
        while item.parent() is not None:
            item = item.parent()
        return item.text() if item else None

    def open_table(self: 'MainWindow', index: QModelIndex) -> None:
        item = self.custom_model.itemFromIndex(index)
        if item and not item.hasChildren() and not (item.text() == NO_TABLE):
            self.add_tab(item)

    def show_context_menu(self: 'MainWindow', position: QPoint) -> None:
        index = self.database_navigation_tree_view.indexAt(position)
        if index.isValid():
            self.menu = QMenu()

            self.set_action_menu(self.get_depth(index))

            action = self.menu.exec(self.database_navigation_tree_view.viewport().mapToGlobal(position))
            if action:
                self.execute_action(action.text(), index)

    def close_related_tables(self: 'MainWindow', key_space: str, table: str = None) -> None:
        removed_number_of_widgets = 0
        for i in range(self.tab_widget.count()):
            index = i - removed_number_of_widgets
            tab_widget = self.tab_widget.widget(index)
            if tab_widget and tab_widget.key_space == key_space and (not table or tab_widget.table == table):
                self.closeTab(index)
                removed_number_of_widgets += 1

    def execute_action(self: 'MainWindow', action: TreeViewActionType, index: QModelIndex) -> None:
        item = self.custom_model.itemFromIndex(index)
        self.cassandra_manager = CassandraManager(self.select_connection(item))
        match action:
            case TreeViewActionType.create_key_space.value:
                self.open_create_key_space_window()
            case TreeViewActionType.refresh.value:
                self.refresh_connection_tree_model()
            case TreeViewActionType.delete_key_space.value:
                pop_up_confirmation_dialog(
                    parent = self,
                    confirmation_message = f"Do you really want to delete the '{index.data()}' keyspace?",
                    function_to_execute = self.delete_key_space,
                    index = index)
            case TreeViewActionType.create_table.value:
                self.open_create_table_window(index.data())
            case TreeViewActionType.delete_table.value:
                pop_up_confirmation_dialog(
                    parent = self,
                    confirmation_message = f"Do you really want to delete the '{index.parent().data()}.{index.data()}' table?",
                    function_to_execute = self.delete_table,
                    index = index)

    def open_create_table_window(self: 'MainWindow', key_space: str) -> None:
        window = CreateTableWindow(key_space, self.cassandra_manager, self.refresh_connection_tree_model)
        MainWindow.opened_windows.append(window)
        window.show()

    def open_create_key_space_window(self: 'MainWindow') -> None:
        window = CreateKeySpaceWindow(self.cassandra_manager, self.refresh_connection_tree_model)
        MainWindow.opened_windows.append(window)
        window.show()

    def delete_key_space(self: 'MainWindow', index: QModelIndex) -> None:
        self.cassandra_manager.delete_key_space(index.data())
        self.close_related_tables(index.data())
        self.refresh_connection_tree_model()

    def delete_table(self: 'MainWindow', index: QModelIndex) -> None:
        self.cassandra_manager.delete_table(index.parent().data(), index.data())
        self.close_related_tables(index.parent().data(), index.data())
        self.refresh_connection_tree_model()

    def set_action_menu(self: 'MainWindow', index_level: int) -> None:
        match index_level:
            case TreeViewDepthLevel.db_name.value:
                self.create_db_name_actions()
            case TreeViewDepthLevel.key_space.value:
                self.create_key_space_actions()
            case TreeViewDepthLevel.table.value:
                self.create_table_actions()

    def create_db_name_actions(self: 'MainWindow') -> None:
            create_key_space_action = QAction("Create Keyspace", self)
            self.menu.addAction(create_key_space_action)
            self.menu.addSeparator()
            refresh_action = QAction("Refresh", self)
            self.menu.addAction(refresh_action)

    def create_key_space_actions(self: 'MainWindow') -> None:
            create_table_action = QAction("Create Table", self)
            delete_key_space_action = QAction("Delete Keyspace", self)
            self.menu.addAction(delete_key_space_action)
            self.menu.addSeparator()
            self.menu.addAction(create_table_action)

    def create_table_actions(self: 'MainWindow') -> None:
            delete_table_action = QAction("Delete Table", self)
            self.menu.addAction(delete_table_action)

    def get_depth(self: 'MainWindow', index: QModelIndex) -> int:
        depth = 0
        parent = index.parent()
        while parent.isValid():
            depth += 1
            parent = parent.parent()
        return depth

    def get_key_space_by_index_level(self: 'MainWindow', index_level: int, index: QModelIndex) -> Union[str, None]:
        match index_level:
            case TreeViewDepthLevel.db_name.value:
                return None
            case TreeViewDepthLevel.key_space.value:
                return index.data()
            case TreeViewDepthLevel.table.value:
                return index.parent().data()