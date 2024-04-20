from PyQt6.uic import load_ui
from PyQt6.QtWidgets import QFrame
from constants.common import CREATE_MASTER_PASSWORD_WINDOW_PATH
from constants.utils import pop_up_error
from constants.common import ErrorTitles
from backend.connection_profiles.master_password_manager import MasterPasswordManager
from backend.connection_profiles.connection_window import ConnectionProfilesWindow


class CreateMasterPasswordWindow(QFrame):
    opened_windows = []

    def __init__(self: 'CreateMasterPasswordWindow') -> None:
        super(CreateMasterPasswordWindow, self).__init__()
        load_ui.loadUi(CREATE_MASTER_PASSWORD_WINDOW_PATH, self)
        self.master_password_manager = MasterPasswordManager()

        self.submit_push_button.clicked.connect(self.create_master_password)
        self.continue_push_button.clicked.connect(self.open_connection_profiles_window)


    def open_connection_profiles_window(self: 'CreateMasterPasswordWindow', is_master_password_changed: bool = False) -> None:
        window = ConnectionProfilesWindow(self.master_password_manager, is_master_password_changed)
        CreateMasterPasswordWindow.opened_windows.append(window)
        window.show()
        self.close()

    def create_master_password(self: 'CreateMasterPasswordWindow') -> None:
        password1: str = self.master_password_1_line_edit.text()
        password2: str = self.master_password_2_line_edit.text()
        try:
            self.master_password_manager.create_master_password(password1, password2)
        except Exception as message:
            pop_up_error(ErrorTitles.Error.value, message)
        else:
            if self.master_password_manager.authenticate(password1):
                self.open_connection_profiles_window(is_master_password_changed = True)