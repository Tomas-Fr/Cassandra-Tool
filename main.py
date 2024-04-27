import os
import sys
from PyQt6 import QtGui
from PyQt6.QtWidgets import QApplication
from backend.connection_profiles.authentication_window import AuthenticationWindow

basedir = os.path.dirname(__file__)


def main() -> None:
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(os.path.join(basedir, 'casstl.ico')))
    authentication_window = AuthenticationWindow()
    authentication_window.authenticate()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()