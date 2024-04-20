from typing import Union
from PyQt6.uic import load_ui
from PyQt6.QtWidgets import QFrame
from constants.common import CHANGE_MASTER_PASSWORD_WINDOW_PATH
from constants.utils import pop_up_error
from constants.common import ErrorTitles
from backend.connection_profiles.master_password_manager import MasterPasswordManager
from backend.connection_profiles.connection_window import ConnectionProfilesWindow


class ChangeMasterPasswordWindow(QFrame):
    opened_windows = []

    def __init__(self: 'ChangeMasterPasswordWindow', parent_window: QFrame) -> None:
        super(ChangeMasterPasswordWindow, self).__init__()
        load_ui.loadUi(CHANGE_MASTER_PASSWORD_WINDOW_PATH, self)
        self.master_password_manager = MasterPasswordManager()
        self.__symmetric_key: bytes = None
        self.parent_window = parent_window

        self.submit_change_password_push_button.clicked.connect(self.change_master_password)


    def open_connection_profiles_window(self: 'ChangeMasterPasswordWindow',
                                        is_master_password_changed: bool = False,
                                        symmetric_key: bytes = None) -> None:
        window = ConnectionProfilesWindow(self.master_password_manager, is_master_password_changed, symmetric_key)
        ChangeMasterPasswordWindow.opened_windows.append(window)
        window.show()
        self.close()

    def change_master_password(self: 'ChangeMasterPasswordWindow') -> Union[None, Exception]:
        old_password: str = self.current_password_line_edit.text()
        password1: str = self.new_password_1_line_edit.text()
        password2: str = self.new_password_2_line_edit.text()

        if self.master_password_manager.authenticate(old_password):
            self.__symmetric_key = self.master_password_manager.symmetric_key

        try:
            self.master_password_manager.change_master_password(old_password, password1, password2)
        except Exception as message:
            pop_up_error(ErrorTitles.Error.value, message)
        else:
            if self.master_password_manager.authenticate(password1):
                self.open_connection_profiles_window(is_master_password_changed = True, symmetric_key = self.__symmetric_key)
                self.parent_window.close()