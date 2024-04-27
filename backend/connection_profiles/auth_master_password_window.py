from PyQt6.uic import load_ui
from PyQt6.QtWidgets import QFrame
from constants.common import AUTH_MASTER_PASSWORD_WINDOW_PATH
from backend.connection_profiles.master_password_manager import MasterPasswordManager
from backend.connection_profiles.connection_window import ConnectionProfilesWindow
from backend.connection_profiles.change_master_password_window import ChangeMasterPasswordWindow


class AuthMasterPasswordWindow(QFrame):
    opened_windows = []

    def __init__(self: 'AuthMasterPasswordWindow') -> None:
        super(AuthMasterPasswordWindow, self).__init__()
        load_ui.loadUi(AUTH_MASTER_PASSWORD_WINDOW_PATH, self)
        self.master_password_manager = MasterPasswordManager()

        self.submit_push_button.clicked.connect(self.authenticate)
        self.change_password_push_button.clicked.connect(self.open_change_master_password_window)


    def open_connection_profiles_window(self: 'AuthMasterPasswordWindow') -> None:
        window = ConnectionProfilesWindow(self.master_password_manager)
        AuthMasterPasswordWindow.opened_windows.append(window)
        window.show()
        self.close()

    def authenticate(self: 'AuthMasterPasswordWindow') -> None:
        password: str = self.master_password_line_edit.text()
        if self.master_password_manager.authenticate(password):
            self.open_connection_profiles_window()

    def open_change_master_password_window(self: 'AuthMasterPasswordWindow') -> None:
        window = ChangeMasterPasswordWindow(self)
        AuthMasterPasswordWindow.opened_windows.append(window)
        window.show()