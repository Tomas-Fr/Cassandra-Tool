from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import Qt
from PyQt6 import uic
from constants.common import (ErrorTitles,
                              ConfirmationMessages,
                              CONNECTION_WINDOW_UI_PATH,
                              CONNECTION_PROFILES_TABLE)
from constants.model_wrapper import ModelWrapper
from constants.utils import pop_up_error, pop_up_confirmation_dialog
from backend.connection_profiles.connection_profiles_database import ConnectionProfilesDatabase, PASSWORD_COLUMN_INDEX
from backend.connection_profiles.custom_q_sql_table_model import CustomQSqlTableModel, PasswordDelegate
from backend.custom_filter_proxy_model import CustomFilterProxyModel
from backend.main_window.main_window import MainWindow
from constants.connection_model import Connection
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from backend.connection_profiles.master_password_manager import MasterPasswordManager
from constants.connection_profile_model import ConnectionProfileModel


class ConnectionProfilesWindow(QMainWindow):
    opened_windows = []

    def __init__(self: 'ConnectionProfilesWindow',
                 master_password_manager: MasterPasswordManager,
                 is_master_password_changed: bool = False,
                 symmetric_key: bytes = None) -> None:
        super(ConnectionProfilesWindow, self).__init__()
        uic.loadUi(CONNECTION_WINDOW_UI_PATH, self)
        self.conn_prof_db = ConnectionProfilesDatabase()
        self.connections = []
        self.main_window = None
        self.master_password_manager = master_password_manager
        self.is_master_password_changed = is_master_password_changed
        self.__symmetric_key = symmetric_key
        self.set_up_model()
        self.set_up_view()
        self.set_up_search()

        self.process_master_password_changed()

        self.create_new_connection_button.clicked.connect(self.create_new_connection_profile)
        self.delete_button.clicked.connect(
            lambda: pop_up_confirmation_dialog(
                self,
                ConfirmationMessages.DELETE.value,
                self.delete_connection_profiles
            )
        )
        self.connect_button.clicked.connect(self.connect_to_cassandra)

        self.connection_profiles_table_view.setItemDelegateForColumn(PASSWORD_COLUMN_INDEX, PasswordDelegate())


    def set_up_model(self: 'ConnectionProfilesWindow') -> None:
        self.model = CustomQSqlTableModel(self, master_password_manager=self.master_password_manager, conn_prof_db=self.conn_prof_db)
        self.model.setTable(CONNECTION_PROFILES_TABLE)

    def set_up_view(self: 'ConnectionProfilesWindow') -> None:
        self.model.select()
        self.connection_profiles_table_view.setModel(self.model)
        self.connection_profiles_table_view.resizeColumnsToContents()

    def set_up_search(self: 'ConnectionProfilesWindow') -> None:
        self.proxy_model = CustomFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.connection_profiles_table_view.setModel(self.proxy_model)
        self.find_line.textChanged.connect(self.proxy_model.setFilterRegularExpression)

    def delete_connection_profiles(self: 'ConnectionProfilesWindow') -> None:
        selected_indexes = self.connection_profiles_table_view.selectionModel().selectedIndexes()
        unique_rows = set(index.row() for index in selected_indexes)

        for row in sorted(unique_rows, reverse=True):
            self.model.removeRow(row)

        if not self.model.submitAll():
            pop_up_error(ErrorTitles.Connection_profiles.value, self.model.lastError().databaseText())
        self.model.select()
        self.connection_profiles_table_view.setModel(self.model)

    def create_new_connection_profile(self: 'ConnectionProfilesWindow') -> None:
        row = self.model.rowCount()
        self.model.insertRow(row)

        model = ConnectionProfileModel(
            self.conn_prof_name_line.text(),
            self.host_line.text(),
            self.port_line.text(),
            self.username_line.text(),
            self.password_line.text()
        )

        if self.master_password_manager.is_master_password_created():
            model.password = self.master_password_manager.encrypt_aes_256(model.password)
        else:
            model.password = model.password.encode('utf-8')

        if message := self.conn_prof_db.save_connection_profile(model):
            pop_up_error(ErrorTitles.Connection_profiles.value, message)

        self.model.setData(self.model.index(row, 0), model.connection_name)
        self.model.setData(self.model.index(row, 1), model.host)
        self.model.setData(self.model.index(row, 2), model.port)
        self.model.setData(self.model.index(row, 3), model.username)
        self.model.setData(self.model.index(row, 4), model.password)

        self.model.select()
        self.connection_profiles_table_view.setModel(self.model)

    def connect_to_cassandra(self: 'ConnectionProfilesWindow') -> None:
        connection_profiles = self.get_selected_rows()
        for connection_profile in connection_profiles:
            cluster = None
            auth_provider = PlainTextAuthProvider(username=connection_profile.username, password=connection_profile.password)
            try:
                cluster = Cluster(
                    contact_points=[connection_profile.host],
                    port=connection_profile.port,
                    auth_provider=auth_provider
                )
                cluster.connect()
            except Exception as message:
                pop_up_error(ErrorTitles.Connection_profiles.value, message)
            else:
                if cluster:
                    if not connection_profile.connection_name in [i.connection_profile_name for i in self.connections]:
                        self.connections.append(Connection(cluster, connection_profile.connection_name))
                    self.open_main_window()

    def get_selected_rows(self: 'ConnectionProfilesWindow') -> list:
        selected_indexes = self.connection_profiles_table_view.selectionModel().selectedRows()
        row_models = []
        for index in selected_indexes:
            row_model = ModelWrapper()
            for column in range(self.model.columnCount()):

                key = self.model.headerData(column, Qt.Orientation.Horizontal)
                value = self.model.index(index.row(), column).data()

                if column == PASSWORD_COLUMN_INDEX:
                    value = self.conn_prof_db.get_password(index.data())
                    if self.master_password_manager.is_master_password_created():
                        value = self.master_password_manager.decrypt_aes_256(value)
                    else:
                        value = value.decode('utf-8')

                setattr(row_model, key, value)
            row_models.append(row_model)
        return row_models

    def open_main_window(self: 'ConnectionProfilesWindow') -> None:
        if not self.main_window or self.main_window.is_open is False:
            self.main_window = MainWindow(self.connections)
            ConnectionProfilesWindow.opened_windows.append(self.main_window)
            self.main_window.show()
        else:
            self.main_window.refresh_connection_tree_model()

    def process_master_password_changed(self) -> None:
        if not self.is_master_password_changed:
            return None
        rows = self.conn_prof_db.get_password_to_change()
        if not rows:
            return None
        for row in rows:
            password_str: str = None
            if self.__symmetric_key:
                password_str = self.master_password_manager.decrypt_aes_256(row[1], self.__symmetric_key)
            else:
                password_str = row[1].decode('utf-8')
            password_encrypted = self.master_password_manager.encrypt_aes_256(password_str)
            self.conn_prof_db.update_password(row[0], password_encrypted)