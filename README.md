# Cassandra-Tool
CassTl is a tool for managing and interacting with Cassandra databases. It provides a user-friendly interface for performing various database operations.
Usage
Running the Executable

    For Linux Ubuntu: The executable application can be found in the lin_dist directory. Simply download the entire directory and locate the executable file named CassTl inside it.

    For Windows: Similarly, the executable application can be found in the win_dist directory. Download the entire directory and locate the executable file named CassTl inside it.

# Building from Source

If you make any modifications to the code and want to rebuild the application, you can do so using the following command:

pyinstaller main.spec

Please note that if you modify the code, you may also need to make changes to the main.spec file accordingly.
Installing PyInstaller

If you do not have PyInstaller installed, you can install it using pip:

pip install pyinstaller

PyInstaller is a Python packaging tool that can be used to convert Python applications into standalone executables, making it easier to distribute and run them on different platforms.

# License

This project is licensed under multiple licenses:

    Apache License, Version 2.0: Used for cassandra-driver, python-dateutil, sortedcontainers and cryptography.
    GNU General Public License v3.0: Used for PyQt6.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

You should have received a copy of:
    Apache License along with this program in LICENSE. If not, see <http://www.apache.org/licenses/LICENSE-2.0>
    GNU General Public License along with this program in COPYING and COPYING.LESSER. If not, see <https://www.gnu.org/licenses/>.

Copyright 2024 Tomas Franek