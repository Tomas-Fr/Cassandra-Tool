from backend.connection_profiles.create_master_password_window import CreateMasterPasswordWindow
from backend.connection_profiles.auth_master_password_window import AuthMasterPasswordWindow
from backend.connection_profiles.master_password_manager import MasterPasswordManager


class AuthenticationWindow:
    opened_windows = []

    def authenticate(self: 'AuthenticationWindow') -> None:
        self.master_password_manager = MasterPasswordManager()
        if not self.master_password_manager.is_master_password_created():
            self.open_create_master_password_window()
        else:
            self.open_auth_master_password_window()

    def open_create_master_password_window(self: 'AuthenticationWindow') -> None:
        window = CreateMasterPasswordWindow()
        AuthenticationWindow.opened_windows.append(window)
        window.show()

    def open_auth_master_password_window(self: 'AuthenticationWindow') -> None:
        window = AuthMasterPasswordWindow()
        AuthenticationWindow.opened_windows.append(window)
        window.show()