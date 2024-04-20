import os
import sqlite3
import sys
from typing import Tuple, Union
from PyQt6.QtSql import QSqlDatabase, QSqlQuery
from PyQt6.QtWidgets import QMessageBox
from constants.common import ErrorTitles, CONNECTION_PROFILES_DATABASE_PATH, CONNECTION_PROFILES_TABLE
from constants.connection_profile_model import ConnectionProfileModel


PASSWORD_COLUMN_INDEX = 4

class ConnectionProfilesDatabase:
    __instance = None

    def __new__(cls: 'ConnectionProfilesDatabase') -> 'ConnectionProfilesDatabase':
        if cls.__instance is None:
            cls.__instance = super(ConnectionProfilesDatabase, cls).__new__(cls)
            cls.__instance.__create_connection()
            cls.__instance.__create_connection_profiles_table()
        return cls.__instance


    # Private
    def __create_connection(self: 'ConnectionProfilesDatabase') -> None:
        self.connection = QSqlDatabase.addDatabase("QSQLITE")
        self.connection.setDatabaseName(CONNECTION_PROFILES_DATABASE_PATH)

    def __create_connection_profiles_table(self: 'ConnectionProfilesDatabase') -> None:
        if not os.path.exists(CONNECTION_PROFILES_DATABASE_PATH):
            self.connect()
            query = QSqlQuery()
            query.exec(
                f"""
                CREATE TABLE IF NOT EXISTS {CONNECTION_PROFILES_TABLE} (
                    connection_name VARCHAR(150) PRIMARY KEY UNIQUE NOT NULL,
                    host VARCHAR(150) NOT NULL,
                    port INTEGER NOT NULL,
                    username VARCHAR(150) NOT NULL,
                    password BLOB NOT NULL
                );
                """
            )
            query.finish()
            self.disconnect()

    # Public
    def connect(self: 'ConnectionProfilesDatabase') -> None:
        if not self.connection.open():
            QMessageBox.critical(
                None,
                ErrorTitles.Db_Connection_profiles.value,
                f"{ErrorTitles.Error.value}: {self.connection.lastError().databaseText()}",
            )
            sys.exit(1)

    def disconnect(self: 'ConnectionProfilesDatabase') -> None:
        self.connection.close()

    def save_connection_profile(self: 'ConnectionProfilesDatabase', model: ConnectionProfileModel) -> Union[str, None]:
        connection = sqlite3.connect(CONNECTION_PROFILES_DATABASE_PATH)
        cursor = connection.cursor()

        query = f"""
             INSERT INTO {CONNECTION_PROFILES_TABLE} (connection_name, host, port, username, password)
             VALUES (?, ?, ?, ?, ?)
         """
        values = (model.connection_name, model.host, model.port, model.username, model.password)

        try:
            cursor.execute(query, values)
            connection.commit()
        except Exception as message:
            return str(message)
        finally:
            connection.close()

    def get_password(self: 'ConnectionProfilesDatabase', connection_name: str) -> Union[bytes, None]:
        connection = sqlite3.connect(CONNECTION_PROFILES_DATABASE_PATH)
        cursor = connection.cursor()

        query = f"""
            SELECT password
            FROM {CONNECTION_PROFILES_TABLE}
            WHERE connection_name = ?;
        """

        try:
            cursor.execute(query, (connection_name, ))
        except Exception:
            return None

        row = cursor.fetchone()
        if row:
            connection.close()
            return row[0]

    def get_password_to_change(self: 'ConnectionProfilesDatabase') -> Union[Tuple[str, bytes], None]:
        connection = sqlite3.connect(CONNECTION_PROFILES_DATABASE_PATH)
        cursor = connection.cursor()

        query = f"""
            SELECT connection_name, password
            FROM {CONNECTION_PROFILES_TABLE};
        """

        try:
            cursor.execute(query)
        except Exception:
            return None

        return cursor.fetchall()

    def update_password(self: 'ConnectionProfilesDatabase', connection_name: str, new_password: bytes) -> None:
        connection = sqlite3.connect(CONNECTION_PROFILES_DATABASE_PATH)
        cursor = connection.cursor()

        query = f"""
            UPDATE {CONNECTION_PROFILES_TABLE}
            SET password = ?
            WHERE connection_name = ?;
         """
        values = (new_password, connection_name)

        try:
            cursor.execute(query, values)
            connection.commit()
        except Exception as message:
            return str(message)
        finally:
            connection.close()