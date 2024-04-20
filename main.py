import sys
from PyQt6.QtWidgets import QApplication
from backend.connection_profiles.authentication_window import AuthenticationWindow


def main() -> None:
    app = QApplication(sys.argv)
    authentication_window = AuthenticationWindow()
    authentication_window.authenticate()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()